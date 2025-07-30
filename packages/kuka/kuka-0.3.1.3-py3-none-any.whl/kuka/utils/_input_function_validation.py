
import functools

################### FOR ADD MORE VALIDATION MODES, EDIT THE CODES WITH THE FOLLOWING WARNING: ####################
##################################################################################################################
###################### ------------------------- VALIDATION MODES ------------------------- ######################
##################################################################################################################

def _input_val_dict_has_valid_format(
		_input_val_dict:dict, #dict with the validation protocol
		list_validation_modes:list #list of the validation modes
		) -> None:
	
	# key -> string || value -> tuple or list
	# _input_val_dict[k][0] -> var_types
	# _input_val_dict[k][1] -> validation_mode (restrict values)
	# _input_val_dict[k][2] -> validation_parameters (ruled by validation_mode)

	msg = f'INPUT VALIDATION FUNCTION: "_input_function_validation" invalid input format. See function signature.\nERROR: '
	for k, v in _input_val_dict.items():
		if isinstance(k,str) and isinstance(v, (tuple,list)):
			if (v[1] in list_validation_modes):
				is_none = v[1] in [None, 'none']
				if not(is_none):
					##################################################################################################################
					###################### ------------------------- VALIDATION MODES ------------------------- ######################
					##################################################################################################################
					# rules for the parameters (v[2]) shape/format of each validation mode (v[1])
					if len(v)==3:
						if v[1] == 'pattern':
							if not(isinstance(v[2], (list,tuple))):
								raise ValueError(msg+f'"{v[2]}" of key "{k}" is not a tuple or list')
						elif v[1] == 'range':
							if not(isinstance(v[2], (list,tuple))) or not(len(v[2])==2):
								raise ValueError(msg+f'"{v[2]}" of key "{k}" is not a tuple or list or has an invalid length (!=2)')
						elif v[1]=='length':
							if not(isinstance(v[2], (int))):
								raise ValueError(msg+f'"{v[2]}" of key "{k}" is not a integer')

					else:
						raise ValueError(msg+f'"{v[1]}" of key "{k}" asks for parameters')
				elif is_none:
					pass
				else:
					raise ValueError(msg+f'Invalid length of value ({len(v)}) for the key "{k}".')		
			else:
				raise ValueError(msg+f'"value "{v[1]}" of key "{k}" is outside of range "{list_validation_modes}"')
		else:
			raise ValueError(msg+f'keys ({k}) or values ({v}) with invalid types ')


def _validation_of_decorator_dicts(
        input_dict: dict, #dict with the arguments of the function
		_input_val_dict:dict #dict with the validation protocol
	) -> None:

	'''check if all input_dict.keys() exists in _input_val_dict.keys()'''

	keys_input_val = list(_input_val_dict.keys())
	msg = f'INPUT VALIDATION ERROR: Some "input_dict" key are not present in validation protocol "_input_val_dict"'
	for k in input_dict.keys():
		assert k in keys_input_val, msg


def _type_validation(
		input_dict: dict, #dict with the arguments of the function
		_input_val_dict:dict #dict with the validation protocol
	) -> None:

	'''check if all input_dict.values() matches with "_input_val_dict" description types'''

	for k, v in input_dict.items():
		msg = f'VALIDATION TYPE ERROR: The argument "{k}" (type {type(v)}) is not of type {_input_val_dict[k][0]} (defined in function decorator).'
		assert isinstance(v, _input_val_dict[k][0]), msg


def _value_validation(
		input_dict: dict, #dict with the arguments of the function
		_input_val_dict:dict #dict with the validation protocol
	) -> None:

	'''check if all input_dict.values() match the "validation_parameters" ruled by "validation_mode"'''

	for k, v in input_dict.items():
		validation_mode = _input_val_dict[k][1]

		##################################################################################################################
		###################### ------------------------- VALIDATION MODES ------------------------- ######################
		##################################################################################################################
		# Rules for the v (values) of the k (parameters)
		if (validation_mode is None) or (validation_mode=='none'):
			continue

		validation_parameters = _input_val_dict[k][2]

		if (validation_mode=='pattern'):
			msg = f'INPUT VALIDATION ERROR: "{k}" value "{v}" is outside of range "{validation_parameters}"'
			assert v in validation_parameters, msg
		elif (validation_mode=='range'):
			msg = f'INPUT VALIDATION ERROR: "{k}" value "{v}" is outside of range "{validation_parameters}"'
			check = (v >= validation_parameters[0]) and (v <= validation_parameters[1])
			assert check, msg
		elif (validation_mode=='length'):
			msg = f'INPUT VALIDATION ERROR: "{k}" value "{v}" is not a list/tuple/str OR has a length not equal to "{validation_parameters}"'
			check = isinstance(v, (list,tuple,str)) and (len(v) == validation_parameters)
			assert check, msg



