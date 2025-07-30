"""Stop wrestling with text manipulation and datetime formatting. Polykit's **Text** and **Time** utilities handle everything from pluralization to timezone-aware parsing:

### Text: Powerful Text Formatting and Manipulation

```python
from polykit.text import Text

# Smart pluralization that just works
print(f"Found {Text.plural('file', 5, with_count=True)}")  # "Found 5 files"
print(f"Processing {Text.plural('class', 1, with_count=True)}")  # "Processing 1 class"

# Intelligent truncation with context preservation
long_text = "This is a very long text that needs to be shortened while preserving meaning..."
print(Text.truncate(long_text, chars=50))  # Ends at sentence or word boundary
print(Text.truncate(long_text, from_middle=True))  # Preserves start and end

# Terminal colors made simple
Text.print_color("Success!", color="green", style=["bold"])
Text.print_color("Warning!", color="yellow")
Text.print_color("Error!", color="red", style=["bold", "underline"])

# Battle-tested message splitting that handles even the trickiest edge cases
parts = Text.split_message(long_markdown, max_length=4096)  # Handles the toughest code blocks!
for part in parts:
    send_message(part)  # Perfect for APIs with message length limits
```

### Time: Human-Friendly Datetime Handling

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

- **Battle-Tested Reliability**: The message splitting function alone represents nearly a year of refinement through production use. It can survive almost anything—and it has.
- **Edge Case Mastery**: Handles even the most problematic scenarios like nested code blocks and special characters.
- **No More Pluralization Bugs**: Automatically handle singular/plural forms for cleaner messages.
- **Smart Text Handling**: Truncate, format, and manipulate text with intelligent defaults.
- **Human-Readable Times**: Parse and format dates and times in natural language.
- **Timezone Intelligence**: Automatic timezone detection and handling.

These utilities solve real-world text and time challenges and have been hardened against some of the nastiest edge cases. My message splitting function alone represents nearly a year of refinement to handle every quirk of Markdown parsing that you really don't want to deal with—and now you don't have to!
"""  # noqa: D212, D415, W505

from __future__ import annotations

from .text import Text
from .time import (
    TZ,
    Time,
    TimeZoneManager,
    get_capitalized_time,
    get_pretty_time,
    get_time_only,
    get_weekday_time,
)

color = Text.color
print_color = Text.print_color
