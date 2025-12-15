#!/usr/bin/env python3
"""
dotPipe Language Interpreter
A lightweight programming language for building UI applications
"""

import json
import sys
import re
import math
import random
from typing import Any, Dict, List, Optional, Callable
from abc import ABC, abstractmethod
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

# ============================================================================
# TOKENIZER & PARSER
# ============================================================================

class Token:
    """Represents a token in the dotPipe language"""
    def __init__(self, type_: str, value: str, line: int = 0, col: int = 0):
        self.type = type_
        self.value = value
        self.line = line
        self.col = col
    
    def __repr__(self):
        return f"Token({self.type}, {self.value!r})"


class Lexer:
    """Tokenizes dotPipe source code"""
    
    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1
        self.col = 1
        self.tokens = []
    
    def tokenize(self) -> List[Token]:
        """Convert source code into tokens"""
        while self.pos < len(self.source):
            self._skip_whitespace()
            if self.pos >= len(self.source):
                break
            
            char = self.source[self.pos]
            
            if char == '|':
                self._read_pipe()
            elif char == '!':
                self._read_variable()
            elif char == '&':
                self._read_assign()
            elif char == '@':
                self._read_object_access()
            elif char == '#':
                self._read_array_access()
            elif char in '{}[]():,-':
                self.tokens.append(Token('SYMBOL', char, self.line, self.col))
                self.pos += 1
                self.col += 1
            elif char == '"':
                self._read_string()
            elif char.isdigit():
                self._read_number()
            elif char.isalpha():
                self._read_identifier()
            else:
                self.pos += 1
                self.col += 1
        
        self.tokens.append(Token('EOF', '', self.line, self.col))
        return self.tokens
    
    def _skip_whitespace(self):
        while self.pos < len(self.source) and self.source[self.pos].isspace():
            if self.source[self.pos] == '\n':
                self.line += 1
                self.col = 1
            else:
                self.col += 1
            self.pos += 1
    
    def _read_pipe(self):
        start = self.pos
        self.pos += 1
        self.col += 1
        func_name = ''
        while self.pos < len(self.source) and (self.source[self.pos].isalnum() or self.source[self.pos] in '_-'):
            func_name += self.source[self.pos]
            self.pos += 1
            self.col += 1
        self.tokens.append(Token('PIPE', func_name, self.line, self.col - len(func_name) - 1))
    
    def _read_variable(self):
        self.tokens.append(Token('VAR_GET', '', self.line, self.col))
        self.pos += 1
        self.col += 1
        var_name = ''
        while self.pos < len(self.source) and (self.source[self.pos].isalnum() or self.source[self.pos] in '_'):
            var_name += self.source[self.pos]
            self.pos += 1
            self.col += 1
        if var_name:
            self.tokens.append(Token('IDENT', var_name, self.line, self.col - len(var_name)))
    
    def _read_assign(self):
        self.tokens.append(Token('ASSIGN', '', self.line, self.col))
        self.pos += 1
        self.col += 1
        var_name = ''
        while self.pos < len(self.source) and (self.source[self.pos].isalnum() or self.source[self.pos] in '_'):
            var_name += self.source[self.pos]
            self.pos += 1
            self.col += 1
        if var_name:
            self.tokens.append(Token('IDENT', var_name, self.line, self.col - len(var_name)))
    
    def _read_object_access(self):
        self.tokens.append(Token('OBJ_ACCESS', '', self.line, self.col))
        self.pos += 1
        self.col += 1
        obj_name = ''
        while self.pos < len(self.source) and (self.source[self.pos].isalnum() or self.source[self.pos] in '_'):
            obj_name += self.source[self.pos]
            self.pos += 1
            self.col += 1
        if obj_name:
            self.tokens.append(Token('IDENT', obj_name, self.line, self.col - len(obj_name)))
        if self.pos < len(self.source) and self.source[self.pos] == '.':
            self.pos += 1
            self.col += 1
            prop_name = ''
            while self.pos < len(self.source) and (self.source[self.pos].isalnum() or self.source[self.pos] in '_'):
                prop_name += self.source[self.pos]
                self.pos += 1
                self.col += 1
            if prop_name:
                self.tokens.append(Token('IDENT', prop_name, self.line, self.col - len(prop_name)))
    
    def _read_array_access(self):
        self.tokens.append(Token('ARR_ACCESS', '', self.line, self.col))
        self.pos += 1
        self.col += 1
        arr_name = ''
        while self.pos < len(self.source) and (self.source[self.pos].isalnum() or self.source[self.pos] in '_'):
            arr_name += self.source[self.pos]
            self.pos += 1
            self.col += 1
        if arr_name:
            self.tokens.append(Token('IDENT', arr_name, self.line, self.col - len(arr_name)))
        if self.pos < len(self.source) and self.source[self.pos] == '.':
            self.pos += 1
            self.col += 1
            index = ''
            while self.pos < len(self.source) and self.source[self.pos].isdigit():
                index += self.source[self.pos]
                self.pos += 1
                self.col += 1
            if index:
                self.tokens.append(Token('NUMBER', index, self.line, self.col - len(index)))
    
    def _read_string(self):
        quote = self.source[self.pos]
        self.pos += 1
        self.col += 1
        value = ''
        while self.pos < len(self.source) and self.source[self.pos] != quote:
            if self.source[self.pos] == '\\' and self.pos + 1 < len(self.source):
                self.pos += 1
                self.col += 1
                escape_char = self.source[self.pos]
                if escape_char == 'n':
                    value += '\n'
                elif escape_char == 't':
                    value += '\t'
                elif escape_char == 'r':
                    value += '\r'
                elif escape_char == '\\':
                    value += '\\'
                else:
                    value += escape_char
            else:
                value += self.source[self.pos]
            self.pos += 1
            self.col += 1
        if self.pos < len(self.source):
            self.pos += 1
            self.col += 1
        self.tokens.append(Token('STRING', value, self.line, self.col - len(value)))
    
    def _read_number(self):
        value = ''
        while self.pos < len(self.source) and (self.source[self.pos].isdigit() or self.source[self.pos] == '.'):
            value += self.source[self.pos]
            self.pos += 1
            self.col += 1
        self.tokens.append(Token('NUMBER', value, self.line, self.col - len(value)))
    
    def _read_identifier(self):
        value = ''
        while self.pos < len(self.source) and (self.source[self.pos].isalnum() or self.source[self.pos] in '_-'):
            value += self.source[self.pos]
            self.pos += 1
            self.col += 1
        token_type = 'KEYWORD' if value in ('true', 'false', 'null') else 'IDENT'
        self.tokens.append(Token(token_type, value, self.line, self.col - len(value)))


