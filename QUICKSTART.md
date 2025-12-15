# dotPipe Quick Start Guide

Welcome to dotPipe - A complete programming language for Windows!

## 5-Minute Setup

### 1. Verify Installation
```bash
cd C:\Users\g0d77\New folder\dotFly
python tests/test_interpreter.py
```

**Expected Output:**
```
✓ ALL 27 TESTS PASSED!
```

### 2. Run Example Programs
```bash
python examples/demo.py
```

### 3. Try It Yourself

Create a file `hello.py`:
```python
from src.interpreter import interpret

code = """
|log:"Hello from dotPipe!"
&name:"World"
|log:"Greetings, "!name
"""

interpret(code)
```

Run it:
```bash
python hello.py
```

## Language Basics

### Variables
```dotpipe
&myvar:42
|log:!myvar
```

### Arithmetic
```dotpipe
|log:|add:5:3
|log:|mul:4:5
|log:|sqrt:16
```

### Strings
```dotpipe
|log:|uppercase:"hello"
|log:|length:"hello"
|log:|concat:"Hello ":" World"
```

### Comparisons
```dotpipe
|log:|eq:5:5
|log:|gt:10:5
|log:|and:true:true
```

## Building Windows UI

```python
from src.interpreter import UIBuilder

spec = {
    "title": "My Application",
    "width": 800,
    "height": 600,
    "children": [
        {"type": "Label", "text": "Welcome!"},
        {"type": "Button", "text": "Click Me", "id": "btn1"},
        {"type": "Entry", "width": 40, "id": "input1"},
    ]
}

builder = UIBuilder()
root = builder.create_window(spec)

# Get components
button = builder.components['btn1']
entry = builder.components['input1']

# Add event handlers
def on_click():
    text = entry.get()
    print(f"You entered: {text}")

button.config(command=on_click)
root.mainloop()
```

## All Built-in Functions

### I/O
- `|log:message`
- `|print:message`
- `|input:prompt`

### Arithmetic
- `|add:a:b` `|sub:a:b` `|mul:a:b` `|div:a:b` `|mod:a:b`
- `|abs:a` `|sqrt:a` `|pow:a:b`
- `|round:a` `|floor:a` `|ceil:a`
- `|max:...` `|min:...` `|random:min:max`

### String
- `|concat:...` `|uppercase:s` `|lowercase:s`
- `|length:s` `|trim:s` `|substring:s:start:end`
- `|split:s:delim` `|join:arr:delim` `|replace:s:old:new`

### Array
- `|push:arr:val` `|pop:arr` `|shift:arr` `|unshift:arr:val`
- `|slice:arr:start:end` `|reverse:arr` `|sort:arr`

### Comparison
- `|eq:a:b` `|ne:a:b` `|gt:a:b` `|lt:a:b`
- `|gte:a:b` `|lte:a:b` `|and:...` `|or:...` `|not:a`

### Type
- `|typeof:val` `|tostring:val` `|tonumber:val`
- `|tobool:val` `|isnull:val`

### Object
- `|keys:obj` `|values:obj` `|get:obj:key` `|set:obj:key:val`

## Common Patterns

### Calculate Something
```dotpipe
&price:99.99
&tax:|mul:!price:0.08
&total:|add:!price:!tax
|log:"Total: "|concat:!total
```

### Process Text
```dotpipe
&text:"hello world"
&words:|split:!text:" "
&count:|length:!words
|log:"Word count: "|concat:!count
```

### Check Types
```dotpipe
|log:|typeof:42
|log:|typeof:"hello"
|log:|typeof:true
|log:|typeof:null
```

### Convert Values
```dotpipe
|log:|tostring:123
|log:|tonumber:"456"
|log:|tobool:0
```

## Project Files

```
src/interpreter.py          654 lines - Main implementation
tests/test_interpreter.py  27 tests - Complete test suite
examples/demo.py           4 examples - Sample programs
docs/LANGUAGE_SPEC.md      Language specification
README.md                  Full documentation
requirements.txt           Dependencies (none needed!)
```

## Troubleshooting

**Q: How do I run tests?**
A: `python tests/test_interpreter.py`

**Q: How do I run examples?**
A: `python examples/demo.py`

**Q: Can I use it without tkinter?**
A: Yes! Use `interpret()` for console apps, `UIBuilder` only for GUI.

**Q: What Python version do I need?**
A: Python 3.13 or higher

**Q: Are there any external dependencies?**
A: No! Only tkinter (included with Python).

## Next Steps

1. Read [README.md](README.md) for complete documentation
2. Check [docs/LANGUAGE_SPEC.md](docs/LANGUAGE_SPEC.md) for all language features
3. Explore [examples/demo.py](examples/demo.py) for more programs
4. Build your own application!

## Resources

- **Documentation:** See README.md
- **Language Spec:** See docs/LANGUAGE_SPEC.md
- **Examples:** Run examples/demo.py
- **Tests:** Run tests/test_interpreter.py
- **Source Code:** See src/interpreter.py

## Have Fun!

dotPipe is a complete, working programming language. Start building!

```dotpipe
|log:"Welcome to dotPipe!"
|log:"Start coding now!"
```

---

**Version:** 1.0  
**Status:** ✓ Production Ready  
**License:** MIT
