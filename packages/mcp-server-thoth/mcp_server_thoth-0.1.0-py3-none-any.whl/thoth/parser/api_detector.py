"""Detect API endpoints in code."""

import ast
import re
from typing import Dict, List, Optional, Tuple

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..storage.models import Repository, File, Symbol


class APIEndpoint:
    """Represents an API endpoint."""
    def __init__(self, method: str, path: str, handler: str, file: str, line: int):
        self.method = method
        self.path = path
        self.handler = handler
        self.file = file
        self.line = line


class APIDetector:
    """Detects API endpoints in Python web frameworks."""
    
    # FastAPI patterns
    FASTAPI_DECORATORS = {'get', 'post', 'put', 'delete', 'patch', 'options', 'head'}
    
    # Flask patterns
    FLASK_DECORATORS = {'route'}
    
    def __init__(self):
        self.endpoints: List[APIEndpoint] = []
    
    async def detect_endpoints_in_file(self, session: AsyncSession, file_id: int) -> List[APIEndpoint]:
        """Detect API endpoints in a file."""
        # Get file
        result = await session.execute(
            select(File).where(File.id == file_id)
        )
        file = result.scalar_one()
        
        try:
            with open(file.path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content, filename=file.path)
            visitor = APIVisitor(file.path)
            visitor.visit(tree)
            
            return visitor.endpoints
            
        except Exception:
            return []


class APIVisitor(ast.NodeVisitor):
    """AST visitor to detect API endpoints."""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.endpoints: List[APIEndpoint] = []
        self.current_class: Optional[str] = None
        
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Check function decorators for API endpoints."""
        self._check_decorators(node)
        self.generic_visit(node)
    
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Check async function decorators for API endpoints."""
        self._check_decorators(node)
        self.generic_visit(node)
    
    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Track class context."""
        old_class = self.current_class
        self.current_class = node.name
        self.generic_visit(node)
        self.current_class = old_class
    
    def _check_decorators(self, node: ast.FunctionDef) -> None:
        """Check if function has API endpoint decorators."""
        for decorator in node.decorator_list:
            endpoint = self._parse_decorator(decorator, node)
            if endpoint:
                self.endpoints.append(endpoint)
    
    def _parse_decorator(self, decorator: ast.AST, func_node: ast.FunctionDef) -> Optional[APIEndpoint]:
        """Parse decorator to extract endpoint info."""
        method = None
        path = None
        
        # FastAPI style: @app.get("/path")
        if isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Attribute):
            attr_name = decorator.func.attr
            
            if attr_name in {'get', 'post', 'put', 'delete', 'patch', 'options', 'head'}:
                method = attr_name.upper()
                
                # Get path from first argument
                if decorator.args and isinstance(decorator.args[0], ast.Constant):
                    path = decorator.args[0].value
                elif decorator.args and isinstance(decorator.args[0], ast.Str):
                    path = decorator.args[0].s
        
        # Flask style: @app.route("/path", methods=["GET"])
        elif isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Attribute):
            if decorator.func.attr == 'route':
                # Get path
                if decorator.args and isinstance(decorator.args[0], ast.Constant):
                    path = decorator.args[0].value
                elif decorator.args and isinstance(decorator.args[0], ast.Str):
                    path = decorator.args[0].s
                
                # Get methods from keywords
                method = 'GET'  # Default
                for keyword in decorator.keywords:
                    if keyword.arg == 'methods' and isinstance(keyword.value, ast.List):
                        methods = []
                        for elt in keyword.value.elts:
                            if isinstance(elt, ast.Constant):
                                methods.append(elt.value)
                            elif isinstance(elt, ast.Str):
                                methods.append(elt.s)
                        if methods:
                            method = methods[0]  # Take first method
        
        # WebSocket endpoints
        elif isinstance(decorator, ast.Attribute) and decorator.attr == 'websocket':
            method = 'WEBSOCKET'
            path = f"/{func_node.name}"  # Use function name as path
        
        if method and path:
            handler = func_node.name
            if self.current_class:
                handler = f"{self.current_class}.{handler}"
            
            return APIEndpoint(
                method=method,
                path=path,
                handler=handler,
                file=self.file_path,
                line=func_node.lineno
            )
        
        return None


async def detect_api_endpoints_in_repository(session: AsyncSession, repo_id: int) -> Dict[str, List[APIEndpoint]]:
    """Detect all API endpoints in a repository."""
    # Get all Python files
    result = await session.execute(
        select(File).where(File.repository_id == repo_id)
    )
    files = result.scalars().all()
    
    detector = APIDetector()
    all_endpoints = {}
    
    for file in files:
        endpoints = await detector.detect_endpoints_in_file(session, file.id)
        if endpoints:
            all_endpoints[file.path] = endpoints
    
    return all_endpoints