class ASTNode(ABC):
    """Base class for AST nodes"""
    @abstractmethod
    def accept(self, visitor):
        pass


class LiteralNode(ASTNode):
    def __init__(self, value: Any):
        self.value = value
    def accept(self, visitor):
        return visitor.visit_literal(self)


class VariableNode(ASTNode):
    def __init__(self, name: str):
        self.name = name
    def accept(self, visitor):
        return visitor.visit_variable(self)


class PipeNode(ASTNode):
    def __init__(self, func_name: str, args: List[ASTNode]):
        self.func_name = func_name
        self.args = args
    def accept(self, visitor):
        return visitor.visit_pipe(self)


class AssignNode(ASTNode):
    def __init__(self, var_name: str, value: ASTNode):
        self.var_name = var_name
        self.value = value
    def accept(self, visitor):
        return visitor.visit_assign(self)


class Parser:
    """Parses tokens into AST"""
    
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
    
    def parse(self) -> List[ASTNode]:
        """Parse tokens into a program"""
        nodes = []
        while not self._is_at_end():
            if self.current().type == 'PIPE':
                nodes.append(self._parse_pipe())
            elif self.current().type == 'ASSIGN':
                nodes.append(self._parse_assign())
            elif self.current().type == 'VAR_GET':
                nodes.append(self._parse_variable())
            else:
                nodes.append(self._parse_expression())
        return nodes
    
    def _parse_pipe(self) -> PipeNode:
        func_name = self.current().value
        self.advance()  # skip PIPE
        
        args = []
        while not self._is_at_end() and self.current().type not in ('PIPE', 'ASSIGN', 'VAR_GET', 'EOF'):
            if self.current().value == ':':
                self.advance()  # skip colon
                continue
            args.append(self._parse_expression())
        
        return PipeNode(func_name, args)
    
    def _parse_assign(self) -> AssignNode:
        self.advance()  # skip &
        var_name = self.current().value
        self.advance()  # skip IDENT
        self.advance() if self.current().value == ':' else None
        
        value = self._parse_expression()
        return AssignNode(var_name, value)
    
    def _parse_variable(self) -> VariableNode:
        self.advance()  # skip !
        name = self.current().value
        self.advance()  # skip IDENT
        return VariableNode(name)
    
    def _parse_expression(self) -> ASTNode:
        token = self.current()
        
        if token.type == 'STRING':
            self.advance()
            return LiteralNode(token.value)
        elif token.type == 'NUMBER':
            self.advance()
            val = float(token.value) if '.' in token.value else int(token.value)
            return LiteralNode(val)
        elif token.type == 'KEYWORD':
            self.advance()
            if token.value == 'true':
                return LiteralNode(True)
            elif token.value == 'false':
                return LiteralNode(False)
            else:
                return LiteralNode(None)
        elif token.type == 'VAR_GET':
            return self._parse_variable()
        elif token.type == 'PIPE':
            return self._parse_pipe()
        elif token.type == 'IDENT':
            self.advance()
            return LiteralNode(token.value)
        elif token.type == 'SYMBOL' and token.value == '-':
            # Handle negative numbers
            self.advance()
            next_token = self.current()
            if next_token.type == 'NUMBER':
                self.advance()
                val = float(next_token.value) if '.' in next_token.value else int(next_token.value)
                return LiteralNode(-val)
            else:
                return LiteralNode(-1)
        
        self.advance()
        return LiteralNode(None)
    
    def current(self) -> Token:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return Token('EOF', '')
    
    def advance(self):
        self.pos += 1
    
    def _is_at_end(self) -> bool:
        return self.current().type == 'EOF'


