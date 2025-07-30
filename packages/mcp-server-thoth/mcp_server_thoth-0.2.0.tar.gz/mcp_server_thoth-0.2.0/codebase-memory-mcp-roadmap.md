# Codebase Memory MCP Server - Comprehensive Roadmap

## Vision
Build a deterministic, user-level MCP server that provides persistent codebase understanding across multiple related repositories, with real-time visualization capabilities and deep integration with AI assistants like Claude.

## Problem Statement
AI assistants currently lack persistent memory of codebases between conversations, leading to:
- Repetitive grepping and searching for the same information
- Lost context about system architecture and design patterns
- Inability to understand cross-repository relationships
- No visualization of code structure and dependencies
- Inefficient debugging due to lack of call graph understanding

## Core Requirements

### 1. Multi-Repository Support
- User-level configuration supporting multiple related repositories
- Cross-repository dependency tracking
- Unified indexing and querying across repo boundaries
- Understanding of API contracts between repos (e.g., slush-client ↔ slush)

### 2. Deterministic Analysis
- AST-based parsing (no LLM calls)
- Reproducible results
- Incremental updates based on file changes
- Version control aware

### 3. Visualization Capabilities
- Mermaid diagram generation for:
  - System architecture
  - Class diagrams
  - Call flow diagrams
  - Data flow diagrams
  - Module dependencies
- Dashboard with interactive graph visualization
- Real-time or manual updates via git hooks

### 4. Deep Code Understanding
- Function/class/method indexing
- Import tracking and resolution
- Call graph analysis
- Type information extraction
- Documentation linking
- Library identification with automatic docs linking

### 5. MCP Integration
- Standard MCP server implementation
- Tools for querying code structure
- Resources for accessing visualizations
- Prompts for common analysis patterns
- Integration with Claude Code hooks

### 6. Optional Features
- VSCode extension
- Web dashboard
- Real-time file watching
- Complexity metrics
- Code smell detection

## Technical Architecture

### Storage Layer
```
~/.config/codebase-memory/
├── config.yaml              # Repository configurations
├── index.db                # SQLite database for cross-repo queries
├── cache/
│   ├── ast/                # Cached AST representations
│   └── diagrams/           # Generated Mermaid diagrams
└── logs/                   # Operation logs
```

### Database Schema (SQLite)
```sql
-- Core tables
symbols (id, name, type, repo, file, line, column, parent_id, docstring)
imports (id, repo, file, import_stmt, resolved_repo, resolved_file)
calls (id, caller_symbol_id, callee_symbol_id, line, column)
files (id, repo, path, last_modified, hash)

-- Visualization cache
diagrams (id, type, repo_scope, content, generated_at)

-- Cross-repo relationships
repo_dependencies (from_repo, to_repo, dependency_type)
api_endpoints (id, repo, method, path, handler_symbol_id)
```

### MCP Server API

#### Tools
1. **find_definition**
   - Input: symbol_name, repos[]
   - Output: [{repo, file, line, type}]

2. **get_callers**
   - Input: symbol_name, repos[]
   - Output: [{repo, file, line, calling_function}]

3. **trace_call_path**
   - Input: from_symbol, to_symbol
   - Output: [call_chain]

4. **get_file_structure**
   - Input: file_path
   - Output: {functions[], classes[], imports[]}

5. **search_symbols**
   - Input: query, type_filter, repos[]
   - Output: [matching_symbols]

6. **generate_diagram**
   - Input: diagram_type, scope, format
   - Output: mermaid_text or diagram_url

7. **analyze_dependencies**
   - Input: repo_name
   - Output: {internal_deps, external_deps, circular_deps}

8. **trace_api_flow**
   - Input: endpoint_or_message
   - Output: {client_code, server_handler, data_flow}

#### Resources
1. **/repos** - List of indexed repositories
2. **/symbols/{repo}** - Symbol index for a repository
3. **/diagrams/{type}** - Generated diagrams
4. **/metrics/{repo}** - Code metrics and statistics

#### Prompts
1. **debug_issue** - Structured debugging workflow
2. **understand_architecture** - System comprehension guide
3. **trace_data_flow** - Data flow analysis template

## Implementation Roadmap

### Phase 1: MVP (Week 1) ✅ COMPLETED (v0.1.0 on PyPI)
**Goal**: Basic Python parsing and symbol indexing for single repo

- [x] Set up project structure with `uv`
- [x] Implement Python AST parser using `ast` module
- [x] Create SQLite schema and basic models
- [x] Build simple file indexer
- [x] Implement core MCP tools (find_definition, get_file_structure)
- [x] Basic Mermaid module dependency diagram
- [x] Manual indexing script

**Deliverables**:
- Working MCP server for single Python repository
- Basic symbol search and definition lookup
- Simple module dependency visualization

### Phase 1.5: Semantic Search (v0.2.0) 🚧 IN PROGRESS
**Goal**: Add lightweight semantic search capabilities without heavy dependencies

