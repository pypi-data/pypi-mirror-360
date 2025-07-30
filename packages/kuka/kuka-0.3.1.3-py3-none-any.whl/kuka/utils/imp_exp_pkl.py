import pickle
import os
import datetime

from .. import utils

_input_type_dict1 = {
						'path': (str, None),
						}

@utils._input_function_validation(_input_type_dict1)
def import_pkl(
		path,

		) -> object:
	
	'''
	This function returns a an variable after define it according to a pickle file in "path".
	"path" NEEDS contain the name of the file.
	'''

	with open( path, 'rb') as f:
		variable = pickle.load(f)
		print('Imported variable:',type(variable))

	return variable






_input_type_dict2 = {
		'variable': (object, None),
		'path': (str, None),
		}

@utils._input_function_validation(_input_type_dict2)
def export_pkl(
	variable,
	path = 'default', #path for store the variable

		) -> None:
	'''
	This function exports a variable of python as pickle file to the "path".
	"path" NEEDS contain the name of the file.
	'''

	time = datetime.datetime.now()

	if path == 'default':
				filename = f"var_{time.strftime('%Y_%m_%d_%Hh%Mmin_%S_%f')}.pkl"
				path = os.path.join(os.getcwd(), filename)

	with open( path, 'wb' ) as f:
		pickle.dump( variable, f)
		print('Exported variable:',type(variable))