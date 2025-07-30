"""Mermaid diagram generation."""

from collections import defaultdict
from typing import Dict, List, Set

from ..storage.models import Import


def generate_module_diagram(imports: List[Import], show_cross_repo: bool = True) -> str:
    """Generate a Mermaid diagram showing module dependencies."""
    # Build module dependency graph
    module_deps: Dict[str, Set[Tuple[str, bool]]] = defaultdict(set)
    cross_repo_deps: Dict[str, Set[str]] = defaultdict(set)
    
    for imp in imports:
        # Extract module name from file path
        file_module = imp.file.path.replace('/', '.').replace('.py', '')
        
        # Check if it's a cross-repo import
        is_cross_repo = (imp.resolved_repository_id and 
                        imp.resolved_repository_id != imp.file.repository_id)
        
        if is_cross_repo and show_cross_repo:
            # Track cross-repo dependencies
            source_repo = imp.file.repository.name if hasattr(imp.file, 'repository') else 'unknown'
            target_repo = imp.resolved_repository.name if hasattr(imp, 'resolved_repository') else imp.module.split('.')[0]
            cross_repo_deps[source_repo].add(target_repo)
        
        # Add dependency
        if imp.module and not imp.module.startswith('.'):
            target = imp.module.split('.')[0]
            module_deps[file_module].add((target, is_cross_repo))
    
    # Generate Mermaid syntax
    lines = ["graph TD"]
    
    # Add subgraphs for repositories if showing cross-repo
    if show_cross_repo and cross_repo_deps:
        repo_modules = defaultdict(set)
        
        # Group modules by repository
        for module in module_deps:
            # Determine repo from module name (simplified)
            if 'slush_client' in module or 'src.' in module:
                repo_modules['slush-client'].add(module)
            elif 'slush.' in module:
                repo_modules['slush'].add(module)
            else:
                repo_modules['other'].add(module)
        
        # Create subgraphs
        for repo, modules in repo_modules.items():
            if modules:
                lines.append(f'    subgraph {repo}["{repo}"]')
                for module in modules:
                    short_name = module.split('.')[-1]
                    lines.append(f'        {module.replace(".", "_")}["{short_name}"]')
                lines.append('    end')
    
    # Add edges
    for module, deps in module_deps.items():
        module_id = module.replace('.', '_')
        
        for dep, is_cross_repo in deps:
            # Skip standard library modules
            if dep in {'os', 'sys', 'json', 'datetime', 'pathlib', 'typing', 
                       'collections', 'itertools', 'functools', 're', 'ast', 
                       'asyncio', 'logging', 'uuid', 'time', 'math'}:
                continue
            
            dep_id = dep.replace('.', '_')
            
            if is_cross_repo:
                lines.append(f'    {module_id} -.->|cross-repo| {dep_id}')
            else:
                lines.append(f'    {module_id} --> {dep_id}')
    
    # Add styling
    if show_cross_repo:
        lines.append('')
        lines.append('    %% Styling for cross-repo dependencies')
        lines.append('    linkStyle 0 stroke:#ff6600,stroke-width:2px,stroke-dasharray: 5 5')
    
    if len(lines) == 1:
        lines.append("    %% No external dependencies found")
    
    return '\n'.join(lines)


def generate_class_diagram(symbols: List) -> str:
    """Generate a Mermaid class diagram."""
    lines = ["classDiagram"]
    
    # Group symbols by class
    classes = {}
    standalone_functions = []
    
    for symbol in symbols:
        if symbol.type == 'class':
            classes[symbol.name] = {
                'methods': [],
                'symbol': symbol
            }
        elif symbol.type == 'method' and symbol.parent:
            if symbol.parent.name in classes:
                classes[symbol.parent.name]['methods'].append(symbol)
        elif symbol.type == 'function':
            standalone_functions.append(symbol)
    
    # Generate class definitions
    for class_name, class_info in classes.items():
        lines.append(f"    class {class_name} {{")
        
        for method in class_info['methods']:
            # Simple method signature
            lines.append(f"        +{method.name}()")
        
        lines.append("    }")
    
    # TODO: Add relationships between classes (inheritance, composition)
    
    return '\n'.join(lines)


def generate_call_flow_diagram(call_chain: List) -> str:
    """Generate a sequence diagram for a call flow."""
    lines = ["sequenceDiagram"]
    
    # TODO: Implement call flow visualization
    lines.append("    %% Call flow not yet implemented")
    
    return '\n'.join(lines)


def generate_system_architecture_diagram(repositories: List, imports: List[Import]) -> str:
    """Generate a system architecture diagram showing repos and their connections."""
    lines = ["graph TB"]
    lines.append("    %% System Architecture")
    
    # Define repository nodes with styling
    for repo in repositories:
        lines.append(f'    {repo.name}["{repo.name}<br/>({repo.language})"]')
    
    # Track cross-repo dependencies
    cross_repo_deps = defaultdict(set)
    
    for imp in imports:
        if imp.resolved_repository_id and imp.file.repository_id != imp.resolved_repository_id:
            # Cross-repository import
            source_repo = next(r for r in repositories if r.id == imp.file.repository_id)
            target_repo = next(r for r in repositories if r.id == imp.resolved_repository_id)
            cross_repo_deps[source_repo.name].add(target_repo.name)
    
    # Add edges for dependencies
    for source, targets in cross_repo_deps.items():
        for target in targets:
            lines.append(f'    {source} --> {target}')
    
    # Add styling
    lines.append('')
    lines.append('    %% Styling')
    lines.append('    classDef default fill:#e1f5fe,stroke:#01579b,stroke-width:2px')
    lines.append('    classDef server fill:#fff3e0,stroke:#e65100,stroke-width:2px')
    lines.append('    classDef client fill:#f3e5f5,stroke:#4a148c,stroke-width:2px')
    
    # Apply styles based on tags (if available)
    for repo in repositories:
        if 'server' in repo.name or 'backend' in repo.name:
            lines.append(f'    class {repo.name} server')
        elif 'client' in repo.name or 'frontend' in repo.name:
            lines.append(f'    class {repo.name} client')
    
    return '\n'.join(lines)