# ============================================================================
# RUNTIME & INTERPRETER
# ============================================================================

class Runtime:
    """Runtime environment for dotPipe execution"""
    
    def __init__(self):
        self.globals = {}
        self.locals = {}
        self.functions = {}
        self.ui_components = {}
        self.event_handlers = {}
        self.built_in_functions = self._setup_builtins()
    
    def _setup_builtins(self) -> Dict[str, Callable]:
        """Setup built-in functions"""
        return {
            # I/O
            'log': self._builtin_log,
            'print': self._builtin_log,
            'input': self._builtin_input,
            
            # Arithmetic
            'add': lambda *args: sum(args),
            'sub': lambda a, b: a - b,
            'mul': lambda *args: math.prod(args) if args else 0,
            'div': lambda a, b: a / b if b != 0 else 0,
            'mod': lambda a, b: a % b if b != 0 else 0,
            'abs': lambda a: abs(a),
            'sqrt': lambda a: math.sqrt(a),
            'pow': lambda a, b: pow(a, b),
            'round': lambda a: round(a),
            'floor': lambda a: math.floor(a),
            'ceil': lambda a: math.ceil(a),
            'max': lambda *args: max(args) if args else 0,
            'min': lambda *args: min(args) if args else 0,
            'random': lambda *args: random.uniform(args[0], args[1]) if len(args) == 2 else random.random(),
            
            # String
            'concat': lambda *args: ''.join(str(a) for a in args),
            'uppercase': lambda s: str(s).upper(),
            'lowercase': lambda s: str(s).lower(),
            'split': lambda s, delim: str(s).split(delim),
            'join': lambda arr, delim: delim.join(str(a) for a in arr),
            'length': lambda s: len(s),
            'substring': lambda s, start, end=None: str(s)[start:end],
            'trim': lambda s: str(s).strip(),
            'replace': lambda s, old, new: str(s).replace(old, new),
            
            # Array
            'push': lambda arr, val: arr.append(val) or arr,
            'pop': lambda arr: arr.pop() if arr else None,
            'shift': lambda arr: arr.pop(0) if arr else None,
            'unshift': lambda arr, val: arr.insert(0, val) or arr,
            'slice': lambda arr, start, end=None: arr[start:end],
            'reverse': lambda arr: arr[::-1],
            'sort': lambda arr: sorted(arr),
            'map': lambda arr, func: [func(x) for x in arr],
            'filter': lambda arr, func: [x for x in arr if func(x)],
            'find': lambda arr, func: next((x for x in arr if func(x)), None),
            'some': lambda arr, func: any(func(x) for x in arr),
            'every': lambda arr, func: all(func(x) for x in arr),
            
            # Object/Dict
            'keys': lambda obj: list(obj.keys()) if isinstance(obj, dict) else [],
            'values': lambda obj: list(obj.values()) if isinstance(obj, dict) else [],
            'get': lambda obj, key: obj.get(key) if isinstance(obj, dict) else None,
            'set': lambda obj, key, val: obj.update({key: val}) or obj if isinstance(obj, dict) else obj,
            
            # Type
            'typeof': lambda val: type(val).__name__,
            'tostring': lambda val: str(val),
            'tonumber': lambda val: float(val) if isinstance(val, str) else val,
            'tobool': lambda val: bool(val),
            'isnull': lambda val: val is None,
            
            # Comparison
            'eq': lambda a, b: a == b,
            'ne': lambda a, b: a != b,
            'gt': lambda a, b: a > b,
            'lt': lambda a, b: a < b,
            'gte': lambda a, b: a >= b,
            'lte': lambda a, b: a <= b,
            'and': lambda *args: all(args),
            'or': lambda *args: any(args),
            'not': lambda a: not a,
            
            # Control
            'if': self._builtin_if,
            'for': self._builtin_for,
            'while': self._builtin_while,
        }
    
    def _builtin_log(self, *args):
        print(' '.join(str(arg) for arg in args))
        return None
    
    def _builtin_input(self, prompt=''):
        return input(str(prompt))
    
    def _builtin_if(self, condition, true_branch, false_branch=None):
        if condition:
            return true_branch() if callable(true_branch) else true_branch
        else:
            return false_branch() if callable(false_branch) else false_branch
    
    def _builtin_for(self, iterable, func):
        results = []
        for item in (iterable if isinstance(iterable, (list, tuple)) else [iterable]):
            result = func(item) if callable(func) else None
            results.append(result)
        return results
    
    def _builtin_while(self, condition_func, body_func):
        result = None
        while condition_func() if callable(condition_func) else condition_func:
            result = body_func() if callable(body_func) else None
        return result


