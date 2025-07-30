# Walking Man

This is Walking Man.

```txt
     .---.
    ( Hi! )
     '---'
         |
 <('-'<) v
 ```

A friendly companion while you wait.

## Usage

Walking Man is designed to be simple and bring joy to your command-line applications. He's perfect for those moments when users need to wait for something to complete.

### Basic Usage

```python
from walking_man import walking_man

# As a context manager (recommended)
with walking_man():
    time.sleep(5)  # Your long-running operation here
```

### With Custom Message

```python
# Walking Man will display your message above the animation
with walking_man("Loading your data..."):
    time.sleep(5)
```

### Customizing Walking Man

```python
# Change his color (cyan is his favorite, but he looks good in yellow too)
with walking_man("Processing...", color="yellow"):
    # ...

# Make him walk faster or slower (lower values = faster)
with walking_man("Please wait...", speed=0.1):  # Speedy Walking Man!
    # ...
```

### Conditional Walking Man

Sometimes you only want Walking Man to appear based on certain conditions (like verbose mode):

```python
from walking_man import conditional_walking_man

verbose = True  # Or any condition

with conditional_walking_man(verbose, "Working on it..."):
    # Walking Man only appears if the condition is True
    # ...
```

### Clearing Walking Man

Walking Man is pretty good about cleaning up after himself, but if he ever gets stuck:

```python
# If there was loading text, clear the line above
WalkingMan.clear(line_above=True)

# Otherwise, just clear the current line
WalkingMan.clear()
```

### Using Walking Man Responsibly

Walking Man is a special friend who brings joy to tedious waiting times. But like any good thing, moderation is key:

- Don't overuse him on every loading screen
- Let him appear unexpectedly to bring surprise and delight
- Save him for those moments when users really need a smile
- Popping up infrequently is part of his magic ✨

Walking Man is most effective when he shows up just when you've forgotten about him, making you smile exactly when you needed it most.
