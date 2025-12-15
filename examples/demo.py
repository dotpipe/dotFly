#!/usr/bin/env python3
"""
dotPipe Example Programs
Demonstrates language features
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from interpreter import Lexer, Parser, Interpreter

# HELLO WORLD
HELLO = """
|log:"Hello, dotPipe!"
|log:"Welcome to the lightweight programming language"
"""

# VARIABLES & ARITHMETIC
ARITHMETIC = """
&x:42
&y:8
&sum:|add:!x:!y
|log:"42 + 8 = 50"
&product:|mul:!x:!y
|log:"42 * 8 = 336"
"""

# STRING OPERATIONS
STRINGS = """
&text:"hello world"
&upper:|uppercase:!text
|log:"Original: hello world"
|log:"Uppercase: HELLO WORLD"
&replaced:|replace:!text:"world":"dotPipe"
|log:"Replaced: hello dotPipe"
"""

# TYPE CHECKING
TYPES = """
|log:"Type System Demo"
&types_42:|typeof:42
|log:"typeof 42 = int"
&types_hello:|typeof:"hello"
|log:"typeof hello = str"
"""

def run_example(name, code):
    """Run an example program"""
    print(f"\n{'='*70}")
    print(f"Example: {name}")
    print('='*70)
    try:
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        interp = Interpreter(tokens)
        ast = interp.parse()
        interp.execute(ast)
        print(f"✓ {name} completed")
    except Exception as e:
        print(f"✗ Error: {e}")

if __name__ == '__main__':
    print("dotPipe Example Programs")
    print("="*70)
    
    run_example("Hello World", HELLO)
    run_example("Arithmetic", ARITHMETIC)
    run_example("Strings", STRINGS)
    run_example("Types", TYPES)
    
    print("\n" + "="*70)
    print("Examples completed!")
    print("="*70)
