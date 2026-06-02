# src/parser.py
# Analyses Python code structure using AST
# before sending to LLM models

import ast
import textwrap
from dataclasses import dataclass
from typing import List

@dataclass
class CodeMetadata:
    """Structured metadata extracted from code"""
    raw_code: str
    lines_of_code: int
    functions: List[str]
    classes: List[str]
    imports: List[str]
    complexity: str
    has_docstrings: bool
    has_type_hints: bool
    potential_issues: List[str]


def parse_code(code: str) -> CodeMetadata:
    """
    Parse Python code and extract structural metadata
    using Python's built in AST library
    """
    
    # clean up indentation issues
    code = textwrap.dedent(code).strip()
    
    # initialise tracking lists
    functions = []
    classes = []
    imports = []
    potential_issues = []
    has_docstrings = False
    has_type_hints = False
    
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return CodeMetadata(
            raw_code=code,
            lines_of_code=len(code.splitlines()),
            functions=[],
            classes=[],
            imports=[],
            complexity="unknown",
            has_docstrings=False,
            has_type_hints=False,
            potential_issues=[f"Syntax error: {str(e)}"]
        )
    
    # walk through AST nodes
    for node in ast.walk(tree):
        
        # extract function names
        if isinstance(node, ast.FunctionDef):
            functions.append(node.name)
            
            # check for docstrings
            if (ast.get_docstring(node)):
                has_docstrings = True
            
            # check for type hints
            if node.returns or any(
                arg.annotation for arg in node.args.args
            ):
                has_type_hints = True
            
            # flag very long functions
            func_lines = node.end_lineno - node.lineno
            if func_lines > 50:
                potential_issues.append(
                    f"Function '{node.name}' is {func_lines} lines long — consider breaking it up"
                )
        
        # extract class names
        elif isinstance(node, ast.ClassDef):
            classes.append(node.name)
        
        # extract imports
        elif isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        
        elif isinstance(node, ast.ImportFrom):
            imports.append(node.module or "unknown")
        
        # flag hardcoded passwords or secrets
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    name_lower = target.id.lower()
                    if any(keyword in name_lower for keyword in 
                           ["password", "secret", "key", "token", "api"]):
                        potential_issues.append(
                            f"Possible hardcoded secret in variable '{target.id}'"
                        )
        
        # flag bare except clauses
        elif isinstance(node, ast.ExceptHandler):
            if node.type is None:
                potential_issues.append(
                    "Bare except clause found — catches all exceptions including KeyboardInterrupt"
                )
        
        # flag nested loops — potential O(n²)
        elif isinstance(node, (ast.For, ast.While)):
            for child in ast.walk(node):
                if child is not node and isinstance(child, (ast.For, ast.While)):
                    potential_issues.append(
                        "Nested loop detected — potential O(n²) performance issue"
                    )
                    break
    
    # determine complexity
    total_nodes = sum(1 for _ in ast.walk(tree))
    if total_nodes < 50:
        complexity = "low"
    elif total_nodes < 150:
        complexity = "medium"
    else:
        complexity = "high"
    
    return CodeMetadata(
        raw_code=code,
        lines_of_code=len(code.splitlines()),
        functions=functions,
        classes=classes,
        imports=imports,
        complexity=complexity,
        has_docstrings=has_docstrings,
        has_type_hints=has_type_hints,
        potential_issues=list(set(potential_issues))  # remove duplicates
    )


def get_summary(metadata: CodeMetadata) -> str:
    """Return a human readable summary of code metadata"""
    
    return f"""
Code Analysis Summary:
- Lines of code: {metadata.lines_of_code}
- Functions: {', '.join(metadata.functions) if metadata.functions else 'None'}
- Classes: {', '.join(metadata.classes) if metadata.classes else 'None'}
- Imports: {', '.join(metadata.imports) if metadata.imports else 'None'}
- Complexity: {metadata.complexity}
- Has docstrings: {metadata.has_docstrings}
- Has type hints: {metadata.has_type_hints}
- Pre-detected issues: {len(metadata.potential_issues)}
{chr(10).join(f'  • {issue}' for issue in metadata.potential_issues) if metadata.potential_issues else '  • None detected'}
""".strip()