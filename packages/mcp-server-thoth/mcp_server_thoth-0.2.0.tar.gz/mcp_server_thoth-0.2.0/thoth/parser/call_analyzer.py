"""Analyze and resolve function calls in code."""

import ast
from typing import Dict, List, Optional, Set, Tuple

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..storage.models import Call, File, Repository, Symbol


class CallAnalyzer:
    """Analyzes function calls and resolves them to symbols."""
    
    def __init__(self):
        self.current_file: Optional[str] = None
        self.current_function: Optional[str] = None
        self.current_class: Optional[str] = None
        self.imports: Dict[str, str] = {}  # alias -> module
        self.symbols: Dict[str, int] = {}  # name -> symbol_id
    
    async def analyze_file_calls(self, session: AsyncSession, file_id: int) -> None:
        """Analyze all calls in a file and resolve them to symbols."""
        # Get file
        result = await session.execute(
            select(File).where(File.id == file_id)
        )
        file = result.scalar_one()
        
        # Get all symbols in this file
        result = await session.execute(
            select(Symbol).where(Symbol.file_id == file_id)
        )
        file_symbols = result.scalars().all()
        
        # Build symbol lookup
        for sym in file_symbols:
            self.symbols[sym.name] = sym.id
            if sym.parent:
                # Also track class.method format
                parent_result = await session.execute(
                    select(Symbol).where(Symbol.id == sym.parent_id)
                )
                parent = parent_result.scalar_one()
                self.symbols[f"{parent.name}.{sym.name}"] = sym.id
        
        # Parse file to extract calls with context
        try:
            with open(file.path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content, filename=file.path)
            visitor = CallVisitor(file_id, self.symbols, session)
            visitor.visit(tree)
            
            # Store the calls
            for call_info in visitor.calls:
                call = Call(
                    file_id=file_id,
                    line=call_info['line'],
                    column=call_info['column'],
                    caller_symbol_id=call_info.get('caller_id'),
                    callee_symbol_id=call_info.get('callee_id')
                )
                session.add(call)
            
            await session.commit()
            
        except Exception as e:
            # Skip files with parse errors
            pass


class CallVisitor(ast.NodeVisitor):
    """AST visitor to extract function calls with context."""
    
    def __init__(self, file_id: int, symbols: Dict[str, int], session: AsyncSession):
        self.file_id = file_id
        self.symbols = symbols
        self.session = session
        self.calls: List[Dict] = []
        self.current_function_id: Optional[int] = None
        self.current_class: Optional[str] = None
        self.imports: Dict[str, str] = {}
    
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Track current function context."""
        old_function = self.current_function_id
        
        # Look up function symbol
        if self.current_class:
            func_name = f"{self.current_class}.{node.name}"
        else:
            func_name = node.name
        
        self.current_function_id = self.symbols.get(func_name)
        
        # Visit function body
        self.generic_visit(node)
        
        self.current_function_id = old_function
    
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Track async function context."""
        self.visit_FunctionDef(node)
    
    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Track current class context."""
        old_class = self.current_class
        self.current_class = node.name
        
        # Visit class body
        self.generic_visit(node)
        
        self.current_class = old_class
    
    def visit_Import(self, node: ast.Import) -> None:
        """Track imports."""
        for alias in node.names:
            name = alias.asname or alias.name
            self.imports[name] = alias.name
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Track from imports."""
        module = node.module or ''
        for alias in node.names:
            name = alias.asname or alias.name
            self.imports[name] = f"{module}.{alias.name}"
        self.generic_visit(node)
    
    def visit_Call(self, node: ast.Call) -> None:
        """Extract function calls."""
        call_info = {
            'line': node.lineno,
            'column': node.col_offset,
            'caller_id': self.current_function_id
        }
        
        # Try to resolve the callee
        if isinstance(node.func, ast.Name):
            # Simple function call
            func_name = node.func.id
            
            # Check if it's an imported function
            if func_name in self.imports:
                # TODO: Resolve across files/modules
                pass
            else:
                # Local function
                call_info['callee_id'] = self.symbols.get(func_name)
        
        elif isinstance(node.func, ast.Attribute):
            # Method call (obj.method)
            attr_name = node.func.attr
            
            if isinstance(node.func.value, ast.Name):
                obj_name = node.func.value.id
                
                # Check for self.method() calls
                if obj_name == 'self' and self.current_class:
                    method_name = f"{self.current_class}.{attr_name}"
                    call_info['callee_id'] = self.symbols.get(method_name)
                else:
                    # Try to resolve obj.method
                    full_name = f"{obj_name}.{attr_name}"
                    call_info['callee_id'] = self.symbols.get(full_name)
        
        self.calls.append(call_info)
        self.generic_visit(node)


async def resolve_calls_in_repository(session: AsyncSession, repo_id: int) -> None:
    """Resolve all calls in a repository."""
    # Get all files in repository
    result = await session.execute(
        select(File).where(File.repository_id == repo_id)
    )
    files = result.scalars().all()
    
    analyzer = CallAnalyzer()
    
    for file in files:
        await analyzer.analyze_file_calls(session, file.id)