class Interpreter(Parser):
    """Interprets AST and executes dotPipe code"""
    
    def __init__(self, tokens: List[Token]):
        super().__init__(tokens)
        self.runtime = Runtime()
    
    def execute(self, nodes: List[ASTNode]) -> Any:
        """Execute AST nodes"""
        result = None
        for node in nodes:
            result = node.accept(self)
        return result
    
    def visit_literal(self, node: LiteralNode) -> Any:
        return node.value
    
    def visit_variable(self, node: VariableNode) -> Any:
        if node.name in self.runtime.locals:
            return self.runtime.locals[node.name]
        elif node.name in self.runtime.globals:
            return self.runtime.globals[node.name]
        return None
    
    def visit_assign(self, node: AssignNode) -> Any:
        value = node.value.accept(self)
        self.runtime.locals[node.var_name] = value
        return value
    
    def visit_pipe(self, node: PipeNode) -> Any:
        """Execute a pipe function"""
        func_name = node.func_name
        
        # Get function
        if func_name in self.runtime.built_in_functions:
            func = self.runtime.built_in_functions[func_name]
        elif func_name in self.runtime.functions:
            func = self.runtime.functions[func_name]
        else:
            raise NameError(f"Function not found: {func_name}")
        
        # Evaluate arguments
        args = [arg.accept(self) for arg in node.args]
        
        # Execute function
        try:
            return func(*args)
        except TypeError as e:
            raise TypeError(f"Error calling {func_name}: {e}")


