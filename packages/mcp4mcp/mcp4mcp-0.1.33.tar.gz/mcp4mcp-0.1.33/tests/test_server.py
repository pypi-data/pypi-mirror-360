"""
Tests for mcp4mcp server integration
"""

import pytest
import asyncio
import tempfile
import os
from pathlib import Path
from fastmcp import FastMCP, Client
from mcp4mcp.tools.state_management import register_state_tools
from mcp4mcp.tools.intelligence import register_intelligence_tools
from mcp4mcp.tools.tracking import register_tracking_tools


class TestServerIntegration:
    """Test server integration"""
    
    def setup_method(self):
        """Setup test server"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test.db"
        # Override the global DB_PATH for testing
        import mcp4mcp.storage
        self.original_db_path = mcp4mcp.storage.DB_PATH
        mcp4mcp.storage.DB_PATH = self.db_path
        
        # Create test server
        self.mcp = FastMCP("test-mcp4mcp")
        register_state_tools(self.mcp)
        register_intelligence_tools(self.mcp)
        register_tracking_tools(self.mcp)
    
    def teardown_method(self):
        """Cleanup test environment"""
        # Restore original DB_PATH
        import mcp4mcp.storage
        mcp4mcp.storage.DB_PATH = self.original_db_path
        
        # Remove test database
        if self.db_path.exists():
            os.remove(self.db_path)
        
        # Clean up temp directory
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_server_creation(self):
        """Test that server is created with tools"""
        assert self.mcp.name == "test-mcp4mcp"
        # Server is created successfully - we'll test tools with the Client
        assert isinstance(self.mcp, FastMCP)
    
    @pytest.mark.asyncio
    async def test_tool_registration(self):
        """Test that all expected tools are registered"""
        # Use the official FastMCP Client to test tool registration
        async with Client(self.mcp) as client:
            tools = await client.list_tools()
            tool_names = [tool.name for tool in tools]
            
            # State management tools
            assert "get_project_state_tool" in tool_names
            assert "update_project_state_tool" in tool_names
            assert "scan_project_files_tool" in tool_names
            assert "update_tool_status_tool" in tool_names
            
            # Intelligence tools
            assert "check_before_build_tool" in tool_names
            assert "suggest_next_action_tool" in tool_names
            assert "analyze_tool_similarity_tool" in tool_names
            
            # Tracking tools
            assert "track_development_session_tool" in tool_names
            assert "end_development_session_tool" in tool_names
            assert "get_development_sessions_tool" in tool_names
            assert "get_session_analytics_tool" in tool_names
    
    @pytest.mark.asyncio
    async def test_tool_execution(self):
        """Test that tools can be executed through the FastMCP server"""
        async with Client(self.mcp) as client:
            # Test get_project_state_tool
            result = await client.call_tool("get_project_state_tool", {
                "project_name": "test_project"
            })
            
            assert result.data["success"] is True
            assert "project" in result.data
            assert result.data["project"]["name"] == "test_project"
            
            # Test update_project_state_tool
            result = await client.call_tool("update_project_state_tool", {
                "project_name": "test_project",
                "description": "Test project description",
                "tools": [{
                    "name": "test_tool",
                    "description": "A test tool",
                    "status": "planned"
                }]
            })
            
            assert result.data["success"] is True
            assert result.data["total_tools"] == 1
            
            # Test track_development_session_tool
            result = await client.call_tool("track_development_session_tool", {
                "action": "Started testing",
                "project_name": "test_project"
            })
            
            assert result.data["success"] is True
            assert "session_id" in result.data
    
    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test that tools handle errors gracefully"""
        async with Client(self.mcp) as client:
            # Test with invalid tool status
            result = await client.call_tool("update_tool_status_tool", {
                "tool_name": "nonexistent_tool",
                "status": "invalid_status",
                "project_name": "test_project"
            })
            
            # Should return error response, not throw exception
            assert result.data["success"] is False
            assert "error" in result.data or "message" in result.data
    
    @pytest.mark.asyncio
    async def test_intelligence_tools(self):
        """Test intelligence tools functionality"""
        async with Client(self.mcp) as client:
            # First create a project with some tools
            await client.call_tool("update_project_state_tool", {
                "project_name": "intelligence_test",
                "tools": [
                    {"name": "file_reader", "description": "Read files", "status": "completed"},
                    {"name": "file_writer", "description": "Write files", "status": "planned"}
                ]
            })
            
            # Test check_before_build_tool
            result = await client.call_tool("check_before_build_tool", {
                "tool_name": "file_processor",
                "tool_description": "Process files",
                "project_name": "intelligence_test"
            })
            
            assert result.data["success"] is True
            assert "conflicts" in result.data
            
            # Test suggest_next_action_tool
            result = await client.call_tool("suggest_next_action_tool", {
                "project_name": "intelligence_test"
            })
            
            assert result.data["success"] is True
            assert "suggestions" in result.data
            assert "analysis" in result.data
            
            # Test analyze_tool_similarity_tool
            result = await client.call_tool("analyze_tool_similarity_tool", {
                "project_name": "intelligence_test",
                "similarity_threshold": 0.5
            })
            
            assert result.data["success"] is True
            assert "similarity_results" in result.data