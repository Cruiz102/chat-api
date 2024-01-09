import unittest
from python_parser import pythonParser
import os
import tempfile
import ast

class TestPythonParser(unittest.TestCase):

    def test_get_function_body(self):
        # Test the get_function_body method
        source_code = """def example_function(arg1, arg2):
                             return arg1 + arg2"""
        node = ast.parse(source_code)
        function_node = node.body[0]  # Assuming there is only one function

        # Manually splitting the source code into lines to simulate 'source_lines'
        source_lines = source_code.split('\n')

        expected_body = 'def example_function(arg1, arg2):\n                             return arg1 + arg2'
        result = pythonParser.get_function_body(source_lines, function_node)
        self.assertEqual(result, expected_body)

    def test_parse_python_functions(self):
        # Test the parse_python_functions method
        # Create a temporary Python file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py') as tmp:
            tmp.write("def foo():\n    return 'bar'")
            tmp_file_path = tmp.name

        expected_result = {
            'foo': {
                "name": "foo",
                'body': "def foo():\n    return 'bar'",
                'called_functions': [],
                'class_name': None
            }
            
        }
        result = pythonParser().parse_python_functions(tmp_file_path)
        self.assertEqual(result, expected_result)

        # Clean up the temporary file
        os.remove(tmp_file_path)

    def test_filter_callables(self):
        # Test the _filter_callables method
        parser = pythonParser(filtered_libraries_aliases=['os'])
        callables = ['print', 'os.path.join', 'custom_function']
        parser._filter_callables(callables)
        
        # Assuming 'os.path.join' is in the filtered_libraries_aliases
        expected_result = ['custom_function']
        self.assertEqual(callables, expected_result)

    def test_traverse_through_directory(self):
        # Test the traverse_through_directory method
        # Create a temporary directory and files
        with tempfile.TemporaryDirectory() as tmp_dir:
            file_path_1 = os.path.join(tmp_dir, 'test1.py')
            with open(file_path_1, 'w') as f:
                f.write("def foo():\n    return 'bar'")

            file_path_2 = os.path.join(tmp_dir, 'test2.py')
            with open(file_path_2, 'w') as f:
                f.write("def bar():\n    return 'foo'")

            result = pythonParser().traverse_through_directory(tmp_dir)
            expected_keys = {os.path.basename(file_path_1), os.path.basename(file_path_2)}
            self.assertEqual(set(result.keys()), expected_keys)

            # Asserting the function names in each file
            self.assertIn('foo', result[os.path.basename(file_path_1)])
            self.assertIn('bar', result[os.path.basename(file_path_2)])

if __name__ == '__main__':
    unittest.main()
