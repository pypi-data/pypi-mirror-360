# .meow — The Feline-Friendly Esoteric Programming Language

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> Because programming should be fun, cats are chaotic, and you deserve to write code that goes meow!

## What is MeowLang?

MeowLang (.meow) is a whimsical esoteric programming language where every line of code sounds like a cat. Inspired by the chaos of esolangs and the elegance of felines, .meow lets you vibe code using cat noises.

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/meow.git
cd meow

# Run a .meow program
python meow_interpreter.py examples/hello_world.meow
```

### Your First .meow Program

Create a file called `hello.meow`:

```meow
# Hello World in .meow
meow
meow
meow
purr
hiss
purr
scratch
purr
```

Run it:
```bash
python meow_interpreter.py hello.meow
```

Output:
```
3
2
0
```

## Commands Reference

| Command | Action | Example |
|---------|--------|---------|
| `meow` | Increment memory value by 1 | `meow` → memory += 1 |
| `hiss` | Decrement memory value by 1 | `hiss` → memory -= 1 |
| `purr` | Print the current memory value | `purr` → prints memory |
| `nap` | Do nothing (no-op) | `nap` → does nothing |
| `scratch` | Reset memory value to 0 | `scratch` → memory = 0 |
| `lick` | Double the current memory value | `lick` → memory *= 2 |
| `zoomies` | Square the memory value | `zoomies` → memory = memory² |
| `yowl` | Begin a loop (while memory != 0) | `yowl` → loop start |
| `paw` | End a loop | `paw` → loop end |
| `sleep` | Sleep for memory value milliseconds | `sleep` → pause execution |
| `🐾` | Comment/decoration (ignored) | `🐾 comment 🐾` |
| `mew` | Take user input and set memory to that value | `mew` → memory = user input |
| `pounce <line_number>` | Jump to the specified line number (1-based) | `pounce 5` |

## File Extension

All MeowLang programs are saved as `.meow` files:
- `hello_world.meow`
- `fibonacci.meow`
- `countdown.meow`

## Examples

### Countdown Program

```meow
# Countdown from 5 to 1
meow
meow
meow
meow
meow
yowl
purr
hiss
paw
```

**Output:**
```
5
4
3
2
1
```

### Mathematical Operations

```meow
# Powers and multiplication demo
meow
meow
purr
lick
purr
lick
purr
lick
purr
zoomies
purr
```

**Output:**
```
2
4
8
16
256
```

### Fibonacci Sequence

```meow
# First 8 Fibonacci numbers
meow
purr
purr
meow
meow
purr
meow
meow
meow
purr
# ... (see examples/fibonacci.meow for full program)
```

**Output:**
```
1
1
2
3
5
8
13
21
```

## Usage

### Command Line Interface

```bash
# Run a .meow file
python meow_interpreter.py program.meow

# Execute code directly
python meow_interpreter.py -e "meow meow meow purr"

# Get help
python meow_interpreter.py
```

### Python API

```python
from meow_interpreter import MeowInterpreter

interpreter = MeowInterpreter()

# Run from string
code = """
meow
meow
meow
purr
"""
result = interpreter.run(code)
print(result)  # Output: 3

# Run from file
result = interpreter.run_file("program.meow")
```

## Language Features

### Memory Model
- Single integer memory cell
- Starts at 0
- Can be positive or negative
- Supports basic arithmetic operations

### Control Flow
- Simple while loops with `yowl` and `paw`
- Loops continue while memory != 0
- Nested loops supported

### Input/Output
- `purr` outputs current memory value
- Output is always numeric
- Values are printed on separate lines

### Comments and Decorations
- Lines starting with `🐾` are comments
- Emoji comments (`🐾 comment 🐾`) are ignored
- Empty lines are skipped

## Notes & Limitations

- **Case-sensitive**: All commands must be lowercase
- **Whitespace**: Commands are separated by newlines
- **Unknown commands**: Ignored with a warning
- **Memory limits**: Standard Python integer limits apply
- **No input**: Currently read-only (memory manipulation only)

## Why .meow?

Because:
- **Programming is fun** — Why not make it adorable?
- **Cats are chaotic** — Perfect for esoteric languages
- **You deserve joy** — Write code that makes you smile
- **Learning is better with cats** — Meow while you code!

## Contributing

Want to add more cat commands? Here are some ideas:

- `stretch` — Absolute value
- `pounce` — Jump to line number
- `groom` — Sort memory (if we add arrays)
- `chase` — Random number generation
- `sleep` — Sleep/delay command

## License

MIT License - feel free to use this for fun projects, educational purposes, or just because cats are awesome!

## Acknowledgments

- Inspired by esoteric languages like Brainfuck, Befunge, and LOLCODE
- Made with love for the programming community
- Special thanks to all the cats who inspired this language

---

**Made by cat lovers, for cat lovers**

*"In a world full of serious programming languages, be the one that goes meow!"*