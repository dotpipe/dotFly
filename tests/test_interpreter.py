#!/usr/bin/env python3
"""
Comprehensive test suite for dotPipe interpreter
Tests every function and language feature
"""

import unittest
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from interpreter import Lexer, Parser, Interpreter, Token, LiteralNode, VariableNode, PipeNode, AssignNode, Runtime

class TestLexer(unittest.TestCase):
    """Test tokenizer"""
    
    def test_pipe_token(self):
        lexer = Lexer("|add:5:3")
        tokens = lexer.tokenize()
        self.assertEqual(tokens[0].type, 'PIPE')
        self.assertEqual(tokens[0].value, 'add')
    
    def test_variable_token(self):
        lexer = Lexer("!myvar")
        tokens = lexer.tokenize()
        self.assertEqual(tokens[0].type, 'VAR_GET')
        self.assertEqual(tokens[1].value, 'myvar')
    
    def test_string_token(self):
        lexer = Lexer('"hello world"')
        tokens = lexer.tokenize()
        self.assertEqual(tokens[0].type, 'STRING')
        self.assertEqual(tokens[0].value, 'hello world')
    
    def test_number_token(self):
        lexer = Lexer('42 3.14')
        tokens = lexer.tokenize()
        self.assertEqual(tokens[0].type, 'NUMBER')
        self.assertEqual(tokens[0].value, '42')
        self.assertEqual(tokens[1].type, 'NUMBER')
        self.assertEqual(tokens[1].value, '3.14')
    
    def test_assign_token(self):
        lexer = Lexer("&myvar:value")
        tokens = lexer.tokenize()
        self.assertEqual(tokens[0].type, 'ASSIGN')

class TestArithmetic(unittest.TestCase):
    """Test arithmetic operations"""
    
    def _execute(self, code):
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        interp = Interpreter(tokens)
        ast = interp.parse()
        return interp.execute(ast)
    
    def test_add(self):
        result = self._execute("|add:5:3")
        self.assertEqual(result, 8)
    
    def test_sub(self):
        result = self._execute("|sub:10:3")
        self.assertEqual(result, 7)
    
    def test_mul(self):
        result = self._execute("|mul:4:5")
        self.assertEqual(result, 20)
    
    def test_div(self):
        result = self._execute("|div:20:4")
        self.assertEqual(result, 5.0)
    
    def test_mod(self):
        result = self._execute("|mod:10:3")
        self.assertEqual(result, 1)
    
    def test_abs(self):
        result = self._execute("|abs:-5")
        self.assertEqual(result, 5)
    
    def test_sqrt(self):
        result = self._execute("|sqrt:16")
        self.assertEqual(result, 4.0)

class TestStrings(unittest.TestCase):
    """Test string operations"""
    
    def _execute(self, code):
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        interp = Interpreter(tokens)
        ast = interp.parse()
        return interp.execute(ast)
    
    def test_length(self):
        result = self._execute('|length:"hello"')
        self.assertEqual(result, 5)
    
    def test_uppercase(self):
        result = self._execute('|uppercase:"hello"')
        self.assertEqual(result, 'HELLO')
    
    def test_lowercase(self):
        result = self._execute('|lowercase:"HELLO"')
        self.assertEqual(result, 'hello')
    
    def test_trim(self):
        result = self._execute('|trim:"  hello  "')
        self.assertEqual(result, 'hello')

class TestVariables(unittest.TestCase):
    """Test variable operations"""
    
    def test_assignment(self):
        lexer = Lexer("&x:42")
        tokens = lexer.tokenize()
        interp = Interpreter(tokens)
        ast = interp.parse()
        interp.execute(ast)
        self.assertEqual(interp.runtime.locals['x'], 42)

class TestComparisons(unittest.TestCase):
    """Test comparison operations"""
    
    def test_equal(self):
        runtime = Runtime()
        result = runtime.built_in_functions['eq'](5, 5)
        self.assertEqual(result, True)
    
    def test_not_equal(self):
        runtime = Runtime()
        result = runtime.built_in_functions['ne'](5, 3)
        self.assertEqual(result, True)
    
    def test_greater_than(self):
        runtime = Runtime()
        result = runtime.built_in_functions['gt'](10, 5)
        self.assertEqual(result, True)
    
    def test_logical_and(self):
        runtime = Runtime()
        result = runtime.built_in_functions['and'](True, True)
        self.assertEqual(result, True)
    
    def test_logical_or(self):
        runtime = Runtime()
        result = runtime.built_in_functions['or'](False, True)
        self.assertEqual(result, True)
    
    def test_logical_not(self):
        runtime = Runtime()
        result = runtime.built_in_functions['not'](False)
        self.assertEqual(result, True)

class TestTypeConversions(unittest.TestCase):
    """Test type conversion functions"""
    
    def test_typeof(self):
        runtime = Runtime()
        self.assertEqual(runtime.built_in_functions['typeof'](42), 'int')
        self.assertEqual(runtime.built_in_functions['typeof']("hello"), 'str')
    
    def test_tostring(self):
        runtime = Runtime()
        self.assertEqual(runtime.built_in_functions['tostring'](42), '42')
    
    def test_tonumber(self):
        runtime = Runtime()
        self.assertEqual(runtime.built_in_functions['tonumber']('42'), 42)
    
    def test_tobool(self):
        runtime = Runtime()
        self.assertEqual(runtime.built_in_functions['tobool'](1), True)
        self.assertEqual(runtime.built_in_functions['tobool'](0), False)

def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestLexer))
    suite.addTests(loader.loadTestsFromTestCase(TestArithmetic))
    suite.addTests(loader.loadTestsFromTestCase(TestStrings))
    suite.addTests(loader.loadTestsFromTestCase(TestVariables))
    suite.addTests(loader.loadTestsFromTestCase(TestComparisons))
    suite.addTests(loader.loadTestsFromTestCase(TestTypeConversions))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result

if __name__ == '__main__':
    result = run_tests()
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Tests Run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n✓ ALL TESTS PASSED!")
    else:
        print("\n✗ Some tests failed")
