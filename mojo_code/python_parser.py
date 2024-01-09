#  A Python Parser implementation for extracting the functions inside 
#  a file and the information for the FunctionNode.

import ast
import json
from typing import Set, List
import builtins
import os


class pythonParser:

    def __init__(self, filtered_libraries_aliases: List[str] = None,filter_builtin_functions = True ):
        self.filter_builtin_functions = filter_builtin_functions
        self.filtered_libraries_aliases = filtered_libraries_aliases
        


    
    
    def _filter_callables(self,callables: List[str]):
        """
        Filters out callable names in place, removing those that are built-in or from specified libraries.

        Parameters:
        - callables (List[str]): A list of callable names to be filtered.
        """
        builtin_functions = {func for func in dir(builtins) if callable(getattr(builtins, func))}

        # Create a filtered list
        filtered_callables = [call for call in callables if call not in builtin_functions and
                               not any(call.startswith(alias + '.') for alias in self.filtered_libraries_aliases)]

        # Clear the original list and update it with the filtered items
        callables.clear()
        callables.extend(filtered_callables)


    def _get_function_calls(self,node):
            """ Recursively extract all function calls within a node """
            calls = []
            for child in ast.iter_child_nodes(node):
                if isinstance(child, ast.Call) and isinstance(child.func, ast.Name):
                    calls.append(child.func.id)
                else:
                    calls.extend(self._get_function_calls(child))
            return calls
    @staticmethod
    def get_function_body(source_lines, function_node):
        """
        Extracts the function body as a string from the source code lines and the function node.

        Args:
        - source_lines (list): The source code lines.
        - function_node (ast.FunctionDef): The AST node of the function.

        Returns:
        - str: The function body as a string.
        """
        start_line = function_node.lineno - 1
        end_line = function_node.end_lineno
        return '\n'.join(source_lines[start_line:end_line])
 
    def parse_python_functions(self, file_path):
        """
        Parses a Python file to extract information about its functions.

        Args:
        - file_path (str): The path to the Python file.

        Returns:
        - dict: A dictionary with function names as keys, each value is another dictionary containing:
            - 'body': String containing the full body of the function.
            - 'called_functions': List of function names called within the function.
            - 'class_name': Name of the class the function belongs to, if any.
        """
        with open(file_path, 'r') as file:
            source_code = file.read()
            source_lines = source_code.split('\n')
            node = ast.parse(source_code)

        functions_info = {}
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                # Standalone function, not inside a class
                func_info = self._extract_function_info(item, source_lines, None)
                functions_info[func_info['name']] = func_info
            elif isinstance(item, ast.ClassDef):
                # Process functions inside a class
                for function in item.body:
                    if isinstance(function, ast.FunctionDef):
                        func_info = self._extract_function_info(function, source_lines, item.name)
                        functions_info[func_info['name']] = func_info

        return functions_info

    
    def _extract_function_info(self, function_node, source_lines, class_name):
        """
        Extracts information from a single function node.

        Args:
        - function_node (ast.FunctionDef): AST node for the function.
        - source_lines (list): Lines of source code.
        - class_name (str or None): Name of the class containing the function, if any.

        Returns:
        - dict: Information about the function.
        """
        func_name = function_node.name
        func_body = self.get_function_body(source_lines, function_node)
        called_functions = list(set(self._get_function_calls(function_node)))
        self._filter_callables(called_functions)
        return {
            'name': func_name,
            'body': func_body,
            'called_functions': called_functions,
            'class_name': class_name  # None if the function is not inside a class
        }
    

    def traverse_through_directory(self, directory_path: str):
        """
        Traverses through a directory and performs function analysis on all Python files.

        Args:
        - directory_path (str): The path to the directory.

        Returns:
        - dict: A dictionary with filenames as keys and each value is another dictionary 
                returned by `parse_python_functions` method.
        """
        all_functions_info = {}
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    functions_info = self.parse_python_functions(file_path)
                    all_functions_info[file] = functions_info

        return all_functions_info
    
    

if __name__ == "__main__":
    # Parse the Python file
    parsed_functions_v2 = pythonParser(filtered_libraries_aliases=['os']).traverse_through_directory("/home/cesarruiz/Projects/langchain/chat-api/mojo_code/")
    json_output_v2 = json.dumps(parsed_functions_v2, indent=4)
    file = "./text.json"
    with open(file, 'w') as file:
        json.dump(json_output_v2, file)

    # Display the first 500 characters of the JSON output for preview
    print(json_output_v2)
