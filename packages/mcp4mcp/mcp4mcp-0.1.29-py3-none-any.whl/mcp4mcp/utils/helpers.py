"""
Shared utility functions
"""

from typing import Dict, List, Any
from ..models import ProjectState, Tool, ProjectAnalysis, ToolStatus, SimilarityResult


def analyze_project_completeness(project: ProjectState) -> ProjectAnalysis:
    """Calculate completion metrics"""
    total_tools = len(project.tools)
    
    # Count completed tools (both COMPLETED and IMPLEMENTED count as completed)
    completed_tools = sum(1 for tool in project.tools.values() 
                         if tool.status in [ToolStatus.COMPLETED, ToolStatus.IMPLEMENTED])
    
    completion_percentage = (completed_tools / total_tools * 100) if total_tools > 0 else 0
    
    # Generate suggested next actions
    suggested_actions = []
    
    # Check for tools in progress
    in_progress = [tool for tool in project.tools.values() 
                   if tool.status == ToolStatus.IN_PROGRESS]
    if in_progress:
        suggested_actions.append(f"Continue working on {len(in_progress)} tools in progress")
    
    # Check for planned tools
    planned = [tool for tool in project.tools.values() 
               if tool.status == ToolStatus.PLANNED]
    if planned:
        suggested_actions.append(f"Start implementing {len(planned)} planned tools")
    
    # Check for testing tools
    testing = [tool for tool in project.tools.values() 
               if tool.status == ToolStatus.TESTING]
    if testing:
        suggested_actions.append(f"Complete testing for {len(testing)} tools")
    
    if not suggested_actions:
        suggested_actions.append("Project appears complete - consider adding more features")
    
    return ProjectAnalysis(
        total_tools=total_tools,
        completed_tools=completed_tools,
        completion_percentage=completion_percentage,
        suggested_next_actions=suggested_actions,
        potential_duplicates=[],  # Will be filled by similarity analysis
        missing_patterns=[]  # Will be filled by pattern analysis
    )


def format_tools_for_analysis(tools: Dict[str, Tool]) -> str:
    """Format tool data for LLM analysis"""
    if not tools:
        return "No tools found in project."
    
    formatted = "Project Tools:\n\n"
    for name, tool in tools.items():
        formatted += f"Tool: {name}\n"
        formatted += f"  Description: {tool.description}\n"
        formatted += f"  Status: {tool.status.value}\n"
        formatted += f"  File: {tool.file_path or 'Not specified'}\n"
        formatted += f"  Function: {tool.function_name or 'Not specified'}\n"
        if tool.parameters:
            formatted += f"  Parameters: {len(tool.parameters)} defined\n"
        formatted += "\n"
    
    return formatted


def parse_suggestions(llm_response: str) -> List[str]:
    """Parse LLM suggestions into actionable items"""
    if not llm_response:
        return []
    
    # Split by common delimiters
    suggestions = []
    for line in llm_response.split('\n'):
        line = line.strip()
        if not line:
            continue
        
        # Remove common prefixes
        prefixes = ['- ', '• ', '* ', '1. ', '2. ', '3. ', '4. ', '5. ']
        for prefix in prefixes:
            if line.startswith(prefix):
                line = line[len(prefix):].strip()
                break
        
        if line and len(line) > 10:  # Filter out very short suggestions
            suggestions.append(line)
    
    return suggestions[:5]  # Limit to 5 suggestions


def calculate_project_health_score(project: ProjectState) -> float:
    """Calculate overall project health score (0-100)"""
    if not project.tools:
        return 0.0
    
    # Completion score (40% weight)
    analysis = analyze_project_completeness(project)
    completion_score = analysis.completion_percentage * 0.4
    
    # Recency score (30% weight) - how recently tools were updated
    from datetime import datetime, timedelta
    now = datetime.now()
    recent_updates = sum(1 for tool in project.tools.values() 
                        if (now - tool.updated_at) < timedelta(days=7))
    recency_score = (recent_updates / len(project.tools)) * 30
    
    # Documentation score (20% weight) - tools with descriptions
    documented = sum(1 for tool in project.tools.values() 
                    if tool.description and len(tool.description) > 10)
    documentation_score = (documented / len(project.tools)) * 20
    
    # Activity score (10% weight) - development sessions
    activity_score = min(len(project.sessions) * 2, 10)
    
    return completion_score + recency_score + documentation_score + activity_score


def get_project_stats(project: ProjectState) -> Dict[str, Any]:
    """Get comprehensive project statistics"""
    stats = {
        "total_tools": len(project.tools),
        "tools_by_status": {},
        "health_score": calculate_project_health_score(project),
        "total_sessions": len(project.sessions),
        "last_updated": project.updated_at.isoformat(),
    }
    
    # Count tools by status
    for status in ToolStatus:
        count = sum(1 for tool in project.tools.values() if tool.status == status)
        stats["tools_by_status"][status.value] = count
    
    return stats