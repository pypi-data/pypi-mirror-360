"""## Singleton: Thread-Safety Without Compromise

```python
from polykit.core import Singleton

# Create a thread-safe singleton with a single line
class ConfigManager(metaclass=Singleton):
    \"""Configuration is loaded only once and shared throughout the app.\"""

    def __init__(self, config_path=None):
        # This runs only once, no matter how many times you instantiate
        self.load_config(config_path)

    def get_setting(self, key):
        return self.settings.get(key)

# Use it anywhere in your application
config1 = ConfigManager("/path/to/config")
config2 = ConfigManager()  # Different call, same instance

assert config1 is config2  # Always true
```

### Why This Singleton Implementation Stands Out

- **Truly Thread-Safe**: Properly handles race conditions during instantiation with class-level locks.
- **IDE-Friendly**: Carefully designed to preserve method visibility and code intelligence in IDEs.
- **Zero Boilerplate**: Implement the pattern with a single metaclass declaration.
- **Transparent Usage**: No special methods needed to access the singleton instance.
- **Type-Hinting Compatible**: Works seamlessly with static type checkers and modern Python typing.

Singletons are deceptively difficult to implement correctly. This implementation represents significant thought and refinement to solve the common pitfalls—from thread-safety issues to IDE integration challenges—giving you a reliable pattern you can apply consistently across your projects.
"""  # noqa: D212, D415, W505

from __future__ import annotations

from .decorators import async_retry_on_exception, retry_on_exception, with_retries
from .detect import platform_check
from .is_literal import is_literal
from .setup import polykit_setup
from .singleton import Singleton
from .traceback import log_traceback
