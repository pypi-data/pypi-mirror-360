"""Stop writing the same file handling code in every project. **PolyFile** brings elegance and safety to everyday file operations:

```python
from polykit.files import PolyFile
from pathlib import Path

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

### Why PolyFile Makes Development Nicer

- **Intuitive Class Methods**: Access functionality through clean, descriptive methods without instantiation.
- **Consistent Interface**: Every operation follows the same pattern—clear method names that do exactly what they say.
- **Stateless Design**: No need to manage object lifecycles or worry about maintaining state.
- **Trash-Aware Deletion**: Files go to the recycle bin instead of disappearing forever.
- **Natural Sorting**: "file10.txt" come after "file2.txt", not before.
- **Smart Filtering**: Combine extension filters, exclusion patterns, and recursion options.
- **Duplicate Detection**: Find identical files with efficient SHA-256 hashing.
- **Timestamp Management**: Easily compare and manipulate file timestamps.
- **Overwrite Protection**: Prevent accidental data loss with built-in safeguards.
- **Logger Integration**: All operations can report their status through your logging system (which is hopefully PolyLog!).

PolyFile handles the tedious details of file management so you can focus on your application's core functionality.

## PolyDiff: Elegant File Comparison

Comparing files and visualizing differences shouldn't require external tools or complex code. PolyDiff makes file comparison clean and intuitive:

```python
from polykit.files import PolyDiff
from pathlib import Path

# Compare two files with colorized output
result = PolyDiff.files(Path("config_old.json"), Path("config_new.json"), style=DiffStyle.COLORED)

# Compare strings with context
changes = PolyDiff.content(old_text, new_text, filename="user_profile.json")

# Analyze the changes programmatically
if changes.has_changes:
    print(f"Found {len(changes.additions)} additions and {len(changes.deletions)} deletions")

    # Access specific changes
    for added_line in changes.additions:
        process_new_content(added_line)
```

### Why PolyDiff Stands Out

- **Visual Clarity**: Color-coded output makes changes immediately apparent.
- **Multiple Output Styles**: Choose between colored, simple, or minimal output formats.
- **Structured Results**: Get programmatic access to additions, deletions, and full changes.
- **Content or File Comparison**: Compare files directly or arbitrary text content.
- **Context-Aware**: Includes filenames and surrounding lines for better understanding.
- **Logger Integration**: Output changes through your existing logging system (and you know which to use).
- **Clean Formatting**: Consistent spacing and alignment for better readability.

PolyDiff brings the power of unified diff to your Python applications with an API that's both powerful and pleasant to use.
"""  # noqa: D212, D415, W505

from __future__ import annotations

from .polydiff import PolyDiff
from .polyfile import PolyFile