# ============================================================================
# WINDOWS UI BUILDER
# ============================================================================

class UIBuilder:
    """Build Windows UI from dotPipe specifications"""
    
    def __init__(self):
        self.root = None
        self.components = {}
    
    def create_window(self, spec: Dict) -> tk.Tk:
        """Create a main window from specification"""
        self.root = tk.Tk()
        
        # Configure window
        title = spec.get('title', 'dotPipe Application')
        width = spec.get('width', 800)
        height = spec.get('height', 600)
        
        self.root.title(title)
        self.root.geometry(f"{width}x{height}")
        
        # Create children
        children = spec.get('children', [])
        for i, child_spec in enumerate(children):
            self._create_component(self.root, child_spec, i)
        
        return self.root
    
    def _create_component(self, parent: tk.Widget, spec: Dict, index: int) -> tk.Widget:
        """Create a UI component"""
        comp_type = spec.get('type', 'Label')
        comp_id = spec.get('id', f"{comp_type}_{index}")
        
        if comp_type == 'Button':
            widget = self._create_button(parent, spec)
        elif comp_type == 'Label':
            widget = self._create_label(parent, spec)
        elif comp_type == 'Entry':
            widget = self._create_entry(parent, spec)
        elif comp_type == 'Text':
            widget = self._create_text(parent, spec)
        elif comp_type == 'Frame':
            widget = self._create_frame(parent, spec)
        elif comp_type == 'Listbox':
            widget = self._create_listbox(parent, spec)
        else:
            widget = ttk.Label(parent, text=f"Unknown type: {comp_type}")
        
        self.components[comp_id] = widget
        return widget
    
    def _create_button(self, parent: tk.Widget, spec: Dict) -> tk.Button:
        btn = tk.Button(
            parent,
            text=spec.get('text', 'Button'),
            relief=tk.RAISED,
            padx=10,
            pady=5
        )
        btn.pack(pady=5, padx=5)
        return btn
    
    def _create_label(self, parent: tk.Widget, spec: Dict) -> tk.Label:
        lbl = tk.Label(parent, text=spec.get('text', ''))
        lbl.pack(pady=5, padx=5)
        return lbl
    
    def _create_entry(self, parent: tk.Widget, spec: Dict) -> tk.Entry:
        entry = tk.Entry(parent, width=spec.get('width', 40))
        entry.pack(pady=5, padx=5)
        return entry
    
    def _create_text(self, parent: tk.Widget, spec: Dict) -> tk.Text:
        text = tk.Text(parent, width=spec.get('width', 40), height=spec.get('height', 10))
        text.pack(pady=5, padx=5)
        return text
    
    def _create_frame(self, parent: tk.Widget, spec: Dict) -> tk.Frame:
        frame = tk.Frame(parent, relief=tk.SUNKEN, borderwidth=2)
        frame.pack(pady=5, padx=5, fill=tk.BOTH, expand=True)
        
        # Create children
        children = spec.get('children', [])
        for i, child_spec in enumerate(children):
            self._create_component(frame, child_spec, i)
        
        return frame
    
    def _create_listbox(self, parent: tk.Widget, spec: Dict) -> tk.Listbox:
        listbox = tk.Listbox(parent, height=spec.get('height', 10))
        listbox.pack(pady=5, padx=5, fill=tk.BOTH, expand=True)
        
        items = spec.get('items', [])
        for item in items:
            listbox.insert(tk.END, item)
        
        return listbox


# ============================================================================
# MAIN PROGRAM
# ============================================================================

def interpret(source: str) -> Any:
    """Main function to interpret dotPipe code"""
    try:
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        interp = Interpreter(tokens)
        ast = interp.parse()
        
        return interp.execute(ast)
    except Exception as e:
        print(f"Error: {e}")
        return None


if __name__ == '__main__':
    # Example program
    code = """
    |log:Hello from dotPipe!
    |&name:World
    |log:Hello !name
    |&result:|add:5:3
    |log:5 + 3 = !result
    """
    
    interpret(code)
