"""
Core state management tools for MCP projects
"""

from typing import Dict, Any, List
from fastmcp import FastMCP
from ..models import ProjectState, Tool, ToolStatus
from ..storage import load_project_state, save_project_state, init_database
from ..analyzers.code_scanner import MCPToolScanner
from ..utils.helpers import format_tools_for_analysis


async def get_project_state(project_name: str = "default") -> Dict[str, Any]:
    """Load current project state from storage"""
    try:
        await init_database()
        project = await load_project_state(project_name)

        return {
            "success": True,
            "project": {
                "name": project.name,
                "description": project.description,
                "total_tools": len(project.tools),
                "tools": {name: {
                    "name": tool.name,
                    "description": tool.description,
                    "status": tool.status.value,
                    "file_path": tool.file_path,
                    "function_name": tool.function_name,
                    "parameters": tool.parameters,
                    "return_type": tool.return_type,
                    "created_at": tool.created_at.isoformat(),
                    "updated_at": tool.updated_at.isoformat()
                } for name, tool in project.tools.items()},
                "created_at": project.created_at.isoformat(),
                "updated_at": project.updated_at.isoformat()
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


async def update_project_state(
    project_name: str = "default",
    description: str = "",
    tools: List[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Update project information and tools"""
    try:
        await init_database()
        project = await load_project_state(project_name)

        # Update description if provided
        if description:
            project.description = description

        # Update tools if provided
        if tools:
            for tool_data in tools:
                tool = Tool(
                    name=tool_data["name"],
                    description=tool_data.get("description", ""),
                    status=ToolStatus(tool_data.get("status", "planned")),
                    file_path=tool_data.get("file_path"),
                    function_name=tool_data.get("function_name"),
                    parameters=tool_data.get("parameters", []),
                    return_type=tool_data.get("return_type")
                )
                project.add_tool(tool)

        await save_project_state(project)

        return {
            "success": True,
            "message": f"Updated project '{project_name}'",
            "total_tools": len(project.tools)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


async def scan_project_files(
    project_name: str = "default",
    project_root: str = "."
) -> Dict[str, Any]:
    """Scan project files for MCP tools and update state"""
    try:
        await init_database()
        project = await load_project_state(project_name)

        # Scan for tools
        scanner = MCPToolScanner(project_root)
        discovered_tools = scanner.scan_project_files()

        # Add discovered tools to project
        new_tools = 0
        updated_tools = 0

        for tool in discovered_tools:
            if tool.name in project.tools:
                # Update existing tool
                existing = project.tools[tool.name]
                existing.file_path = tool.file_path
                existing.function_name = tool.function_name
                existing.parameters = tool.parameters
                existing.return_type = tool.return_type
                if existing.status == ToolStatus.PLANNED and tool.status in [ToolStatus.COMPLETED, ToolStatus.IMPLEMENTED]:
                    existing.status = tool.status
                updated_tools += 1
            else:
                # Add new tool
                project.add_tool(tool)
                new_tools += 1

        await save_project_state(project)

        # Get project summary
        summary = scanner.get_project_summary()

        return {
            "success": True,
            "message": f"Scanned project files",
            "discovered_tools": len(discovered_tools),
            "new_tools": new_tools,
            "updated_tools": updated_tools,
            "summary": summary
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


async def update_tool_status(
    tool_name: str,
    status: str,
    project_name: str = "default"
) -> Dict[str, Any]:
    """Update the status of a specific tool"""
    try:
        await init_database()
        project = await load_project_state(project_name)

        # Find and update the tool
        if tool_name not in project.tools:
            return {
                "success": False,
                "message": f"Tool '{tool_name}' not found in project '{project_name}'"
            }

        # Convert status string to ToolStatus enum - Fixed mapping
        status_map = {
            "planned": ToolStatus.PLANNED,
            "in_progress": ToolStatus.IN_PROGRESS,
            "implemented": ToolStatus.IMPLEMENTED,
            "completed": ToolStatus.COMPLETED,
            "testing": ToolStatus.TESTING,
            "tested": ToolStatus.TESTED,
            "deprecated": ToolStatus.DEPRECATED
        }

        if status.lower() not in status_map:
            return {
                "success": False,
                "message": f"Invalid status '{status}'. Valid options: {list(status_map.keys())}"
            }

        # Update the tool status
        project.tools[tool_name].status = status_map[status.lower()]

        # Save the updated project
        await save_project_state(project)

        return {
            "success": True,
            "message": f"Updated tool '{tool_name}' status to '{status}'"
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"Error updating tool status: {str(e)}"
        }


def register_state_tools(mcp: FastMCP):
    """Register state management tools with FastMCP"""

    @mcp.tool()
    async def get_project_state_tool(project_name: str = "default") -> Dict[str, Any]:
        """Load current project state from storage

        Args:
            project_name: Name of the project to load (default: "default")

        Returns:
            Dict containing project state and tools
        """
        return await get_project_state(project_name)

    @mcp.tool()
    async def update_project_state_tool(
        project_name: str = "default",
        description: str = "",
        tools: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Update project information and tools

        Args:
            project_name: Name of the project to update
            description: Project description
            tools: List of tool definitions to add/update

        Returns:
            Dict with success status and message
        """
        return await update_project_state(project_name, description, tools or [])

    @mcp.tool()
    async def scan_project_files_tool(
        project_name: str = "default",
        project_root: str = "."
    ) -> Dict[str, Any]:
        """Scan project files for MCP tools and update state

        Args:
            project_name: Name of the project to update
            project_root: Root directory to scan (default: current directory)

        Returns:
            Dict with scan results and discovered tools
        """
        return await scan_project_files(project_name, project_root)

    @mcp.tool()
    async def update_tool_status_tool(
        tool_name: str,
        status: str,
        project_name: str = "default"
    ) -> Dict[str, Any]:
        """Update the status of a specific tool

        Args:
            tool_name: Name of the tool to update
            status: New status (planned, in_progress, implemented, completed, testing, tested, deprecated)
            project_name: Name of the project containing the tool

        Returns:
            Dict with success status and message
        """
        return await update_tool_status(tool_name, status, project_name)