
"""
Tests for mcp4mcp data models
"""

import pytest
from datetime import datetime
from mcp4mcp.models import (
    ProjectState, Tool, DevelopmentSession, SimilarityResult, 
    ProjectAnalysis, ToolStatus, SessionAction
)


class TestTool:
    """Test Tool model"""
    
    def test_tool_creation(self):
        """Test basic tool creation"""
        tool = Tool(
            name="test_tool",
            description="A test tool"
        )
        assert tool.name == "test_tool"
        assert tool.description == "A test tool"
        assert tool.status == ToolStatus.PLANNED
        assert isinstance(tool.created_at, datetime)
    
    def test_tool_with_parameters(self):
        """Test tool with parameters"""
        tool = Tool(
            name="parameterized_tool",
            description="Tool with parameters",
            parameters=[
                {"name": "param1", "type": "str", "description": "First parameter"},
                {"name": "param2", "type": "int", "description": "Second parameter"}
            ]
        )
        assert len(tool.parameters) == 2
        assert tool.parameters[0]["name"] == "param1"


class TestProjectState:
    """Test ProjectState model"""
    
    def test_project_creation(self):
        """Test basic project creation"""
        project = ProjectState(
            name="test_project",
            description="A test project"
        )
        assert project.name == "test_project"
        assert project.description == "A test project"
        assert len(project.tools) == 0
        assert len(project.sessions) == 0
    
    def test_add_tool(self):
        """Test adding a tool to project"""
        project = ProjectState(name="test_project")
        tool = Tool(name="test_tool", description="Test tool")
        
        project.add_tool(tool)
        
        assert len(project.tools) == 1
        assert "test_tool" in project.tools
        assert project.tools["test_tool"].name == "test_tool"
    
    def test_get_tool(self):
        """Test getting a tool from project"""
        project = ProjectState(name="test_project")
        tool = Tool(name="test_tool", description="Test tool")
        project.add_tool(tool)
        
        retrieved_tool = project.get_tool("test_tool")
        assert retrieved_tool is not None
        assert retrieved_tool.name == "test_tool"
        
        missing_tool = project.get_tool("missing_tool")
        assert missing_tool is None
    
    def test_update_tool_status(self):
        """Test updating tool status"""
        project = ProjectState(name="test_project")
        tool = Tool(name="test_tool", description="Test tool")
        project.add_tool(tool)
        
        success = project.update_tool_status("test_tool", ToolStatus.COMPLETED)
        assert success is True
        assert project.tools["test_tool"].status == ToolStatus.COMPLETED
        
        failure = project.update_tool_status("missing_tool", ToolStatus.COMPLETED)
        assert failure is False


class TestDevelopmentSession:
    """Test DevelopmentSession model"""
    
    def test_session_creation(self):
        """Test basic session creation"""
        session = DevelopmentSession(
            session_id="test_session",
            project_name="test_project",
            actions=[SessionAction(
                action="Started development",
                tool_name="test_tool",
                timestamp=datetime.now()
            )]
        )
        assert session.project_name == "test_project"
        assert len(session.actions) == 1
        assert session.actions[0].action == "Started development"


class TestSimilarityResult:
    """Test SimilarityResult model"""
    
    def test_similarity_result_creation(self):
        """Test similarity result creation"""
        result = SimilarityResult(
            tool1_name="tool1",
            tool2_name="tool2",
            similarity_score=0.85,
            explanation="High similarity detected",
            recommended_action="Consider merging these tools"
        )
        assert result.tool1_name == "tool1"
        assert result.tool2_name == "tool2"
        assert result.similarity_score == 0.85
        assert result.explanation == "High similarity detected"


class TestProjectAnalysis:
    """Test ProjectAnalysis model"""
    
    def test_project_analysis_creation(self):
        """Test project analysis creation"""
        analysis = ProjectAnalysis(
            total_tools=5,
            completed_tools=3,
            completion_percentage=60.0,
            suggested_next_actions=["Add more error handling", "Improve documentation"],
            potential_duplicates=[],
            missing_patterns=[]
        )
        assert analysis.total_tools == 5
        assert analysis.completed_tools == 3
        assert analysis.completion_percentage == 60.0
        assert len(analysis.suggested_next_actions) == 2
