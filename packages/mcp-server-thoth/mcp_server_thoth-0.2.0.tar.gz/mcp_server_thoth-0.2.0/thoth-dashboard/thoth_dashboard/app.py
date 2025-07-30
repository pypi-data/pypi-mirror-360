"""Main Gradio application for Thoth Dashboard."""

import os
import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging

import gradio as gr
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

from thoth.storage.database import Database
from thoth.storage.backend import ThothStorage
from thoth.storage.models import Repository, Symbol, File

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ThothDashboard:
    """Interactive dashboard for Thoth codebase memory."""
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize dashboard.
        
        Args:
            db_path: Path to Thoth database (default: ~/.thoth/index.db)
        """
        self.db_path = db_path or os.getenv("THOTH_DB_PATH", "~/.thoth/index.db")
        self.db_path = Path(self.db_path).expanduser()
        
        # Initialize async components
        self.db: Optional[Database] = None
        self.storage: Optional[ThothStorage] = None
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        
        # Initialize in async context
        self._loop.run_until_complete(self._init_async())
    
    async def _init_async(self):
        """Initialize async components."""
        self.db = Database(str(self.db_path))
        await self.db.init_db()
        
        self.storage = ThothStorage(str(self.db_path))
        await self.storage.initialize()
    
    def _run_async(self, coro):
        """Run async function in sync context."""
        return self._loop.run_until_complete(coro)
    
    def get_overview_stats(self) -> Dict[str, Any]:
        """Get overview statistics."""
        stats = self._run_async(self.storage.get_stats())
        return stats
    
    def search_symbols(
        self,
        query: str,
        repo: Optional[str] = None,
        symbol_type: Optional[str] = None,
        limit: int = 20
    ) -> pd.DataFrame:
        """Search for symbols."""
        if not query:
            return pd.DataFrame()
        
        results = self._run_async(
            self.storage.search_semantic(
                query=query,
                repo=repo if repo != "All" else None,
                symbol_type=symbol_type if symbol_type != "All" else None,
                limit=limit
            )
        )
        
        # Convert to DataFrame
        if results:
            df = pd.DataFrame(results)
            df['score'] = df['score'].round(3)
            return df[['name', 'type', 'repo', 'file_path', 'line', 'score']]
        
        return pd.DataFrame()
    
    def create_repository_graph(self) -> go.Figure:
        """Create repository dependency graph."""
        # Get graph data
        nodes = []
        edges = []
        
        # Get unique repositories
        repos = set()
        for node, data in self.storage.graph.nodes(data=True):
            if 'repo' in data:
                repos.add(data['repo'])
        
        # Create nodes for each repo
        for i, repo in enumerate(repos):
            nodes.append({
                'id': repo,
                'label': repo,
                'x': i * 100,
                'y': 0
            })
        
        # Count cross-repo dependencies
        cross_deps = {}
        for edge in self.storage.graph.edges(data=True):
            source_data = self.storage.graph.nodes.get(edge[0], {})
            target_data = self.storage.graph.nodes.get(edge[1], {})
            
            source_repo = source_data.get('repo', '')
            target_repo = target_data.get('repo', '')
            
            if source_repo and target_repo and source_repo != target_repo:
                key = (source_repo, target_repo)
                cross_deps[key] = cross_deps.get(key, 0) + 1
        
        # Create edges
        for (source, target), count in cross_deps.items():
            edges.append({
                'source': source,
                'target': target,
                'weight': count
            })
        
        # Create Plotly figure
        fig = go.Figure()
        
        # Add nodes
        for node in nodes:
            fig.add_trace(go.Scatter(
                x=[node['x']],
                y=[node['y']],
                mode='markers+text',
                text=[node['label']],
                textposition='top center',
                marker=dict(size=30, color='lightblue'),
                showlegend=False
            ))
        
        # Add edges
        for edge in edges:
            source_node = next(n for n in nodes if n['id'] == edge['source'])
            target_node = next(n for n in nodes if n['id'] == edge['target'])
            
            fig.add_trace(go.Scatter(
                x=[source_node['x'], target_node['x']],
                y=[source_node['y'], target_node['y']],
                mode='lines',
                line=dict(width=edge['weight'] / 10),
                showlegend=False
            ))
        
        fig.update_layout(
            title="Repository Dependencies",
            showlegend=False,
            hovermode='closest',
            xaxis=dict(showgrid=False, showticklabels=False),
            yaxis=dict(showgrid=False, showticklabels=False)
        )
        
        return fig
    
    def create_symbol_distribution(self) -> go.Figure:
        """Create symbol type distribution chart."""
        # Count symbols by type
        symbol_counts = {'function': 0, 'class': 0, 'method': 0}
        
        for node, data in self.storage.graph.nodes(data=True):
            if node.startswith('symbol_') and 'type' in data:
                symbol_type = data['type']
                if symbol_type in symbol_counts:
                    symbol_counts[symbol_type] += 1
        
        # Create pie chart
        fig = px.pie(
            values=list(symbol_counts.values()),
            names=list(symbol_counts.keys()),
            title="Symbol Type Distribution"
        )
        
        return fig
    
    def build_interface(self) -> gr.Blocks:
        """Build Gradio interface."""
        with gr.Blocks(title="Thoth Dashboard") as interface:
            gr.Markdown("# 🧠 Thoth Dashboard")
            gr.Markdown("Interactive visualization for codebase memory")
            
            with gr.Tab("Overview"):
                with gr.Row():
                    stats_json = gr.JSON(label="System Statistics")
                    refresh_btn = gr.Button("Refresh Stats")
                
                with gr.Row():
                    repo_graph = gr.Plot(label="Repository Dependencies")
                    symbol_dist = gr.Plot(label="Symbol Distribution")
                
                # Event handlers
                def refresh_overview():
                    stats = self.get_overview_stats()
                    graph = self.create_repository_graph()
                    dist = self.create_symbol_distribution()
                    return stats, graph, dist
                
                refresh_btn.click(
                    refresh_overview,
                    outputs=[stats_json, repo_graph, symbol_dist]
                )
                
                # Load on startup
                interface.load(
                    refresh_overview,
                    outputs=[stats_json, repo_graph, symbol_dist]
                )
            
            with gr.Tab("Symbol Search"):
                with gr.Row():
                    search_query = gr.Textbox(
                        label="Search Query",
                        placeholder="Enter natural language query..."
                    )
                    search_repo = gr.Dropdown(
                        label="Repository Filter",
                        choices=["All"] + self.get_overview_stats().get("repositories", []),
                        value="All"
                    )
                    search_type = gr.Dropdown(
                        label="Symbol Type",
                        choices=["All", "function", "class", "method"],
                        value="All"
                    )
                
                search_btn = gr.Button("Search", variant="primary")
                
                results_table = gr.DataFrame(
                    label="Search Results",
                    interactive=False
                )
                
                # Search handler
                search_btn.click(
                    self.search_symbols,
                    inputs=[search_query, search_repo, search_type],
                    outputs=results_table
                )
            
            with gr.Tab("Graph Explorer"):
                gr.Markdown("### Interactive Code Graph")
                gr.Markdown("Coming soon: Interactive graph exploration with zoom, pan, and node details.")
            
            with gr.Tab("API"):
                gr.Markdown("""
                ### API Endpoints
                
                The dashboard exposes a REST API for programmatic access:
                
                - `GET /api/stats` - Get system statistics
                - `POST /api/search` - Search for symbols
                - `GET /api/symbol/{id}` - Get symbol details
                - `GET /api/graph` - Get graph data
                
                See documentation for details.
                """)
        
        return interface
    
    def cleanup(self):
        """Cleanup resources."""
        if self.storage:
            self._run_async(self.storage.close())
        if self._loop:
            self._loop.close()


def main():
    """Main entry point."""
    host = os.getenv("THOTH_DASHBOARD_HOST", "127.0.0.1")
    port = int(os.getenv("THOTH_DASHBOARD_PORT", "7860"))
    
    try:
        dashboard = ThothDashboard()
        interface = dashboard.build_interface()
        
        logger.info(f"Starting Thoth Dashboard on http://{host}:{port}")
        interface.launch(
            server_name=host,
            server_port=port,
            share=False
        )
    except KeyboardInterrupt:
        logger.info("Shutting down dashboard...")
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        raise
    finally:
        if 'dashboard' in locals():
            dashboard.cleanup()


if __name__ == "__main__":
    main()