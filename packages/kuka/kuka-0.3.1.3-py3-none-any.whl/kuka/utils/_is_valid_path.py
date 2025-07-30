from pathlib import Path
import re
import os

from . import _input_function_validation

_input_type_dict = {
    'path_str': ( str, None ),
    'type_path': ( str, 'pattern', ['file', 'dir'] ),
    'check_only_syntax': ( bool, None ),
    }

@_input_function_validation(_input_type_dict)
def _is_valid_path(path_str, type_path = 'file or dir', check_only_syntax=False):
    """
    Checks whether a given string is a valid path to an EXISTING file or directory.

    This function validates whether `path_str` is a properly formatted string that can
    represent a file or directory path on the current operating system. It checks:
    - That it is a non-empty string
    - That it does not contain invalid characters (especially on Windows)
    - That backslashes are used correctly (e.g., allows network paths like \\\\server)
    - That it points to an existing file or directory, depending on `type_path`

    Args:
        path_str (str): The path string to validate.
        type_path (str): The type of path to validate. Accepts:
            - "file": to check if it's an existing file
            - "dir": to check if it's an existing directory

    Returns:
        bool: `True` if `path_str` is a valid and existing path of the specified type,
        `False` otherwise.

    Examples:
        __is_valid_path("data/model.pkl", type_path="file")
        __is_valid_path("data/", type_path="dir")
    """ 
    
    # Ensure that is a string
    if not isinstance(path_str, str):
        return False
    
    # Ensure that is not empty
    if not path_str.strip():
        return False
    
    # Check if exists invalid characters (Windows)
    if os.name == 'nt':
        if re.search(r'[<>"|?*]', path_str):
            return False
        
        if not(Path(path_str).is_absolute()):
            if re.search(r'[:]', str(path_str)):
                return False
        
    # Check the presence of "\"
    if "\\" in path_str and not path_str.startswith("\\\\"):  # tolerates network \\server
        return False
    
    # Create a Path object
    path_str = Path(path_str)

    if not(check_only_syntax):
        msg = 'TypeError: set a valid value for `type_path`. "file" or "dir"'
        assert (type_path != 'file or dir') and ( (type_path=='file') or (type_path=='dir') ) , msg

        if type_path=='file':
            return path_str.is_file()
        elif type_path=='dir':
            return path_str.is_dir()
    else:
        return True
