
import pandas as pd
import numpy as np
from .. import utils

@utils.__input_type_validation
def str2int_simple_encoder(
  df,
  columns='all',
  
  _input_type_dict = {
    'df': pd.DataFrame,
    'columns': (str, list, tuple),
    }
  
  ) -> dict:

  id_dict = {}
  if (columns=='all'):

    for i in df.columns:
      if (df[i].dtype==object):
        id_dict[i] = {}
        unique_values = df[i].unique()
        id_dict[i] = {name: id + 1 for id, name in enumerate(unique_values)}

        df[i] = df[i].apply(lambda row, value : value[row], value = id_dict[i] )

  else:

    for i in columns:
      if ( (df[i].dtype==object) and (i in df.columns) ):
        id_dict[i] = {}
        unique_values = df[i].unique()
        id_dict[i] = {name: id + 1 for id, name in enumerate(unique_values)}

        df[i] = df[i].apply(lambda row, value : value[row], value = id_dict[i] )
      else:
        print('str2int_simple_encoder: coluna especificada não é do tipo "object" ou não existe no dataframe')
        return

  return id_dict



@utils.__input_type_validation
def str2int_hot_encoder(
  df,
  columns='all',
  
  _input_type_dict = {
    'df': pd.DataFrame,
    'columns': (str, list, tuple),
    }
  
  ) -> dict:

  id_dict = {}

  if (columns=='all'):
    columns = []
    for i in df.columns:
      if (df[i].dtype==object):
        columns += [i]

  for i in columns:
    if ( (df[i].dtype==object) and (i in df.columns) ):
      id_dict[i] = {}
      unique_values = df[i].unique()
      for id,name in enumerate(unique_values):
        aux = [0]*(len(unique_values)-1)
        aux.insert(id,1)
        id_dict[i][name] = aux

      transformed_column = df[i].apply(lambda row, value : value[row], value = id_dict[i] )

      new_colunms = []
      for count,category in enumerate(id_dict[i].keys()): #value = valores categoricos da coluna 'i'
        new_colunms += [i+'_'+category]
        df.insert( df.columns.get_loc(i) + count +1, new_colunms[count], np.nan)

      df.drop( [i], axis=1, inplace=True )

      for index in transformed_column.index:
        df.loc[index, new_colunms] = transformed_column[index]

    else:
      print('str2int_simple_encoder: coluna especificada não é do tipo "object" ou não existe no dataframe')
      return

  return id_dict