"""Version information for marearts-xcolor package."""

import os
import re
from pathlib import Path


def get_version():
    """Extract version from pyproject.toml."""
    try:
        # Try to find pyproject.toml in parent directory
        current_dir = Path(__file__).parent
        pyproject_path = current_dir.parent / "pyproject.toml"
        
        if pyproject_path.exists():
            with open(pyproject_path, "r") as f:
                content = f.read()
                # Match version = "x.y.z" pattern
                match = re.search(r'version\s*=\s*"([^"]+)"', content)
                if match:
                    return match.group(1)
        
        # Fallback: try to get from package metadata
        try:
            from importlib.metadata import version
            return version("marearts-xcolor")
        except Exception:
            pass
            
    except Exception:
        pass
    
    # Default version if all else fails
    return "1.0.0"


__version__ = get_version()