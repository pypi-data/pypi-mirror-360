
"""
Example MCP tools for testing mcp4mcp functionality
"""

import os
import math
from pathlib import Path
from typing import Dict, List, Any
from fastmcp import FastMCP


def register_file_tools(mcp: FastMCP):
    """Register file manipulation tools"""
    
    @mcp.tool()
    async def read_file_tool(file_path: str) -> Dict[str, Any]:
        """Read contents of a file
        
        Args:
            file_path: Path to the file to read
            
        Returns:
            Dict with file contents or error message
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return {
                "success": True,
                "content": content,
                "file_path": file_path,
                "size": len(content)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "file_path": file_path
            }
    
    @mcp.tool()
    async def write_file_tool(file_path: str, content: str) -> Dict[str, Any]:
        """Write content to a file
        
        Args:
            file_path: Path to the file to write
            content: Content to write to the file
            
        Returns:
            Dict with success status and file information
        """
        try:
            # Create directory if it doesn't exist
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return {
                "success": True,
                "file_path": file_path,
                "bytes_written": len(content.encode('utf-8'))
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "file_path": file_path
            }
    
    @mcp.tool()
    async def list_files_tool(directory: str = ".") -> Dict[str, Any]:
        """List files in a directory
        
        Args:
            directory: Directory to list files from (default: current directory)
            
        Returns:
            Dict with file list or error message
        """
        try:
            files = []
            for item in os.listdir(directory):
                item_path = os.path.join(directory, item)
                files.append({
                    "name": item,
                    "path": item_path,
                    "is_file": os.path.isfile(item_path),
                    "is_directory": os.path.isdir(item_path),
                    "size": os.path.getsize(item_path) if os.path.isfile(item_path) else 0
                })
            
            return {
                "success": True,
                "directory": directory,
                "files": files,
                "total_count": len(files)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "directory": directory
            }


def register_math_tools(mcp: FastMCP):
    """Register mathematical calculation tools"""
    
    @mcp.tool()
    async def calculate_tool(expression: str) -> Dict[str, Any]:
        """Evaluate a mathematical expression
        
        Args:
            expression: Mathematical expression to evaluate
            
        Returns:
            Dict with calculation result or error message
        """
        try:
            # Basic safety check - only allow certain characters
            allowed_chars = set('0123456789+-*/.() ')
            if not all(c in allowed_chars for c in expression):
                return {
                    "success": False,
                    "error": "Invalid characters in expression",
                    "expression": expression
                }
            
            result = eval(expression)
            return {
                "success": True,
                "expression": expression,
                "result": result,
                "type": type(result).__name__
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "expression": expression
            }
    
    @mcp.tool()
    async def sqrt_tool(number: float) -> Dict[str, Any]:
        """Calculate square root of a number
        
        Args:
            number: Number to calculate square root of
            
        Returns:
            Dict with square root result or error message
        """
        try:
            if number < 0:
                return {
                    "success": False,
                    "error": "Cannot calculate square root of negative number",
                    "number": number
                }
            
            result = math.sqrt(number)
            return {
                "success": True,
                "number": number,
                "result": result
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "number": number
            }
    
    @mcp.tool()
    async def power_tool(base: float, exponent: float) -> Dict[str, Any]:
        """Calculate power of a number
        
        Args:
            base: Base number
            exponent: Exponent to raise base to
            
        Returns:
            Dict with power calculation result or error message
        """
        try:
            result = math.pow(base, exponent)
            return {
                "success": True,
                "base": base,
                "exponent": exponent,
                "result": result
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "base": base,
                "exponent": exponent
            }
    
    @mcp.tool()
    async def factorial_tool(number: int) -> Dict[str, Any]:
        """Calculate factorial of a number
        
        Args:
            number: Number to calculate factorial of
            
        Returns:
            Dict with factorial result or error message
        """
        try:
            if number < 0:
                return {
                    "success": False,
                    "error": "Cannot calculate factorial of negative number",
                    "number": number
                }
            
            if number > 170:
                return {
                    "success": False,
                    "error": "Number too large for factorial calculation",
                    "number": number
                }
            
            result = math.factorial(number)
            return {
                "success": True,
                "number": number,
                "result": result
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "number": number
            }
