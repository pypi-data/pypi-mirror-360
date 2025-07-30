"""Managing package versions shouldn't require detective work. **VersionChecker** gives you complete visibility into your Python dependencies:

```python
from polykit.packages import VersionChecker, PackageSource

# Quick version check with smart detection
checker = VersionChecker()
info = checker.check_package("requests")

print(info)  # "requests v2.28.1 (pypi)"

# Check for updates against PyPI
if info.update_available:
    print(f"Update available: v{info.latest}")

# Check against GitHub releases
github_info = checker.check_package("fastapi", source=PackageSource.GITHUB, owner="tiangolo")

# Detect development installations
if checker.is_development_version("my_package"):
    print("Using development version")

# Automatic package detection for CLI tools
current_package = VersionChecker.get_caller_package_name()
version_info = checker.check_package(current_package)
```

### Why VersionChecker Is Indispensable

- **Multi-Source Intelligence**: Check versions against PyPI, GitHub, GitLab, or any Git repository.
- **Dev Environment Awareness**: Detects when you're running from source or in editable mode.
- **Update Awareness**: Easily compare installed versions against latest available releases.
- **Smart Package Detection**: Determine package names from running scripts and entry points.
- **Rich Version Information**: Get structured data about versions, sources, and update status.
- **Zero Configuration**: Works out-of-the-box with sensible defaults for most scenarios.
- **Seamless CLI Integration**: Perfect companion for PolyArgs' automatic version reporting.

VersionChecker removes the guesswork from package management, giving you precise information about what's installed, where it came from, and what updates are available.

"""  # noqa: D212, D415, W505

from __future__ import annotations

from .packages import VersionChecker
from .types import PackageSource, VersionInfo
