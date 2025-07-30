"""
NoETL React UI Package

This package contains the built React UI components for the NoETL dashboard.
The UI is served by the FastAPI server and provides a web interface for
managing playbooks, workflows, and monitoring execution.
"""

import os
from pathlib import Path

# Get the UI package directory
UI_DIR = Path(__file__).parent

# Paths to UI assets
STATIC_DIR = UI_DIR / "static"
TEMPLATES_DIR = UI_DIR / "templates"

def get_static_dir():
    """Get the path to static assets directory."""
    return str(STATIC_DIR)

def get_templates_dir():
    """Get the path to templates directory."""
    return str(TEMPLATES_DIR)

def is_ui_available():
    """Check if UI assets are available."""
    return STATIC_DIR.exists() and TEMPLATES_DIR.exists()

__all__ = ['get_static_dir', 'get_templates_dir', 'is_ui_available']