- [ ] Add vLLM integration for embeddings
- [ ] Implement Qwen3-Embedding-0.6B model support
- [ ] Integrate ChromaDB for vector storage
- [ ] Keep TF-IDF as fallback search method
- [ ] Add semantic_search MCP tool
- [ ] Create embedding provider interface
- [ ] Implement unified backend.py
- [ ] Create separate thoth-dashboard package

**Deliverables**:
- Local-only semantic search using vLLM
- ChromaDB vector storage integration
- New semantic_search MCP tool
- Dashboard as separate installable package
- Maintained lightweight core with optional features

### Phase 2: Multi-Repository Support (Week 2) ✅ PARTIALLY COMPLETED
**Goal**: Cross-repository understanding

- [x] Implement user-level config system
- [x] Extend parser for import resolution across repos
- [x] Add cross-repo relationship tracking
- [x] Implement API endpoint detection
- [x] Build trace_api_flow tool
- [x] System architecture diagram generation

**Deliverables**:
- Multi-repo configuration support
- Cross-repo import and call tracking
- System-level architecture visualization

### Phase 3: Enhanced Parsing (Week 3)
**Goal**: Deeper code understanding

- [ ] Migrate to tree-sitter for better parsing
- [ ] Add call graph analysis
- [ ] Extract type information
- [ ] Parse docstrings and comments
- [ ] Implement incremental parsing
- [ ] Add support for JavaScript/TypeScript

**Deliverables**:
- Complete call graph analysis
- Type information extraction
- Multi-language support

### Phase 4: Advanced Visualizations (Week 4)
**Goal**: Rich diagram generation

- [ ] Class diagram generation
- [ ] Sequence diagram for call flows
- [ ] Data flow diagrams
- [ ] Interactive web dashboard
- [ ] Real-time diagram updates
- [ ] Diagram caching and optimization

**Deliverables**:
- Complete Mermaid diagram suite
- Web-based visualization dashboard

### Phase 5: Integration & Intelligence (Week 5)
**Goal**: Deep IDE and AI integration

- [ ] VSCode extension development
- [ ] Git hooks for automatic updates
- [ ] Claude Code hook integration
- [ ] Documentation linking system
- [ ] Library detection and docs integration
- [ ] Performance optimizations

**Deliverables**:
- VSCode extension
- Automated update system
- AI assistant integration

### Phase 6: Polish & Extended Features (Week 6)
**Goal**: Production readiness

- [ ] Comprehensive testing
- [ ] Performance benchmarking
- [ ] Configuration UI
- [ ] Export capabilities
- [ ] Metrics and analytics
- [ ] Documentation

**Deliverables**:
- Production-ready system
- Complete documentation
- Performance benchmarks

## Technology Stack

### Core
- **Language**: Python 3.10+
- **Package Manager**: uv
- **MCP Framework**: FastMCP or official Python SDK
- **Database**: SQLite with FTS5 for search

### Parsing
- **Phase 1**: Python `ast` module ✅
- **Phase 3+**: tree-sitter with language bindings

### Search & Embeddings (v0.2.0)
- **Embeddings**: vLLM with Qwen3-Embedding-0.6B
- **Vector Store**: ChromaDB (lightweight mode)
- **Fallback**: TF-IDF with scikit-learn
- **Cache**: Redis (optional)

### Visualization
- **Diagrams**: Mermaid.js ✅
- **Dashboard**: Gradio (separate package)
- **Graphing**: Plotly (in dashboard package)

### Integration
- **File Watching**: watchdog
- **Git Hooks**: pre-commit framework
- **VSCode**: Extension API with Language Server Protocol

## Success Metrics

1. **Performance**
   - Index 10K files in < 30 seconds
   - Symbol lookup in < 10ms
   - Diagram generation in < 1 second

2. **Coverage**
   - 95%+ symbol detection accuracy
   - Support for Python, JavaScript, TypeScript
   - Handle repos with 100K+ lines of code

3. **Usability**
   - Reduce Claude's grepping by 80%
   - Enable cross-repo debugging workflows
   - Provide instant architecture understanding

## Risks & Mitigations

1. **Performance at Scale**
   - Risk: Slow indexing for large codebases
   - Mitigation: Incremental updates, parallel processing

2. **Parser Limitations**
   - Risk: Incomplete understanding of dynamic code
   - Mitigation: Focus on static analysis, document limitations

3. **Cross-Repo Complexity**
   - Risk: Incorrect dependency resolution
   - Mitigation: Explicit configuration, validation tools

## Open Questions

1. Should we support remote repositories (GitHub URLs)?
2. How to handle private/proprietary code security?
3. Integration with other AI assistants beyond Claude?
4. Support for compiled languages (Go, Rust)?
5. Real-time collaboration features?

## Next Steps

1. Review and refine this roadmap
2. Set up development environment
3. Create GitHub repository
4. Implement Phase 1 MVP
5. Gather feedback and iterate

---

This roadmap represents a comprehensive plan to build a codebase intelligence system that will fundamentally improve how AI assistants understand and work with code. The phased approach allows for early value delivery while building toward a fully-featured system.