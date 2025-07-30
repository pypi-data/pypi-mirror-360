"""Python AST parser for extracting code structure."""

import ast
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


@dataclass
class Symbol:
    """Represents a code symbol (function, class, method)."""
    name: str
    type: str  # 'function', 'class', 'method'
    file: str
    line: int
    column: int
    parent: Optional[str] = None
    docstring: Optional[str] = None


@dataclass
class Import:
    """Represents an import statement."""
    module: str
    file: str
    line: int
    name: Optional[str] = None
    alias: Optional[str] = None


@dataclass
class Call:
    """Represents a function/method call."""
    name: str
    file: str
    line: int
    column: int
    in_function: Optional[str] = None


@dataclass
class FileInfo:
    """Information extracted from a single file."""
    path: str
    symbols: List[Symbol] = field(default_factory=list)
    imports: List[Import] = field(default_factory=list)
    calls: List[Call] = field(default_factory=list)


class PythonParser:
    """Parser for Python source files using AST."""
    
    def __init__(self):
        self.current_file: Optional[str] = None
        self.current_class: Optional[str] = None
        self.current_function: Optional[str] = None
        self.symbols: List[Symbol] = []
        self.imports: List[Import] = []
        self.calls: List[Call] = []
    
    def parse_file(self, file_path: str) -> FileInfo:
        """Parse a Python file and extract structure information."""
        self.current_file = str(file_path)
        self.current_class = None
        self.current_function = None
        self.symbols = []
        self.imports = []
        self.calls = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content, filename=file_path)
            self._visit_node(tree)
            
            return FileInfo(
                path=self.current_file,
                symbols=self.symbols[:],
                imports=self.imports[:],
                calls=self.calls[:]
            )
        except Exception as e:
            # Return empty info on parse errors
            return FileInfo(path=self.current_file)
    
    def _visit_node(self, node: ast.AST, parent: Optional[str] = None) -> None:
        """Recursively visit AST nodes."""
        if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
            self._handle_function(node, parent)
        elif isinstance(node, ast.ClassDef):
            self._handle_class(node)
        elif isinstance(node, ast.Import):
            self._handle_import(node)
        elif isinstance(node, ast.ImportFrom):
            self._handle_import_from(node)
        elif isinstance(node, ast.Call):
            self._handle_call(node)
        
        # Visit child nodes
        for child in ast.iter_child_nodes(node):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self._visit_node(child, node.name)
            else:
                self._visit_node(child, parent)
    
    def _handle_function(self, node: ast.FunctionDef, parent: Optional[str]) -> None:
        """Extract function information."""
        docstring = ast.get_docstring(node)
        
        symbol = Symbol(
            name=node.name,
            type='method' if self.current_class else 'function',
            file=self.current_file,
            line=node.lineno,
            column=node.col_offset,
            parent=self.current_class,
            docstring=docstring
        )
        self.symbols.append(symbol)
        
        # Track current function for call context
        old_function = self.current_function
        self.current_function = node.name
        
        # Visit function body
        for child in node.body:
            self._visit_node(child, node.name)
        
        self.current_function = old_function
    
    def _handle_class(self, node: ast.ClassDef) -> None:
        """Extract class information."""
        docstring = ast.get_docstring(node)
        
        symbol = Symbol(
            name=node.name,
            type='class',
            file=self.current_file,
            line=node.lineno,
            column=node.col_offset,
            docstring=docstring
        )
        self.symbols.append(symbol)
        
        # Track current class
        old_class = self.current_class
        self.current_class = node.name
        
        # Visit class body
        for child in node.body:
            self._visit_node(child, node.name)
        
        self.current_class = old_class
    
    def _handle_import(self, node: ast.Import) -> None:
        """Extract import statements."""
        for alias in node.names:
            imp = Import(
                module=alias.name,
                alias=alias.asname,
                file=self.current_file,
                line=node.lineno
            )
            self.imports.append(imp)
    
    def _handle_import_from(self, node: ast.ImportFrom) -> None:
        """Extract from-import statements."""
        module = node.module or ''
        for alias in node.names:
            imp = Import(
                module=module,
                name=alias.name,
                alias=alias.asname,
                file=self.current_file,
                line=node.lineno
            )
            self.imports.append(imp)
    
    def _handle_call(self, node: ast.Call) -> None:
        """Extract function calls."""
        if isinstance(node.func, ast.Name):
            call_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            call_name = self._get_attribute_name(node.func)
        else:
            return
        
        call = Call(
            name=call_name,
            file=self.current_file,
            line=node.lineno,
            column=node.col_offset,
            in_function=self.current_function
        )
        self.calls.append(call)
    
    def _get_attribute_name(self, node: ast.Attribute) -> str:
        """Get full attribute name (e.g., 'obj.method')."""
        if isinstance(node.value, ast.Name):
            return f"{node.value.id}.{node.attr}"
        elif isinstance(node.value, ast.Attribute):
            return f"{self._get_attribute_name(node.value)}.{node.attr}"
        else:
            return node.attr