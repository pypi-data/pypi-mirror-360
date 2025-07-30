"""
SQLite storage optimized for MCP project intelligence
"""

import json
import sqlite3
import aiosqlite
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from .models import ProjectState, Tool, DevelopmentSession, ToolStatus


# Storage configuration
STORAGE_DIR = Path.home() / ".mcp4mcp"
DB_PATH = STORAGE_DIR / "projects.db"


async def init_database() -> None:
    """Create tables for projects, tools, sessions"""
    STORAGE_DIR.mkdir(exist_ok=True)
    
    async with aiosqlite.connect(DB_PATH) as db:
        # Projects table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                name TEXT PRIMARY KEY,
                description TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        """)
        
        # Tools table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS tools (
                name TEXT,
                project_name TEXT,
                description TEXT,
                status TEXT,
                file_path TEXT,
                function_name TEXT,
                parameters TEXT,
                return_type TEXT,
                created_at TEXT,
                updated_at TEXT,
                similarity_scores TEXT,
                PRIMARY KEY (name, project_name),
                FOREIGN KEY (project_name) REFERENCES projects (name)
            )
        """)
        
        # Sessions table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                project_name TEXT,
                start_time TEXT,
                end_time TEXT,
                tools_worked_on TEXT,
                actions_taken TEXT,
                notes TEXT,
                FOREIGN KEY (project_name) REFERENCES projects (name)
            )
        """)
        
        await db.commit()


async def load_project_state(project_name: str = "default") -> ProjectState:
    """Load project with efficient joins"""
    await init_database()
    
    async with aiosqlite.connect(DB_PATH) as db:
        # Load project
        cursor = await db.execute(
            "SELECT * FROM projects WHERE name = ?", (project_name,)
        )
        project_row = await cursor.fetchone()
        
        if not project_row:
            # Create new project
            project = ProjectState(name=project_name)
            await save_project_state(project)
            return project
        
        # Load tools
        cursor = await db.execute(
            "SELECT * FROM tools WHERE project_name = ?", (project_name,)
        )
        tool_rows = await cursor.fetchall()
        
        tools = {}
        for row in tool_rows:
            tool = Tool(
                name=row[0],
                description=row[2],
                status=ToolStatus(row[3]),
                file_path=row[4],
                function_name=row[5],
                parameters=json.loads(row[6]) if row[6] else [],
                return_type=row[7],
                created_at=datetime.fromisoformat(row[8]),
                updated_at=datetime.fromisoformat(row[9]),
                similarity_scores=json.loads(row[10]) if row[10] else {}
            )
            tools[tool.name] = tool
        
        # Load sessions
        cursor = await db.execute(
            "SELECT * FROM sessions WHERE project_name = ?", (project_name,)
        )
        session_rows = await cursor.fetchall()
        
        sessions = []
        for row in session_rows:
            session = DevelopmentSession(
                session_id=row[0],
                project_name=row[1],
                start_time=datetime.fromisoformat(row[2]),
                end_time=datetime.fromisoformat(row[3]) if row[3] else None,
                tools_worked_on=json.loads(row[4]) if row[4] else [],
                actions_taken=json.loads(row[5]) if row[5] else [],
                notes=row[6] or ""
            )
            sessions.append(session)
        
        return ProjectState(
            name=project_row[0],
            description=project_row[1],
            tools=tools,
            sessions=sessions,
            created_at=datetime.fromisoformat(project_row[2]),
            updated_at=datetime.fromisoformat(project_row[3])
        )


async def save_project_state(project: ProjectState) -> None:
    """Atomic updates with transactions"""
    await init_database()
    
    async with aiosqlite.connect(DB_PATH) as db:
        # Save project
        await db.execute("""
            INSERT OR REPLACE INTO projects (name, description, created_at, updated_at)
            VALUES (?, ?, ?, ?)
        """, (
            project.name,
            project.description,
            project.created_at.isoformat(),
            project.updated_at.isoformat()
        ))
        
        # Clear existing tools and sessions for this project
        await db.execute("DELETE FROM tools WHERE project_name = ?", (project.name,))
        await db.execute("DELETE FROM sessions WHERE project_name = ?", (project.name,))
        
        # Save tools
        for tool in project.tools.values():
            await db.execute("""
                INSERT INTO tools (
                    name, project_name, description, status, file_path, function_name,
                    parameters, return_type, created_at, updated_at, similarity_scores
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                tool.name,
                project.name,
                tool.description,
                tool.status.value,
                tool.file_path,
                tool.function_name,
                json.dumps(tool.parameters),
                tool.return_type,
                tool.created_at.isoformat(),
                tool.updated_at.isoformat(),
                json.dumps(tool.similarity_scores)
            ))
        
        # Save sessions
        for session in project.sessions:
            await db.execute("""
                INSERT INTO sessions (
                    session_id, project_name, start_time, end_time,
                    tools_worked_on, actions_taken, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                session.session_id,
                session.project_name,
                session.start_time.isoformat(),
                session.end_time.isoformat() if session.end_time else None,
                json.dumps(session.tools_worked_on),
                json.dumps(session.actions_taken),
                session.notes
            ))
        
        await db.commit()


async def find_similar_tools_db(tool_name: str, tool_description: str, project_name: str = "default", threshold: float = 0.7) -> List[Tool]:
    """Fast similarity queries across all projects"""
    await init_database()
    
    # Create a temporary tool for comparison
    temp_tool = Tool(
        name=tool_name,
        description=tool_description,
        status=ToolStatus.PLANNED
    )
    
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            SELECT * FROM tools 
            WHERE project_name = ? AND name != ?
        """, (project_name, tool_name))
        
        rows = await cursor.fetchall()
        similar_tools = []
        
        # Import here to avoid circular imports
        from .analyzers.similarity import ToolSimilarityAnalyzer
        analyzer = ToolSimilarityAnalyzer(threshold)
        
        for row in rows:
            # Create tool from database row
            db_tool = Tool(
                name=row[0],
                description=row[2],
                status=ToolStatus(row[3]),
                file_path=row[4],
                function_name=row[5],
                parameters=json.loads(row[6]) if row[6] else [],
                return_type=row[7],
                created_at=datetime.fromisoformat(row[8]),
                updated_at=datetime.fromisoformat(row[9]),
                similarity_scores=json.loads(row[10]) if row[10] else {}
            )
            
            # Calculate similarity
            similarity = analyzer.calculate_similarity(temp_tool, db_tool)
            
            if similarity >= threshold:
                # Update similarity score
                db_tool.similarity_scores[tool_name] = similarity
                similar_tools.append(db_tool)
        
        return similar_tools


async def get_development_sessions(project_name: str = "default", limit: int = 10) -> List[DevelopmentSession]:
    """Get development sessions for a project"""
    await init_database()
    
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            SELECT * FROM sessions 
            WHERE project_name = ? 
            ORDER BY start_time DESC 
            LIMIT ?
        """, (project_name, limit))
        
        rows = await cursor.fetchall()
        sessions = []
        
        for row in rows:
            session = DevelopmentSession(
                session_id=row[0],
                project_name=row[1],
                start_time=datetime.fromisoformat(row[2]),
                end_time=datetime.fromisoformat(row[3]) if row[3] else None,
                tools_worked_on=json.loads(row[4]) if row[4] else [],
                actions_taken=json.loads(row[5]) if row[5] else [],
                notes=row[6] or ""
            )
            sessions.append(session)
        
        return sessions


async def list_all_projects() -> List[str]:
    """Get list of all project names"""
    await init_database()
    
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT name FROM projects")
        rows = await cursor.fetchall()
        return [row[0] for row in rows]