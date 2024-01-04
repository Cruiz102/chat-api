import re
import builtins
from typing import Set, List, Tuple
import os

def extract_function_calls(function_body: str) -> Set[str]:
    """
    Extracts all the functions called inside another python function.

    Parameters:
    - function_body (str): A string containing the body of a function.

    Returns:
    - Set[str]: A set of extracted function call names.

    Raises:
    - ValueError: If a function definition is found within the function body.
    """
    # Check for function definition inside the body
    if re.search(r'\bdef\s+[a-zA-Z_][a-zA-Z_0-9]*\s*\(', function_body):
        raise ValueError("Function definition detected in function body. This function expects only the body of another function, not a full function definition.")
    
    # Extract function calls
    pattern = r'\b([a-zA-Z_][a-zA-Z_0-9]*)\s*\('
    return set(re.findall(pattern, function_body))


def filter_out_library_and_builtin_calls(function_calls: Set[str], library_aliases: List[str]) -> Set[str]:
    """
    Filters out function calls that are either built-in or from specified libraries.

    Parameters:
    - function_calls (Set[str]): A set of function call names.
    - library_aliases (List[str]): A list of library aliases to filter out.

    Returns:
    - Set[str]: A set of function call names after filtering out built-ins and specified libraries.
    """
    builtin_functions = {func for func in dir(builtins) if callable(getattr(builtins, func))}
    return {call for call in function_calls if call not in builtin_functions and not any(call.startswith(alias + '.') for alias in library_aliases)}

def analyze_function_code(function_code: str, library_aliases: List[str]) -> Tuple[str, Set[str]]:
    """
    Analyzes a single function's code to extract and filter function calls.

    Parameters:
    - function_code (str): A string containing the code of a single function.
    - library_aliases (List[str]): A list of library aliases to filter out.

    Returns:
    - Tuple[str, Set[str]]: A tuple containing the cleaned function body and a set of non-library, non-built-in function calls.
    """
    lines = function_code.split('\n')
    function_body_lines = [line for line in lines if line.startswith('    ')]

    function_body_cleaned = '\n'.join(function_body_lines)
    function_calls = extract_function_calls(function_body_cleaned)
    non_library_builtin_calls = filter_out_library_and_builtin_calls(function_calls, library_aliases)

    return function_body_cleaned, non_library_builtin_calls

def get_code_functions(code: str, library_aliases: List[str]) -> List[Tuple[str, str, Set[str]]]:
    """
    Given the text of a python file and a list of the libraries  of the functions we want to exclude
    is going to retrieve a list of the functions in the file with the given descriptions. The set of 
    the functions will also exclude the built-in functions.

     - Functions Definitions : String
     - Function content : String
     - A collection of the functions used inside this function: Set[Strings]


     EXAMPLE:
    Python code

     ```
    import numpy as np
     import torch

     def foo():
        array = np.array([1,2,3])
        torch = torch.tensor([1,2,3])
        print(array, torch)

     ```


    get_code_functions(file_text, ["np"])

    Result:
    ['foo', 
    '''
    array = np.array([1,2,3])
    torch = torch.tensor([1,2,3])
    print(array, torch)
    ''',

    "{tensor}"
    ]


    Parameters:
    - code (str): A string containing the full code to analyze.
    - library_aliases (List[str]): A list of library aliases to filter out.

    Returns:
    - List[Tuple[str, str, Set[str]]]: A list of tuples, each containing the function definition, the cleaned function body, and a set of non-library, non-built-in function calls.
    """
    function_pattern = r"""
        (def\s+                   # Match 'def ' keyword
        [a-zA-Z_][a-zA-Z_0-9]*    # Function name
        \s*\([^)]*\)              # Match parameters within parentheses
        (?:\s*->\s*[^\s:]+)?      # Optionally match return arrow (->) and return type
        \s*:\s*\n)                # Match colon and newline
        ([\s\S]+?)                # Match all following content (non-greedy match)
        (?=^\s*def\s|\Z)          # Lookahead for next 'def' or end of string
    """

    results = []
    function_matches = re.finditer(function_pattern, code, re.VERBOSE | re.MULTILINE)

    for match in function_matches:
        function_definition = match.group(1)
        function_body = match.group(2)

        body_cleaned, non_library_builtin_calls = analyze_function_code(function_body, library_aliases)
        results.append((function_definition, body_cleaned, non_library_builtin_calls))

    return results





def get_code_functions_from_path(file_path: str, library_aliases: List[str]) -> List[Tuple[str, str, Set[str]]]:
    """
    Reads a Python file from the given path and analyzes it.

    Parameters:
    - file_path (str): The path to the Python file to be analyzed.
    - library_aliases (List[str]): A list of library aliases to filter out.

    Returns:
    - List[Tuple[str, str, Set[str]]]: A list of tuples, each containing the function definition, the cleaned function body, and a set of non-library, non-built-in function calls, or an empty list in case of file read errors.
    """
    try:
        with open(file_path, 'r') as file:
            code = file.read()
        return get_code_functions(code, library_aliases)
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return []
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return []


def process_python_files_in_directory(directory_path: str, library_aliases: List[str]) -> List[Tuple[str, str, Set[str]]]:
    """
    Traverses through a directory recursively and processes all Python files.

    Parameters:
    - directory_path (str): The path to the directory to be traversed.
    - library_aliases (List[str]): A list of library aliases to filter out.

    Returns:
    - List[Tuple[str, str, Set[str]]]: A combined list of tuples from all processed Python files,
      each tuple containing the function definition, the cleaned function body, and a set of non-library,
      non-built-in function calls, or an empty list in case of file read errors.
    """
    results = []
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                file_results = get_code_functions_from_path(file_path, library_aliases)
                results.extend(file_results)
    return results

# Example usage
directory_path = '/home/cesarruiz/Projects/mojo_code/graph_text.py'  # Replace with the actual directory path
library_aliases = ['np', 'torch']  # Assuming np and torch are the libraries you want to filter out

all_results = get_code_functions_from_path(directory_path, library_aliases)
print(len(all_results))
for result in all_results:
    function_definition, function_body, non_library_builtin_calls = result
    print("Function Definition:", function_definition)
    print("Function Body:\n", function_body)
    print("Non-Library and Non-Built-In Function Calls:", non_library_builtin_calls)
    print("----")