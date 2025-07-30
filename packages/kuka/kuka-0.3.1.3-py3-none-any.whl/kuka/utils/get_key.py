from .. import utils

_input_type_dict = {
            'val': (object, None),
            'my_dict': (dict, None),
            'default': (object, None),
            }

@utils._input_function_validation(_input_type_dict)
def get_key(
        val, my_dict,
        default=None,        
        ) -> list: #dict = key : value
    
    '''
    Given a certain "value" in a dictionary, what is the "key" associated with it?

    Returns the key associated with a specific value in a dictionary.
    
    Args:
        val: The value to search for in the dictionary.
        my_dict: The dictionary to search in.
        default: The value to return if the value is not found (default: None).
        
    Returns:
        The key associated with the value if found, otherwise the default value.
        
    Examples:
        >>> get_key(2, {'a': 1, 'b': 2, 'c': 3})
        'b'
        >>> get_key(5, {'a': 1, 'b': 2, 'c': 3}, "Not found")
        'Not found'
    '''

    # Handle case where value appears multiple times
    keys = [k for k, v in my_dict.items() if v == val]
    
    if keys:
        return keys[:]  # Return the matching key(s)

    return default