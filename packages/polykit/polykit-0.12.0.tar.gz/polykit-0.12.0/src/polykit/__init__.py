"""Every developer has a collection of utilities they've refined over the years. Polykit is mine.

"*Another* utility library?" I can already hear you rolling your eyes. But don't close the tab yet! What sets Polykit apart isn't just the functionality but the thought behind each implementation. These are tools born from solving real-world problems, used in production but refined as passion.

If you're managing environment variables, handling paths across different operating systems, formatting text for human consumption, building command-line interfaces, or just want a *really* nice logger, Polykit provides elegant solutions that just work, often in ways you didn't realize you needed until you experience them.

Polykit doesn't try to be everything to everyone. Instead, it focuses on doing common tasks extraordinarily well, with an emphasis on developer happiness and code that's a pleasure to use.

## Why Polykit?

When you use Polykit, you're benefiting from:

- **Reliability** that comes from components used in real production environments.
- **Developer-centric design** that prioritizes clean APIs and intuitive interfaces.
- **Attention to edge cases** that others often overlook or ignore.
- **Consistent design philosophy** across all components for a cohesive experience.
- **Modern Python practices** including comprehensive type hints and up-to-date language features.

Everything you see here was created to solve genuine problems in day-to-day development, so it prioritizes developer experience with IDE-friendly interfaces, meaningful error messages, sensible defaults, and comprehensive (if still evolving) documentation. Every detail has been considered from the perspective of the person who will actually use these tools (because that person was me!).

Polykit strives to be intuitive, handle complexity behind clean interfaces, and integrate seamlessly with each other and your existing code. It's a toolkit from a developer who refuses to accept "good enough" and always goes for "really f*cking good." And the work is never finished—Polykit is still being actively developed, with tools being added and refined on a regular basis.

I'd love it if you gave Polykit a try, and I'd love even more if it helps you like it's helped me! If you're ready to bring some joy to your Python development, you know the way:

```bash
pip install polykit
```

## Features

Here's some of what Polykit has to offer:

### [`PolyLog`](https://github.com/dannystewart/polykit/tree/main/src/polykit/log): Beautiful, Context-Aware Logging

`PolyLog` is more than just another boring, hard-to-configure logger—it makes your application's internal dialogue clear and informative, and it looks beautiful doing it. It's the first thing I add to any new project.

- **Context-Aware**: Automatically detects caller class and module names.
- **Time-Intelligent**: Formats datetime objects into human-readable strings.
- **Visually Distinct**: Color-coded by log level for instant visual priority assessment.
- **Configurable**: From minimalist to detailed logging formats with a single parameter.
- **Production-Ready**: Rotating file handlers, thread safety, and proper log level management.

```python
# Create a smart, context-aware logger
logger = PolyLog.get_logger()  # Automatically detects class/module name!

# Datetime objects automatically formatted into human-readable text
logger.info("Next maintenance scheduled for %s.", datetime.now() + timedelta(days=7))
# Output: "Next maintenance scheduled for next Tuesday at 3:45 PM"

# Elegant error handling with context managers
with PolyLog.catch(logger, "Failed during data processing"):
    process_complex_data()  # Any exceptions are beautifully logged
```

### [`PolyEnv`](https://github.com/dannystewart/polykit/tree/main/src/polykit/env): Demystify Environment Variables

Environment variables shouldn't be a source of confusion and frustration, which is why I wrote `PolyEnv`—to make them a clear, declarative part of your application.

- **Hierarchical Loading**: Automatically loads from multiple `.env` files with smart precedence rules.
- **Type Conversion**: Transforms environment strings to Python types (`int`, `bool`, etc.) automatically.
- **Attribute Access**: Clean `env.VARIABLE_NAME` syntax with customizable attribute names for easy access.
- **Validation**: Ensure all required variables are present before your app runs.
- **Secret Protection**: Mask sensitive values in logs and debug output.

```python
env = PolyEnv()

# Declare your configuration needs
env.add_var("API_KEY", required=True, secret=True)
env.add_var("MAX_CONNECTIONS", default="10", var_type=int)
env.add_bool("ENABLE_CACHE", default=True)
env.add_var("UPLOAD_DIR", default="/tmp/uploads")

# Access variables with clean, IDE-friendly syntax
max_conn = env.MAX_CONNECTIONS  # Automatically converted to int
if env.ENABLE_CACHE:
    cache_dir = Path(env.UPLOAD_DIR) / "cache"

# Validate all variables at once on startup
try:
    env.validate_all()
    print("Environment configured correctly!")
except ValueError as e:
    print(f"Configuration error: {e}")
```

### [`PolyPath`](https://github.com/dannystewart/polykit/tree/main/src/polykit/paths): Navigate File Systems with Confidence

`PolyPath` brings sanity to file management and eliminates an entire class of cross-platform headaches:

- **User Directory Integration**: Seamless access to Documents, Downloads, Pictures and more.
- **Clean, Intuitive API**: Methods like `from_config()` and `from_cache()` make code self-documenting.
- **macOS App Domain Support**: Proper bundle identifiers (com.developer.appname) for macOS conventions.

```python
paths = PolyPath("my_awesome_app", app_author="YourName")

# Access platform-specific directories with a consistent API
config_file = paths.from_config("settings.json")  # ~/.config/my_awesome_app/settings.json on Linux
cache_dir = paths.from_cache(
    "api_responses"
)  # ~/Library/Caches/my_awesome_app/api_responses on macOS
log_path = paths.from_log("debug.log")  # Appropriate log location on any platform

# Work with user directories naturally
docs = paths.from_documents("Reports", "2023")  # ~/Documents/Reports/2025
music = paths.from_music("Playlists")  # ~/Music/Playlists
downloads = paths.from_downloads("temp.zip")  # ~/Downloads/temp.zip
```

### [`PolyFile`](https://github.com/dannystewart/polykit/blob/main/src/polykit/files/polyfile.py): File Operations Simplified

`PolyFile` brings elegance and safety to everyday file operations:

- **Intuitive Class Methods**: Access functionality through clean, descriptive methods without instantiation.
- **Delete to Trash**: Files go to the recycle bin instead of disappearing forever.
- **Natural Sorting**: "file10.txt" come after "file2.txt", not before.
- **Smart Filtering**: Combine extension filters, exclusion patterns, and recursion options.
- **Duplicate Detection**: Find identical files with efficient SHA-256 hashing.

```python
# Find files with smart filtering and natural sorting
image_files = PolyFile.list(
    Path("~/Pictures"),
    extensions=["jpg", "png"],
    recursive=True,
    exclude=["*thumbnail*"],
    hidden=False,
)

# Safe deletion with trash bin support
deleted, failed = PolyFile.delete(outdated_files, logger=logger)

# Copy with overwrite protection
PolyFile.copy(source_file, destination, overwrite=False)

# Find and manage duplicate files
dupes = PolyFile.find_dupes_by_hash(files)
for hash_value, file_list in dupes.items():
    # Keep the first file, delete the rest
    PolyFile.delete(file_list[1:])
```

### [`PolyDiff`](https://github.com/dannystewart/polykit/blob/main/src/polykit/files/polydiff.py): Elegant File Comparison

`PolyDiff` makes text and file comparison clean and intuitive:

- **Visual Clarity**: Color-coded output makes changes immediately apparent.
- **Multiple Output Styles**: Choose between colored, simple, or minimal output formats.
- **Structured Results**: Get programmatic access to additions, deletions, and full changes.
- **Context-Aware**: Includes filenames and surrounding lines for better understanding.

```python
# Compare two files with colorized output
result = PolyDiff.files(Path("config_old.json"), Path("config_new.json"), style=DiffStyle.COLORED)

# Compare strings with context
changes = PolyDiff.content(old_text, new_text, filename="user_profile.json")

# Analyze the changes programmatically
if changes.has_changes:
    print(f"Found {len(changes.additions)} additions and {len(changes.deletions)} deletions")

    # Access specific changes
    for added_line in changes.additions:
        process(added_line)
```

### [`PolyArgs`](https://github.com/dannystewart/polykit/blob/main/src/polykit/cli/polyargs.py): Command-Line Interfaces That Look Professional

`PolyArgs` transforms the standard `argparse` experience into something you'll actually enjoy:

- **Built Around `argparse`:** No need to learn new methods or adapt your existing implementation. `PolyArgs` is a drop-in replacement.
- **Write Once, Use Twice**: Maintain comprehensive module documentation while keeping help text concise with `lines=1` to include a set number of paragraphs with formatting preserved.
- **Intelligent Column Widths**: Automatically calculates optimal formatting based on your arguments.
- **Version Integration**: Automatically adds `--version` that reports detailed package information.

```python
# Only the first paragraph appears in help text!
parser = PolyArgs(description=__doc__, lines=1)

# Add arguments with automatic formatting
parser.add_argument("--input", "-i", help="Input file path")
parser.add_argument("--output", "-o", help="Output file path")
parser.add_argument("--verbose", "-v", action="store_true", help="Enable detailed output")

args = parser.parse_args()
```

### [`VersionChecker`](https://github.com/dannystewart/polykit/blob/main/src/polykit/packages/packages.py): Package Version Intelligence

`VersionChecker` gives you visibility into your dependencies—what's installed, where it came from, and what updates are available.

- **Multi-Source Intelligence**: Check versions against PyPI, GitHub, GitLab, or any Git repository.
- **Dev Environment Awareness**: Detects when you're running from source or in editable mode.
- **Smart Package Detection**: Determine package names from running scripts and entry points.
- **Rich Version Information**: Get structured data about versions, sources, and update status.

```python
# Quick version check with smart detection
checker = VersionChecker()
info = checker.check_package("requests")

print(info)  # "requests v2.28.1 (pypi)"

# Check for updates against PyPI (or GitHub, or anything else)
if info.update_available:
    print(f"Update available: v{info.latest}")

# Detect development installations
if checker.is_development_version("my_package"):
    print("Using development version")

# Automatic package detection for CLI tools
current_package = VersionChecker.get_caller_package_name()
```

### [`Text`](https://github.com/dannystewart/polykit/blob/main/src/polykit/formatters/text.py) and [`Time`](https://github.com/dannystewart/polykit/blob/main/src/polykit/formatters/time.py): The Swiss Army Knives of Formatting

Polykit's `Text` and `Time` utility classes handle everything from pluralization to timezone-aware parsing, solving real-world text and time challenges and hardened against some of the nastiest edge cases.

- **Smart Text Handling**: Truncate, format, and manipulate text with intelligent defaults.
- **Edge Case Mastery**: Handles tricky scenarios like nested code blocks and special characters with grace and reliability.
- **Human-Readable Times**: Parse and format dates and times in natural language.
- **Battle-Tested**: The `split_message()` function alone represents nearly a year of refinement through production use. It can survive almost anything—and it has.

```python
# Smart pluralization that just works
print(f"Found {Text.plural('file', 5, with_count=True)}")  # "Found 5 files"
print(f"Processing {Text.plural('class', 1, with_count=True)}")  # "Processing 1 class"

# Intelligent truncation with context preservation
print(Text.truncate(long_text, chars=50))  # Ends at sentence or word boundary
print(Text.truncate(long_text, from_middle=True))  # Preserves start and end

# Terminal colors made simple
Text.print_color("Success!", color="green", style=["bold"])
Text.print_color("Error!", color="red", style=["bold", "underline"])

# Parse human-friendly time expressions
meeting = Time.parse("3pm tomorrow")
deadline = Time.parse("Friday at 5")

# Format datetimes in a natural way
print(Time.get_pretty_time(meeting))  # "tomorrow at 3:00 PM"
print(Time.get_pretty_time(deadline))  # "Friday at 5:00 PM"

# Convert durations to readable text
print(Time.convert_sec_to_interval(3725))  # "1 hour, 2 minutes and 5 seconds"
```

Why spend months solving these problems when somebody else has put in the time (lots and lots of time) solving them for you?

### Honorable Mention

Polykit also has a few more tricks up its sleeve for common development challenges.

#### [`Singleton`](https://github.com/dannystewart/polykit/blob/main/src/polykit/core/singleton.py) Metaclass

Singletons are deceptively difficult to implement correctly, but `Singleton` handles it all:

- **Truly Thread-Safe**: Properly handles race conditions during instantiation with class-level locks.
- **No Boilerplate**: Implement the pattern with a single metaclass declaration.
- **IDE-Friendly**: Designed to preserve method visibility and code intelligence in IDEs.
- **Type-Hinting Compatible**: Works seamlessly with static type checkers and modern Python typing.

#### And even more:

- Gracefully handle keyboard interrupts with the `@handle_interrupt()` decorator.
- Auto-retry operations that might fail transiently with the `@retry_on_exception()` decorator.
- Check permissions with `is_root_user()` and elevate with `acquire_sudo()` if needed.
- Get user confirmation with a single keypress using `confirm_action()`.
- Use stylish loading indicators like spinners with the `with_spinner()` context manager…
- …or use Walking Man `<('-'<)` (honestly, he alone is worth the download).

## License

Polykit is licensed under the [LGPL-3.0 license](https://github.com/dannystewart/polykit/blob/main/LICENSE). Contributions and feedback are welcome!
"""  # noqa: D212, D415, W505

from __future__ import annotations

from .cli.polyargs import PolyArgs
from .env.polyenv import PolyEnv
from .files.polyfile import PolyFile
from .formatters import Text, Time
from .log.polylog import PolyLog
from .paths.polypath import PolyPath
from .text import PolyColors, PolyMoji, PolyNumbers, PolySplit, PolyText, PolyTruncate
from .time import TZ, PolyTime
