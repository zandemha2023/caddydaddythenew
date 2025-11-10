#!/usr/bin/env python3
"""Validate all imports and basic functionality."""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

def test_imports():
    """Test all critical imports."""
    print("=" * 60)
    print("Theo CAD - Import Validation")
    print("=" * 60)
    print()

    tests_passed = 0
    tests_failed = 0

    # Test 1: Core imports
    print("Test 1: Core dependencies")
    try:
        import fastapi
        import uvicorn
        import anthropic
        import sqlalchemy
        import redis
        import structlog
        import cadquery as cq
        print(f"  ✓ FastAPI {fastapi.__version__}")
        print(f"  ✓ Anthropic {anthropic.__version__}")
        print(f"  ✓ SQLAlchemy {sqlalchemy.__version__}")
        print(f"  ✓ CadQuery {cq.__version__}")
        print(f"  ✓ All core dependencies imported")
        tests_passed += 1
    except ImportError as e:
        print(f"  ✗ Import failed: {e}")
        tests_failed += 1
    print()

    # Test 2: Application modules
    print("Test 2: Application modules")
    try:
        from app.main import app
        from app.core.config import settings
        from app.db.base import get_db
        print("  ✓ Main application")
        print("  ✓ Configuration")
        print("  ✓ Database")
        tests_passed += 1
    except ImportError as e:
        print(f"  ✗ Import failed: {e}")
        tests_failed += 1
    print()

    # Test 3: Agent modules
    print("Test 3: Agent modules")
    try:
        from app.services.agents.base_agent import BaseAgent
        from app.services.agents.requirements_agent_v2 import RequirementsAgentV2
        from app.services.agents.cad_agent_v2 import CADAgentV2
        from app.services.agents.design_orchestrator import DesignOrchestrator
        print("  ✓ Base Agent")
        print("  ✓ Requirements Agent V2")
        print("  ✓ CAD Agent V2")
        print("  ✓ Design Orchestrator")
        tests_passed += 1
    except ImportError as e:
        print(f"  ✗ Import failed: {e}")
        tests_failed += 1
    print()

    # Test 4: API endpoints
    print("Test 4: API endpoints")
    try:
        from app.api.endpoints import design, health, cad
        from app.api.websockets.agent_stream import agent_stream_manager
        print("  ✓ Design endpoints")
        print("  ✓ Health endpoints")
        print("  ✓ CAD endpoints")
        print("  ✓ WebSocket manager")
        tests_passed += 1
    except ImportError as e:
        print(f"  ✗ Import failed: {e}")
        tests_failed += 1
    print()

    # Test 5: Database models
    print("Test 5: Database models")
    try:
        from app.models.design import Design, DesignVersion
        from app.models.cad_file import CADFile
        from app.models.project import Project
        from app.models.user import User
        print("  ✓ Design models")
        print("  ✓ CAD file models")
        print("  ✓ Project models")
        print("  ✓ User models")
        tests_passed += 1
    except ImportError as e:
        print(f"  ✗ Import failed: {e}")
        tests_failed += 1
    print()

    # Test 6: CadQuery functionality
    print("Test 6: CadQuery functionality")
    try:
        import cadquery as cq

        # Create a simple test object
        result = cq.Workplane("XY").box(10, 10, 10)

        # Verify it's a valid CadQuery object
        assert result is not None
        print("  ✓ CadQuery basic operations work")
        print("  ✓ Can create simple geometry")
        tests_passed += 1
    except Exception as e:
        print(f"  ✗ CadQuery test failed: {e}")
        tests_failed += 1
    print()

    # Summary
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Tests passed: {tests_passed}")
    print(f"Tests failed: {tests_failed}")
    print()

    if tests_failed == 0:
        print("✓ All tests passed! System is ready.")
        print()
        print("Next steps:")
        print("  1. Ensure PostgreSQL is running")
        print("  2. Ensure Redis is running")
        print("  3. Set ANTHROPIC_API_KEY in .env")
        print("  4. Run: uvicorn app.main:app --reload")
        print("=" * 60)
        return 0
    else:
        print("✗ Some tests failed. Please fix the issues above.")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(test_imports())
