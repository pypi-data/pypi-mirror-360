"""
AST parsing for tool discovery in MCP codebases
"""

import ast
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from ..models import Tool, ToolStatus


class MCPToolScanner:
    """Scans Python files for MCP tool definitions"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
    
    def scan_project_files(self) -> List[Tool]:
        """Scan all Python files in project for MCP tools"""
        tools = []
        
        # Look for Python files
        for py_file in self.project_root.rglob("*.py"):
            if self._should_skip_file(py_file):
                continue
                
            file_tools = self.scan_file(py_file)
            tools.extend(file_tools)
        
        return tools
    
    def scan_file(self, file_path: Path) -> List[Tool]:
        """Scan a single Python file for MCP tools"""
        tools = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            # Look for FastMCP tool registrations
            tools.extend(self._find_fastmcp_tools(tree, file_path))
            
            # Look for function definitions that might be tools
            tools.extend(self._find_function_tools(tree, file_path))
            
            # Look for class-based tools
            tools.extend(self._find_class_tools(tree, file_path))
            
        except Exception as e:
            print(f"Error scanning {file_path}: {e}")
        
        return tools
    
    def _should_skip_file(self, file_path: Path) -> bool:
        """Check if file should be skipped during scanning"""
        skip_patterns = [
            "__pycache__",
            ".git",
            ".venv",
            "venv",
            "node_modules",
            "test_",
            "_test.py",
            "tests"
        ]
        
        path_str = str(file_path)
        return any(pattern in path_str for pattern in skip_patterns)
    
    def _find_fastmcp_tools(self, tree: ast.AST, file_path: Path) -> List[Tool]:
        """Find FastMCP @tool decorated functions"""
        tools = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check for @tool decorator
                if self._has_tool_decorator(node):
                    tool = self._create_tool_from_function(node, file_path)
                    if tool:
                        tools.append(tool)
        
        return tools
    
    def _find_function_tools(self, tree: ast.AST, file_path: Path) -> List[Tool]:
        """Find functions that look like MCP tools"""
        tools = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Skip if already found as FastMCP tool
                if self._has_tool_decorator(node):
                    continue
                
                # Look for tool-like patterns
                if self._is_tool_like_function(node):
                    tool = self._create_tool_from_function(node, file_path)
                    if tool:
                        tools.append(tool)
        
        return tools
    
    def _find_class_tools(self, tree: ast.AST, file_path: Path) -> List[Tool]:
        """Find class-based tool implementations"""
        tools = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Look for tool-like classes
                if self._is_tool_like_class(node):
                    tool = self._create_tool_from_class(node, file_path)
                    if tool:
                        tools.append(tool)
        
        return tools
    
    def _has_tool_decorator(self, func_node: ast.FunctionDef) -> bool:
        """Check if function has @tool decorator"""
        for decorator in func_node.decorator_list:
            if isinstance(decorator, ast.Name) and decorator.id == "tool":
                return True
            elif isinstance(decorator, ast.Attribute) and decorator.attr == "tool":
                return True
            elif isinstance(decorator, ast.Call):
                # Handle @mcp.tool() style decorators
                if isinstance(decorator.func, ast.Attribute) and decorator.func.attr == "tool":
                    return True
                elif isinstance(decorator.func, ast.Name) and decorator.func.id == "tool":
                    return True
        return False
    
    def _is_tool_like_function(self, func_node: ast.FunctionDef) -> bool:
        """Check if function looks like an MCP tool"""
        # Common tool patterns
        tool_patterns = [
            "handle_",
            "process_",
            "get_",
            "set_",
            "update_",
            "create_",
            "delete_",
            "list_",
            "search_",
            "analyze_"
        ]
        
        func_name = func_node.name.lower()
        return any(func_name.startswith(pattern) for pattern in tool_patterns)
    
    def _is_tool_like_class(self, class_node: ast.ClassDef) -> bool:
        """Check if class looks like a tool implementation"""
        class_name = class_node.name.lower()
        return "tool" in class_name or "handler" in class_name
    
    def _create_tool_from_function(self, func_node: ast.FunctionDef, file_path: Path) -> Optional[Tool]:
        """Create Tool object from function AST node"""
        try:
            # Extract docstring
            description = ""
            if (func_node.body and 
                isinstance(func_node.body[0], ast.Expr) and 
                isinstance(func_node.body[0].value, ast.Constant)):
                description = func_node.body[0].value.value
            
            # Extract parameters
            parameters = []
            for arg in func_node.args.args:
                if arg.arg not in ["self", "ctx"]:  # Skip self and ctx parameters
                    param_info = {
                        "name": arg.arg,
                        "type": self._get_annotation_string(arg.annotation),
                        "required": True
                    }
                    parameters.append(param_info)
            
            # Extract return type
            return_type = self._get_annotation_string(func_node.returns)
            
            # Determine status based on implementation
            status = ToolStatus.IMPLEMENTED if len(func_node.body) > 1 else ToolStatus.PLANNED
            
            return Tool(
                name=func_node.name,
                description=description or f"Tool function: {func_node.name}",
                status=status,
                file_path=str(file_path.relative_to(self.project_root)),
                function_name=func_node.name,
                parameters=parameters,
                return_type=return_type
            )
            
        except Exception as e:
            print(f"Error creating tool from function {func_node.name}: {e}")
            return None
    
    def _create_tool_from_class(self, class_node: ast.ClassDef, file_path: Path) -> Optional[Tool]:
        """Create Tool object from class AST node"""
        try:
            # Extract docstring
            description = ""
            if (class_node.body and 
                isinstance(class_node.body[0], ast.Expr) and 
                isinstance(class_node.body[0].value, ast.Constant)):
                description = class_node.body[0].value.value
            
            # Look for main method (handle, execute, run, etc.)
            main_method = None
            for node in class_node.body:
                if isinstance(node, ast.FunctionDef):
                    if node.name in ["handle", "execute", "run", "__call__"]:
                        main_method = node.name
                        break
            
            return Tool(
                name=class_node.name,
                description=description or f"Tool class: {class_node.name}",
                status=ToolStatus.IMPLEMENTED,
                file_path=str(file_path.relative_to(self.project_root)),
                function_name=main_method,
                parameters=[],
                return_type=None
            )
            
        except Exception as e:
            print(f"Error creating tool from class {class_node.name}: {e}")
            return None
    
    def _get_annotation_string(self, annotation) -> Optional[str]:
        """Convert AST annotation to string"""
        if annotation is None:
            return None
        
        try:
            if isinstance(annotation, ast.Name):
                return annotation.id
            elif isinstance(annotation, ast.Attribute):
                return f"{annotation.value.id}.{annotation.attr}"
            elif isinstance(annotation, ast.Constant):
                return str(annotation.value)
            else:
                return str(annotation)
        except:
            return None
    
    def get_project_summary(self) -> Dict[str, Any]:
        """Get summary of project structure"""
        tools = self.scan_project_files()
        
        summary = {
            "total_tools": len(tools),
            "tools_by_status": {},
            "tools_by_file": {},
            "common_patterns": []
        }
        
        # Group by status
        for status in ToolStatus:
            count = sum(1 for tool in tools if tool.status == status)
            summary["tools_by_status"][status.value] = count
        
        # Group by file
        for tool in tools:
            file_path = tool.file_path or "unknown"
            if file_path not in summary["tools_by_file"]:
                summary["tools_by_file"][file_path] = []
            summary["tools_by_file"][file_path].append(tool.name)
        
        # Find common patterns
        all_names = [tool.name for tool in tools]
        patterns = self._find_naming_patterns(all_names)
        summary["common_patterns"] = patterns
        
        return summary
    
    def _find_naming_patterns(self, names: List[str]) -> List[str]:
        """Find common naming patterns in tool names"""
        patterns = []
        
        # Common prefixes
        prefixes = ["get_", "set_", "update_", "create_", "delete_", "list_", "handle_"]
        for prefix in prefixes:
            count = sum(1 for name in names if name.startswith(prefix))
            if count > 0:
                patterns.append(f"{prefix}* ({count} tools)")
        
        # Common suffixes
        suffixes = ["_tool", "_handler", "_processor"]
        for suffix in suffixes:
            count = sum(1 for name in names if name.endswith(suffix))
            if count > 0:
                patterns.append(f"*{suffix} ({count} tools)")
        
        return patterns