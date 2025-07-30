"""
Pydantic data models for type safety and validation
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from enum import Enum


class ToolStatus(str, Enum):
    """Status of a tool in development"""
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    IMPLEMENTED = "implemented"  # Added missing status
    COMPLETED = "completed"
    TESTING = "testing"
    TESTED = "tested"  # Added missing status
    DEPRECATED = "deprecated"


class Tool(BaseModel):
    """Individual tool representation"""
    name: str
    description: str
    status: ToolStatus = ToolStatus.PLANNED
    file_path: Optional[str] = None
    function_name: Optional[str] = None
    parameters: List[Dict[str, Any]] = Field(default_factory=list)
    return_type: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    similarity_scores: Dict[str, float] = Field(default_factory=dict)


class SessionAction(BaseModel):
    """Individual action within a development session"""
    action: str
    tool_name: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    details: Optional[str] = None


class DevelopmentSession(BaseModel):
    """Session tracking data"""
    session_id: str
    project_name: str
    start_time: datetime = Field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    tools_worked_on: List[str] = Field(default_factory=list)
    actions_taken: List[str] = Field(default_factory=list)
    actions: List[SessionAction] = Field(default_factory=list)
    notes: str = ""


class SimilarityResult(BaseModel):
    """Tool similarity analysis results"""
    tool1_name: str
    tool2_name: str
    similarity_score: float
    explanation: str
    recommended_action: str


class ProjectAnalysis(BaseModel):
    """Project maturity analysis"""
    total_tools: int
    completed_tools: int
    completion_percentage: float
    suggested_next_actions: List[str]
    potential_duplicates: List[SimilarityResult]
    missing_patterns: List[str]


class ProjectState(BaseModel):
    """Main project state container"""
    name: str = "default"
    description: str = ""
    tools: Dict[str, Tool] = Field(default_factory=dict)
    sessions: List[DevelopmentSession] = Field(default_factory=list)
    analysis: Optional[ProjectAnalysis] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    def add_tool(self, tool: Tool) -> None:
        """Add a tool to the project"""
        self.tools[tool.name] = tool
        self.updated_at = datetime.now()
    
    def get_tool(self, name: str) -> Optional[Tool]:
        """Get a tool by name"""
        return self.tools.get(name)
    
    def update_tool_status(self, name: str, status: ToolStatus) -> bool:
        """Update tool status"""
        if name in self.tools:
            self.tools[name].status = status
            self.tools[name].updated_at = datetime.now()
            self.updated_at = datetime.now()
            return True
        return False