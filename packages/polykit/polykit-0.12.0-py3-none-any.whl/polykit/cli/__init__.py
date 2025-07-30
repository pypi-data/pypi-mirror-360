"""Building command-line tools shouldn't require fighting with formatting. **PolyArgs** transforms the standard argparse experience into something you'll actually enjoy:

```python
from polykit.cli import PolyArgs

# Use your full module docstring but only show the first paragraph in help text

\"""Process and analyze data files with advanced filtering options.

This module provides tools for loading, filtering, and transforming data
from various file formats. It supports CSV, JSON, and XML inputs.

Examples:
    process.py --input data.csv --output results.json
    process.py --filter "created_at > 2023-01-01" --format pretty
\"""

# Only the first paragraph appears in help text!
parser = PolyArgs(description=__doc__, lines=1)

# Add arguments with automatic formatting
parser.add_argument("--input", "-i", help="Input file path")
parser.add_argument("--output", "-o", help="Output file path")
parser.add_argument("--verbose", "-v", action="store_true", help="Enable detailed output")

args = parser.parse_args()
```

### Why PolyArgs Makes Your CLI Tools Better

- **Smart Docstring Handling**: Use `lines=1` to show only the first paragraph of your docstring in help text.
- **Write Once, Use Twice**: Maintain comprehensive module documentation while keeping help text concise.
- **Intelligent Column Widths**: Automatically calculates optimal formatting based on your arguments.
- **Version Integration**: Automatically adds `--version` that reports detailed package information.
- **Consistent Text Formatting**: Help text with proper capitalization and paragraph structure.
- **Professional Output**: Help text that looks polished without tedious manual formatting.

PolyArgs solves the classic dilemma between comprehensive documentation and concise help screens—write detailed documentation in your docstring and control exactly how much appears in your command-line help.

### Elegant Error Handling

```python
from polykit.core import handle_interrupt, retry_on_exception

# Gracefully handle keyboard interrupts
@handle_interrupt(message="Download cancelled. Cleaning up...")
def download_large_files():
    # User can press Ctrl+C without seeing ugly traceback

# Auto-retry operations that might fail temporarily
@retry_on_exception(exception_to_check=ConnectionError, tries=3, backoff=2)
def fetch_remote_data():
    # Will retry up to 3 times with increasing delays
```

### Interactive CLI Helpers

```python
from polykit.cli import confirm_action, with_spinner, walking_man

# Get user confirmation with a single keypress
if confirm_action("Delete all temporary files?"):
    cleanup_files()

# Show progress with stylish spinners
@with_spinner("Processing data...", success="Data processed!")
def process_data():
    # Long-running operation with visual feedback

# Or use the charming Walking Man animation
with walking_man("Loading your files..."):
    # <('-'<) keeps users company during lengthy operations
```

### System Operations

```python
from polykit.shell import is_root_user, acquire_sudo
from polykit.core import Singleton

# Check permissions and elevate if needed
if not is_root_user() and not acquire_sudo():
    print("This operation requires admin privileges")

# Create thread-safe singleton classes with minimal code
class ConfigManager(metaclass=Singleton):
    \"""Configuration is loaded only once and shared throughout the app.\"""
```

### Development Tools

```python
from polykit.core import deprecated, not_yet_implemented
from polykit.shell import log_traceback

# Mark APIs for future removal
@deprecated("Use new_function() instead.")
def old_function():
    # Users get helpful warning when using this

# Placeholder for planned features
@not_yet_implemented("Coming in version 2.0")
def future_feature():
    # Raises clear error if accidentally called

# Colorized, formatted tracebacks
try:
    risky_operation()
except Exception:
    log_traceback()  # Pretty, syntax-highlighted traceback
```
"""  # noqa: D212, D415, W505

from __future__ import annotations

from .confirm import confirm_action, get_single_char_input
from .interrupt import async_handle_interrupt, async_with_handle_interrupt, handle_interrupt
from .permissions import acquire_sudo, is_root_user
from .polyargs import PolyArgs
from .progress import halo_progress, with_spinner
from .walking_man import WalkingMan, conditional_walking_man, walking_man
