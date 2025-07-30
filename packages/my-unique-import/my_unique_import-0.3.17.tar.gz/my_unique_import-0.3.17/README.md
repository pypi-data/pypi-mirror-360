# My Import Package

This package provides custom import functionalities.

## Installation

```bash
pip install my-unique-import
```
## Usage
This package can help with custom module imports, including importing specific functions from modules, getting the location of a module, and setting up paths for module discovery.

## Setting up paths
The setup_paths module allows you to add the project root directory to the Python path dynamically.
```python
from my_import.setup_paths import setup_paths

# Call this function at the beginning of your script
setup_paths()
```

## Custom importer
The custom_importer module provides various utilities for importing modules and functions dynamically.

## Import a specific function from a module
```python
from my_import.custom_importer import import_from

# Import the 'sqrt' function from the 'math' module
sqrt = import_from('math', 'sqrt')
print(sqrt(16))  # Output: 4.0
```
## Import a module
```python
from my_import.custom_importer import import_module

# Import the 'os' module
os_module = import_module('os')
print(os_module.name)  # Output: posix (or 'nt' on Windows)
```
## Get the location of a module
```python
from my_import.custom_importer import get_location

# Get the location of the 'math' module
location = get_location('math')
print(location)  # Output: The file path to the 'math' module
```
Functions
setup_paths
This function adds the project root directory to the Python path dynamically, allowing you to import modules from the project more easily.

import_from
This function allows you to import a specific function from a given module.

Parameters:

module (str): The name of the module.
function (str): The name of the function to import.
Returns:

The imported function.
import_module
This function imports a module dynamically.

Parameters:

name (str): The name of the module to import.
package (str, optional): The package name to use for relative imports.
Returns:

The imported module.
get_location
This function returns the file path to the specified module.

Parameters:

module (str): The name of the module.
Returns:

The file path of the module.