def _input_function_validation(
		_input_val_dict:dict,
		) -> None:
	'''
	Decorator to validate the inputs of a function based on a validation protocol dictionary.

	This decorator is used to automatically check both the **types** and **values** of the input arguments
	passed to a function. It relies on a user-defined dictionary (`_input_val_dict`) which describes the expected
	input types and any additional validation rules.

	Parameters
	----------
	_input_val_dict : dict
		A dictionary that defines the validation rules for each argument.
		The expected format is:
		
		{
			'arg_name': (expected_type(s), validation_mode, validation_parameter),
			...
		}

		- `expected_type(s)`: A type or tuple of types (e.g., `int`, `(int, float)`, `list`, etc.)
		- `validation_mode` (optional): Type of value restriction:
			- `'none'` or `None`: no validation
			- `'pattern'`: value must be in a specific list of accepted values
			- `'range'` : value must be within a numeric range `[min, max]`
			- `'length'`: length of value (must be list/tuple/str) must equal given integer
		- `validation_parameter`: Parameters used in the mode above (e.g., a list of accepted values, a min/max range, or a length)

	Examples
	--------
	```python
	_input_val_dict = {
		'x': (int, 'range', [0, 10]),
		'y': (str, 'pattern', ['a', 'b', 'c']),
		'z': ((list, tuple), 'length', 3)
	}

	@_input_function_validation(_input_val_dict)
	def example(x=0, y='a', z=[1, 2, 3]):
		...
	```
	'''
							##################################################################
	list_validation_modes = [ # <----------- VALIDATION MODES ----------- ######################
		None,				  ##################################################################
		'none', 
		'pattern', 
		'range', 
		'length'
		]
	
	def decorator(func):
		@functools.wraps(func)
		def wrapper(*args, **kwargs):
			######## 0. "_input_val_dict" format validation ########
			_input_val_dict_has_valid_format(_input_val_dict, list_validation_modes)


			######## 1. Get the default arguments from the function signature ########
			# defaults_dict = Variables that are not passed in *args or **kargs, but have a default value difined in function signature
			
			# Gets the names of the arguments of the original function
			# co_varnames = all var names in function | co_argcount = The input arguments of function
			input_names = func.__code__.co_varnames[:func.__code__.co_argcount] 
			# Gets the default values of the arguments (if they exist)
			defaults = func.__defaults__ or ()
			count_defaults = len(defaults)
			# Maps the default arguments to their names. The defaults names are always the last arguments/"input_names" of the function
			defaults_dict = dict(zip(input_names[-count_defaults:], defaults))
			# Remove the kwargs from the defaults_dict
			for key in kwargs.keys():
				defaults_dict.pop(key) if key in defaults_dict else None


			######## 2. Create a dictionary with the args and their names ########
			# The *args names are always the first arguments/"input_names" of the function
			arg_names = input_names[:len(args)]
			args_dict = dict(zip(arg_names, args))

			### 2.1. Remove the agrs from the defaults_dict ####
			# Sometimes default variables are called like the args, 
			# so we need to remove them from the defaults_dict
			defaults_dict = {k: defaults_dict[k] for k in set( defaults_dict.keys() ) - set( args_dict.keys() )}


			######## 3. Merge the dictionaries with ALL the arguments and its values ########
			input_dict = {**args_dict, **kwargs, **defaults_dict}


			######## 4. Update the "_input_val_dict" with not-defined arguments in signature function or ########
			########    with unexplicity validation in _input_val_dict                                   ########
			# Sometimes the function is called with arguments that are not defined in its signature (like *args **kwargs)
			# or the _input_val_dict does not have the validation protocol of some argument.
			foreign_args_keys = list( set( input_dict.keys() ) - set( _input_val_dict.keys() ) )
			#Update the _input_val_dict with the foreign arguments and its object type (generic type) with no restriction:
			_input_val_dict.update({k: (object, None) for k in foreign_args_keys})


			######## 5. Call the function for validate "input_dict" and "_input_val_dict" for the next operations ########
			_validation_of_decorator_dicts(input_dict, _input_val_dict)


			######## 6. Call the function for validate the types ########
			_type_validation(input_dict, _input_val_dict)


			######## 7. Call the function for validate the values of parameters function ########
			_value_validation(input_dict, _input_val_dict)

			return func(*args, **kwargs)
		
		return wrapper
	
	return decorator