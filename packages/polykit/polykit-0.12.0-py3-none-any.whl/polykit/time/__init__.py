"""Stop wrestling with datetime formatting. Polykit's **Time** utilities handle everything from parsing to timezone-aware logging:

```python
from polykit.time import PolyTime

# Parse human-friendly time expressions
meeting = Time.parse("3pm tomorrow")
deadline = Time.parse("Friday at 5")

# Format datetimes in a natural way
print(Time.get_pretty_time(meeting))  # "tomorrow at 3:00 PM"
print(Time.get_pretty_time(deadline))  # "Friday at 5:00 PM"

# Convert durations to readable text
print(Time.convert_sec_to_interval(3725))  # "1 hour, 2 minutes and 5 seconds"
```

### Why These Utilities Make Development Nicer

- **Human-Readable Times**: Parse and format dates and times in natural language.
- **Timezone Intelligence**: Automatic timezone detection and handling.

These utilities solve real-world time challenges and have been hardened against some of the nastiest edge cases.
"""  # noqa: D212, D415, W505

from __future__ import annotations

from .polytime import (
    TZ,
    PolyTime,
    TimeZoneManager,
    get_capitalized_time,
    get_pretty_time,
    get_time_only,
    get_weekday_time,
)
