import unittest
from graph_text import extract_function_calls, filter_out_library_and_builtin_calls, get_code_functions_from_path
import tempfile
import os

class TestFunctionFilter(unittest.TestCase):

    def filter_methods_of_objects(self):
        """Filter the function that are methods of objects"""

    def test_full_function_body_extract(self):
        code = """
        def example():
            print("Hello")
            custom_func()
        """
        expected_message = "Function definition detected in function body. This function expects only the body of another function, not a full function definition."
        with self.assertRaises(ValueError) as context:
            extract_function_calls(code)
        
        self.assertEqual(str(context.exception), expected_message)

    def test_filter_out_library_and_builtin_calls(self):
        function_calls = {'print', 'custom_func', 'np.array'}
        library_aliases = ['np']
        expected = {'custom_func'}
        result = filter_out_library_and_builtin_calls(function_calls, library_aliases)
        self.assertEqual(result, expected)

    def test_analyze_python_file(self):
        mock_code = """
            def mock_function():
                np.array([1, 2, 3])
                do_something()
                torch.nn.Module()
                result = process_data()
                print()
                return something
            """
        library_aliases = ['np', 'torch']

        # Create a temporary file in the /tmp directory and write mock code to it
        with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.py', dir='/tmp') as temp:
            temp.write(mock_code)
            temp_file_path = temp.name

        # Test analyze_python_file function
        try:
            results = get_code_functions_from_path(temp_file_path, library_aliases)
            self.assertTrue(len(results) > 0)  # Check if there's at least one function analyzed
            for _, function_body, non_library_builtin_calls in results:
                self.assertNotIn('np.array', non_library_builtin_calls)
                self.assertNotIn('torch.nn.Module', non_library_builtin_calls)
        finally:
            # Clean up - remove the temporary file
            os.remove(temp_file_path)

if __name__ == '__main__':
    unittest.main()
