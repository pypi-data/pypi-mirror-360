"""
Development session tracking tools
"""

import json
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from fastmcp import FastMCP
from ..storage import init_database, load_project_state, save_project_state
from ..models import DevelopmentSession, SessionAction


async def track_development_session(
    action: str,
    project_name: str = "default",
    tool_name: str = "",
    notes: str = "",
    session_id: str = ""
) -> Dict[str, Any]:
    """Log development activities and track sessions"""
    try:
        await init_database()
        project = await load_project_state(project_name)

        # Find or create current session
        current_session = None
        if session_id:
            # Look for existing session
            for session in project.sessions:
                if session.session_id == session_id and session.end_time is None:
                    current_session = session
                    break

        if not current_session:
            # Create new session
            current_session = DevelopmentSession(
                session_id=session_id or str(uuid.uuid4()),
                project_name=project_name,
                start_time=datetime.now()
            )
            project.sessions.append(current_session)

        # Log the action
        current_session.actions_taken.append(f"{datetime.now().isoformat()}: {action}")

        # Track tool if specified
        if tool_name and tool_name not in current_session.tools_worked_on:
            current_session.tools_worked_on.append(tool_name)

        # Add notes
        if notes:
            if current_session.notes:
                current_session.notes += f"\n{datetime.now().isoformat()}: {notes}"
            else:
                current_session.notes = f"{datetime.now().isoformat()}: {notes}"

        await save_project_state(project)

        return {
            "success": True,
            "session_id": current_session.session_id,
            "action": action,
            "message": f"Logged action: {action}",
            "project_name": project_name,
            "action_count": len(current_session.actions_taken)
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


async def end_development_session(
    session_id: str,
    project_name: str = "default"
) -> Dict[str, Any]:
    """End a development session"""
    try:
        await init_database()
        project = await load_project_state(project_name)

        # Find the session
        target_session = None
        for session in project.sessions:
            if session.session_id == session_id and session.end_time is None:
                target_session = session
                break

        if not target_session:
            return {
                "success": False,
                "error": f"Active session '{session_id}' not found"
            }

        # End the session
        target_session.end_time = datetime.now()
        duration = target_session.end_time - target_session.start_time

        await save_project_state(project)

        return {
            "success": True,
            "message": f"Session ended",
            "session_id": session_id,
            "duration": str(duration),
            "actions_taken": len(target_session.actions_taken),
            "tools_worked_on": target_session.tools_worked_on,
            "summary": _generate_session_summary(target_session)
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


async def get_development_sessions_list(
    project_name: str = "default",
    limit: int = 10
) -> Dict[str, Any]:
    """Get recent development sessions"""
    try:
        await init_database()
        project = await load_project_state(project_name)

        # Sort sessions by start time (most recent first)
        sorted_sessions = sorted(
            project.sessions,
            key=lambda s: s.start_time,
            reverse=True
        )

        # Limit results
        sessions_data = []
        for session in sorted_sessions[:limit]:
            duration = None
            if session.end_time:
                duration = str(session.end_time - session.start_time)
            else:
                duration = str(datetime.now() - session.start_time) + " (ongoing)"

            sessions_data.append({
                "session_id": session.session_id,
                "start_time": session.start_time.isoformat(),
                "end_time": session.end_time.isoformat() if session.end_time else None,
                "duration": duration,
                "actions_count": len(session.actions_taken),
                "tools_worked_on": session.tools_worked_on,
                "is_active": session.end_time is None,
                "notes": session.notes
            })

        # Calculate summary statistics
        total_sessions = len(project.sessions)
        active_sessions = len([s for s in project.sessions if s.end_time is None])

        return {
            "success": True,
            "sessions": sessions_data,
            "total_sessions": total_sessions,
            "active_sessions": active_sessions,
            "showing": len(sessions_data)
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


async def get_session_analytics(
    project_name: str = "default",
    days: int = 7
) -> Dict[str, Any]:
    """Get development analytics for the past N days"""
    try:
        await init_database()
        project = await load_project_state(project_name)

        # Calculate analytics for the specified period
        from datetime import datetime, timedelta
        cutoff_date = datetime.now() - timedelta(days=days)

        # Filter sessions within the time period
        recent_sessions = [
            s for s in project.sessions 
            if s.start_time >= cutoff_date
        ]

        # Calculate statistics
        total_sessions = len(recent_sessions)
        active_sessions = len([s for s in recent_sessions if s.end_time is None])
        completed_sessions = total_sessions - active_sessions

        # Calculate total development time
        total_time = timedelta()
        for session in recent_sessions:
            if session.end_time:
                total_time += session.end_time - session.start_time
            else:
                total_time += datetime.now() - session.start_time

        # Tools worked on
        tools_worked_on = set()
        for session in recent_sessions:
            tools_worked_on.update(session.tools_worked_on)

        # Daily activity
        daily_activity = {}
        for session in recent_sessions:
            day = session.start_time.date().isoformat()
            if day not in daily_activity:
                daily_activity[day] = 0
            daily_activity[day] += 1

        return {
            "success": True,
            "analytics": {
                "period_days": days,
                "total_sessions": total_sessions,
                "active_sessions": active_sessions,
                "completed_sessions": completed_sessions,
                "total_development_time": str(total_time),
                "tools_worked_on": list(tools_worked_on),
                "daily_activity": daily_activity,
                "average_session_length": str(total_time / max(completed_sessions, 1)) if completed_sessions > 0 else "0:00:00"
            }
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"Error getting session analytics: {str(e)}"
        }


def _generate_session_summary(session: DevelopmentSession) -> str:
    """Generate a summary of the development session"""
    summary_parts = []

    if session.tools_worked_on:
        summary_parts.append(f"Worked on {len(session.tools_worked_on)} tools: {', '.join(session.tools_worked_on)}")

    if session.actions_taken:
        summary_parts.append(f"Completed {len(session.actions_taken)} actions")

    if session.end_time:
        duration = session.end_time - session.start_time
        summary_parts.append(f"Session lasted {duration}")

    return ". ".join(summary_parts) + "." if summary_parts else "No specific activities recorded."


def register_tracking_tools(mcp: FastMCP):
    """Register tracking tools with FastMCP"""

    @mcp.tool()
    async def track_development_session_tool(
        action: str,
        project_name: str = "default",
        tool_name: str = "",
        notes: str = "",
        session_id: str = ""
    ) -> Dict[str, Any]:
        """Log development activities and track sessions

        Args:
            action: Description of the action taken
            project_name: Name of the project being worked on
            tool_name: Name of the tool being worked on (optional)
            notes: Additional notes about the work (optional)
            session_id: ID of existing session to continue (optional)

        Returns:
            Dict with session tracking information
        """
        return await track_development_session(action, project_name, tool_name, notes, session_id)

    @mcp.tool()
    async def end_development_session_tool(
        session_id: str,
        project_name: str = "default"
    ) -> Dict[str, Any]:
        """End a development session

        Args:
            session_id: ID of the session to end
            project_name: Name of the project

        Returns:
            Dict with session summary
        """
        return await end_development_session(session_id, project_name)

    @mcp.tool()
    async def get_development_sessions_tool(
        project_name: str = "default",
        limit: int = 10
    ) -> Dict[str, Any]:
        """Get recent development sessions

        Args:
            project_name: Name of the project
            limit: Maximum number of sessions to return

        Returns:
            Dict with list of recent sessions
        """
        return await get_development_sessions_list(project_name, limit)

    @mcp.tool()
    async def get_session_analytics_tool(
        project_name: str = "default",
        days: int = 7
    ) -> Dict[str, Any]:
        """Get development analytics for the past N days

        Args:
            project_name: Name of the project
            days: Number of days to analyze (default: 7)

        Returns:
            Dict with development analytics
        """
        return await get_session_analytics(project_name, days)