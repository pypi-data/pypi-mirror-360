"""
Demo usage of mcp4mcp - Meta MCP Server

This script demonstrates how to use mcp4mcp to manage MCP development projects.
"""

import asyncio
import json
from pathlib import Path
from mcp4mcp.tools.state_management import get_project_state, update_project_state, scan_project_files
from mcp4mcp.tools.intelligence import check_before_build, suggest_next_action, analyze_tool_similarity
from mcp4mcp.tools.tracking import track_development_session, end_development_session
from mcp4mcp.storage import init_database


async def demo_basic_usage():
    """Demonstrate basic mcp4mcp usage"""
    print("\n=== mcp4mcp Demo - Basic Usage ===\n")

    # Initialize database
    await init_database()
    print("✓ Database initialized")

    # Start a development session
    session_result = await track_development_session(
        "Started demo session",
        "demo_project",
        "demo_tool",
        "Demonstrating mcp4mcp capabilities"
    )
    session_id = session_result["session_id"]
    print(f"✓ Started development session: {session_id}")

    # Update project state with some tools
    tools = [
        {
            "name": "file_reader",
            "description": "Read files from disk",
            "status": "planned"
        },
        {
            "name": "file_writer", 
            "description": "Write files to disk",
            "status": "implemented"
        },
        {
            "name": "calculator",
            "description": "Perform mathematical calculations",
            "status": "in_progress"
        }
    ]

    update_result = await update_project_state(
        "demo_project",
        "Demo project for testing mcp4mcp features",
        tools
    )
    print(f"✓ Updated project: {update_result['message']}")

    # Get current project state
    state_result = await get_project_state("demo_project")
    project = state_result["project"]
    print(f"✓ Project '{project['name']}' has {len(project['tools'])} tools")

    # Check before building a new tool
    check_result = await check_before_build(
        "file_processor",
        "Process files by reading and writing them",
        "demo_project"
    )
    print(f"✓ Checked for conflicts: {len(check_result['conflicts'])} potential conflicts found")

    # Analyze tool similarity
    similarity_result = await analyze_tool_similarity("demo_project", 0.6)
    print(f"✓ Analyzed similarity: {len(similarity_result['similar_pairs'])} similar pairs found")

    # Get AI suggestions
    suggestions_result = await suggest_next_action("demo_project", "Working on file operations")
    print(f"✓ Generated suggestions: {len(suggestions_result['suggestions'])} recommendations")

    # End the session
    end_result = await end_development_session(session_id, "demo_project")
    print(f"✓ Ended session: {end_result['duration']} seconds")

    print("\n=== Demo Complete ===")


async def demo_project_scanning():
    """Demonstrate project file scanning"""
    print("\n=== mcp4mcp Demo - Project Scanning ===\n")

    # Scan the example project
    example_project_path = Path(__file__).parent / "example_project"
    if example_project_path.exists():
        scan_result = await scan_project_files(
            "example_project",
            str(example_project_path)
        )
        print(f"✓ Scanned example project: {scan_result['tools_found']} tools found")

        # Get the updated project state
        state_result = await get_project_state("example_project")
        project = state_result["project"]

        print(f"✓ Example project tools:")
        for tool_name, tool_info in project["tools"].items():
            print(f"  - {tool_name}: {tool_info['description']}")
    else:
        print("⚠ Example project not found, skipping scan demo")


async def main():
    """Run all demos"""
    print("=== mcp4mcp Demonstration ===")
    print("This demo shows the capabilities of mcp4mcp - Meta MCP Server")

    try:
        await demo_basic_usage()
        await demo_project_scanning()

        print("\n✅ All demos completed successfully!")
        print("\nTo use mcp4mcp in your own projects:")
        print("1. python server.py - Start the MCP server")
        print("2. Use the provided tools in your MCP client")
        print("3. Track your development progress automatically")

    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())