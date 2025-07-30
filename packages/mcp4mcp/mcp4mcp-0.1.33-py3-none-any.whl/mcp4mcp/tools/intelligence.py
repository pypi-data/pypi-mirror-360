"""
AI-powered intelligence and analysis tools
"""

from typing import Dict, Any, List
from fastmcp import FastMCP
from ..models import ProjectState, SimilarityResult
from ..storage import load_project_state, init_database
from ..analyzers.similarity import ToolSimilarityAnalyzer
from ..utils.helpers import format_tools_for_analysis, parse_suggestions, analyze_project_completeness


async def check_before_build(
    tool_name: str,
    tool_description: str,
    project_name: str = "default"
) -> Dict[str, Any]:
    """Check for duplicates and conflicts before building a new tool"""
    try:
        await init_database()
        project = await load_project_state(project_name)

        # Create temporary tool for comparison
        from ..models import Tool, ToolStatus
        temp_tool = Tool(
            name=tool_name,
            description=tool_description,
            status=ToolStatus.PLANNED
        )

        # Check for exact name conflicts
        if tool_name in project.tools:
            return {
                "success": True,
                "conflicts": True,
                "exact_match": True,
                "message": f"Tool '{tool_name}' already exists in project",
                "recommendation": "Choose a different name or update the existing tool"
            }

        # Check for similar tools
        analyzer = ToolSimilarityAnalyzer(similarity_threshold=0.6)
        similar_tools = []

        for existing_name, existing_tool in project.tools.items():
            similarity = analyzer.calculate_similarity(temp_tool, existing_tool)
            if similarity > 0.6:
                similar_tools.append({
                    "name": existing_name,
                    "similarity": similarity,
                    "explanation": analyzer._generate_explanation(temp_tool, existing_tool, similarity)
                })

        # Sort by similarity score
        similar_tools.sort(key=lambda x: x["similarity"], reverse=True)

        return {
            "success": True,
            "conflicts": len(similar_tools) > 0,
            "exact_match": False,
            "similar_tools": similar_tools[:3],  # Top 3 most similar
            "recommendation": "Proceed with caution - review similar tools" if similar_tools else "Clear to build"
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


async def suggest_next_action(
    project_name: str = "default",
    context: str = ""
) -> Dict[str, Any]:
    """Get AI-powered development suggestions"""
    try:
        await init_database()
        project = await load_project_state(project_name)

        # Analyze project completeness
        analysis = analyze_project_completeness(project)

        # Generate contextual suggestions
        suggestions = []

        # Based on project state
        if analysis.total_tools == 0:
            suggestions.extend([
                "Start by scanning your project files to discover existing tools",
                "Define your first MCP tool based on your project's core functionality",
                "Create a basic tool structure with clear parameters and return types"
            ])
        elif analysis.completion_percentage < 50:
            suggestions.extend([
                "Focus on completing planned tools to reach 50% completion",
                "Review in-progress tools and identify blocking issues",
                "Consider implementing the most critical tools first"
            ])
        elif analysis.completion_percentage < 90:
            suggestions.extend([
                "You're making good progress! Complete remaining tools",
                "Add comprehensive testing for completed tools",
                "Review tool documentation and descriptions"
            ])
        else:
            suggestions.extend([
                "Project is nearly complete! Focus on testing and refinement",
                "Consider adding advanced features or optimizations",
                "Document usage examples and best practices"
            ])

        # Check for similarity issues
        analyzer = ToolSimilarityAnalyzer()
        similarity_results = analyzer.analyze_tools(project.tools)

        if similarity_results:
            suggestions.append(f"Review {len(similarity_results)} similar tool pairs for potential consolidation")

        # Add context-specific suggestions
        if context:
            context_suggestions = _generate_context_suggestions(context, project)
            suggestions.extend(context_suggestions)

        # Limit suggestions
        suggestions = suggestions[:5]
        next_priority = _determine_next_priority(analysis, similarity_results)
        
        return {
            "success": True,
            "suggestions": suggestions,
            "next_priority": next_priority,
            "analysis": {
                "total_tools": analysis.total_tools,
                "completed_tools": analysis.completed_tools,
                "completion_percentage": analysis.completion_percentage,
                "similar_tool_pairs": len(similarity_results)
            },
            "project_analysis": {
                "total_tools": analysis.total_tools,
                "completed_tools": analysis.completed_tools,
                "completion_percentage": analysis.completion_percentage,
                "similar_tool_pairs": len(similarity_results)
            }
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


async def analyze_tool_similarity(
    project_name: str = "default",
    similarity_threshold: float = 0.7
) -> Dict[str, Any]:
    """Analyze tools for similarity and potential duplication"""
    try:
        await init_database()
        project = await load_project_state(project_name)

        if len(project.tools) < 2:
            return {
                "success": True,
                "message": "Need at least 2 tools to analyze similarity",
                "similarity_results": [],
                "similar_pairs": [],
                "total_comparisons": 0,
                "threshold": similarity_threshold,
                "summary": "No tools available for similarity analysis"
            }

        analyzer = ToolSimilarityAnalyzer(similarity_threshold)
        similarity_results = analyzer.analyze_tools(project.tools)

        # Find potential duplicates
        duplicates = analyzer.find_potential_duplicates(project.tools)

        # Format results
        formatted_results = []
        for result in similarity_results:
            formatted_results.append({
                "tool1": result.tool1_name,
                "tool2": result.tool2_name,
                "similarity": result.similarity_score,
                "explanation": result.explanation,
                "recommendation": result.recommended_action
            })

        return {
            "success": True,
            "similarity_results": formatted_results,
            "similar_pairs": formatted_results,  # Add this for backward compatibility
            "potential_duplicates": len(duplicates),
            "total_comparisons": len(similarity_results),
            "threshold": similarity_threshold
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def _generate_context_suggestions(context: str, project: ProjectState) -> List[str]:
    """Generate suggestions based on user context"""
    suggestions = []
    context_lower = context.lower()

    # Common development scenarios
    if "error" in context_lower or "bug" in context_lower:
        suggestions.append("Debug the issue by checking tool parameters and return types")
        suggestions.append("Review error logs and add proper error handling")

    if "test" in context_lower:
        suggestions.append("Add unit tests for your MCP tools")
        suggestions.append("Test tool integration with MCP clients")

    if "performance" in context_lower:
        suggestions.append("Profile tool execution time and optimize slow operations")
        suggestions.append("Consider caching for frequently accessed data")

    if "deploy" in context_lower:
        suggestions.append("Prepare your MCP server for deployment")
        suggestions.append("Ensure all tools are properly tested and documented")

    return suggestions


def _determine_next_priority(analysis, similarity_results) -> str:
    """Determine the next priority action"""
    if analysis.total_tools == 0:
        return "Create your first tool"
    elif len(similarity_results) > 0:
        return "Review similar tools for consolidation"
    elif analysis.completion_percentage < 50:
        return "Complete planned tools"
    elif analysis.completion_percentage < 90:
        return "Finish remaining tools and add testing"
    else:
        return "Polish and optimize existing tools"


def register_intelligence_tools(mcp: FastMCP):
    """Register intelligence tools with FastMCP"""

    @mcp.tool()
    async def check_before_build_tool(
        tool_name: str,
        tool_description: str,
        project_name: str = "default"
    ) -> Dict[str, Any]:
        """Check for duplicates and conflicts before building a new tool

        Args:
            tool_name: Name of the proposed new tool
            tool_description: Description of what the tool will do
            project_name: Name of the project to check against

        Returns:
            Dict with conflict analysis and recommendations
        """
        return await check_before_build(tool_name, tool_description, project_name)

    @mcp.tool()
    async def suggest_next_action_tool(
        project_name: str = "default",
        context: str = ""
    ) -> Dict[str, Any]:
        """Get AI-powered development suggestions

        Args:
            project_name: Name of the project to analyze
            context: Optional context about current development situation

        Returns:
            Dict with personalized suggestions and project analysis
        """
        return await suggest_next_action(project_name, context)

    @mcp.tool()
    async def analyze_tool_similarity_tool(
        project_name: str = "default",
        similarity_threshold: float = 0.7
    ) -> Dict[str, Any]:
        """Analyze tools for similarity and potential duplication

        Args:
            project_name: Name of the project to analyze
            similarity_threshold: Minimum similarity score to report (0.0-1.0)

        Returns:
            Dict with similarity analysis results
        """
        return await analyze_tool_similarity(project_name, similarity_threshold)