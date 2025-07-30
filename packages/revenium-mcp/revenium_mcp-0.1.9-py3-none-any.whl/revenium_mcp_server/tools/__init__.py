"""Tools package for extracted MCP tools.

This package contains tools that have been extracted from the main enhanced_server.py
for better organization and maintainability.
"""

# Import ReveniumTools from the top-level tools.py module to resolve naming conflict
import sys
from pathlib import Path

# Add parent directory to sys.path to import tools.py
parent_dir = Path(__file__).parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

try:
    # Import from tools.py file (not this tools/ package)
    import importlib.util
    tools_py_path = Path(__file__).parent.parent / "tools.py"
    spec = importlib.util.spec_from_file_location("tools_module", tools_py_path)
    tools_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tools_module)
    ReveniumTools = tools_module.ReveniumTools
except Exception as e:
    # Fallback - this should not happen but provides error info
    import warnings
    warnings.warn(f"Could not import ReveniumTools from tools.py: {e}")
    ReveniumTools = None

__all__ = ["ReveniumTools"]