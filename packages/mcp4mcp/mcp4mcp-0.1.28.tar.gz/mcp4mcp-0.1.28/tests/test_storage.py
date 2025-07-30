"""
Tests for mcp4mcp storage backend
"""

import pytest
import asyncio
import tempfile
import os
from pathlib import Path
from mcp4mcp.storage import (
    init_database, load_project_state, save_project_state,
    find_similar_tools_db, get_development_sessions
)
from mcp4mcp.models import ProjectState, Tool, DevelopmentSession, ToolStatus


class TestStorage:
    """Test storage operations"""
    
    def setup_method(self):
        """Setup test database"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test.db"
        # Override the global DB_PATH for testing
        import mcp4mcp.storage
        self.original_db_path = mcp4mcp.storage.DB_PATH
        mcp4mcp.storage.DB_PATH = self.db_path
    
    def teardown_method(self):
        """Cleanup test database"""
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
    
    @pytest.mark.asyncio
    async def test_init_database(self):
        """Test database initialization"""
        await init_database()
        assert self.db_path.exists()
    
    @pytest.mark.asyncio
    async def test_save_and_load_project_state(self):
        """Test saving and loading project state"""
        await init_database()
        
        # Create test project
        project = ProjectState(
            name="test_project",
            description="A test project"
        )
        
        # Add a tool
        tool = Tool(name="test_tool", description="Test tool")
        project.add_tool(tool)
        
        # Save project
        await save_project_state(project)
        
        # Load project
        loaded_project = await load_project_state("test_project")
        
        assert loaded_project.name == "test_project"
        assert loaded_project.description == "A test project"
        assert len(loaded_project.tools) == 1
        assert "test_tool" in loaded_project.tools
    
    @pytest.mark.asyncio
    async def test_load_nonexistent_project(self):
        """Test loading a project that doesn't exist"""
        await init_database()
        
        project = await load_project_state("nonexistent_project")
        assert project.name == "nonexistent_project"
        assert project.description == ""
        assert len(project.tools) == 0
    
    @pytest.mark.asyncio
    async def test_find_similar_tools_db(self):
        """Test finding similar tools in database"""
        await init_database()
        
        # Create and save project with tools
        project = ProjectState(name="test_project")
        
        # Create tools with very similar names and descriptions to ensure matches
        tool1 = Tool(name="file_reader", description="Read files from disk storage")
        tool2 = Tool(name="file_writer", description="Write files to disk storage") 
        tool3 = Tool(name="file_processor", description="Process files from disk")
        tool4 = Tool(name="file_manager", description="Manage files on disk storage")
        tool5 = Tool(name="calculator", description="Perform mathematical calculations")
        
        project.add_tool(tool1)
        project.add_tool(tool2)
        project.add_tool(tool3)
        project.add_tool(tool4)
        project.add_tool(tool5)
        
        await save_project_state(project)
        
        # Find similar tools with a very low threshold to ensure we get matches
        similar_tools = await find_similar_tools_db(
            "file_handler", 
            "Handle files from disk storage", 
            "test_project", 
            0.3  # Very low threshold
        )
        
        # Should find at least some file-related tools
        assert len(similar_tools) >= 1, f"Expected at least 1 similar tool, found {len(similar_tools)}"
        
        # Verify that file-related tools are in the results
        found_tool_names = [tool.name for tool in similar_tools]
        file_tools = [name for name in found_tool_names if "file" in name]
        assert len(file_tools) >= 1, f"Expected at least 1 file-related tool, found tools: {found_tool_names}"
    
    @pytest.mark.asyncio
    async def test_get_development_sessions(self):
        """Test getting development sessions"""
        await init_database()
        
        # Create project with session
        project = ProjectState(name="test_project")
        session = DevelopmentSession(
            session_id="test_session_123",
            project_name="test_project"
        )
        project.sessions.append(session)
        
        await save_project_state(project)
        
        # Get sessions
        sessions = await get_development_sessions("test_project")
        assert len(sessions) >= 1
        assert sessions[0].project_name == "test_project"