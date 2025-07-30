import pandas as pd
from .. import utils


@utils.__input_type_validation
def Zscores(
    df_for_scaled,
    df_reference,
    
    _input_type_dict = {
            'df_for_scaled': pd.DataFrame,
            'df_reference': pd.DataFrame,
            }

    ) -> dict:
  '''
  Escalonar cada coluna de um DataFrame utilizando o "z score"
  '''
  if (any(df_for_scaled.columns != df_reference.columns)):
    print('Zscores function: Dataframes com colunas diferentes')
    return

  Zscores_dict = {}
  print(f'Zscores function: columns_reference = {df_reference.columns}')
  for i in df_for_scaled.columns:
    if (df_for_scaled[i].dtype!=object):
      Zscores_dict[i] = {}
      Zscores_dict[i]['mean'] = df_reference[i].mean()
      Zscores_dict[i]['std'] = df_reference[i].std()
      df_for_scaled[i] = (df_for_scaled[i] - Zscores_dict[i]['mean']) / Zscores_dict[i]['std']
  return Zscores_dict



@utils.__input_type_validation
def Zscores_with_param(
  df_real, 
  dict_params,
  
  _input_type_dict = {
            'df_real': pd.DataFrame,
            'dict_params': dict,
            }

  ) -> pd.DataFrame:
  '''
  Aplicar o escalonamento zscore para cada coluna de um DataFrame a partir dos parametros 
  (média e desvio padrão)

  If the variable is an "np.array", its necessary to convert it to a "DataFrame".

  Example of dict_params:
  dict_params = {
    'columns_dataframe_name1': {'mean':'mean_value1', 'std':'std_value1'},
    'columns_dataframe_name2': {'mean':'mean_value2', 'std':'std_value2'},
    'columns_dataframe_name3': {'mean':'mean_value3', 'std':'std_value3'}
  }
  '''
  df_scaled = df_real.copy()

  for i in df_scaled.columns:
    if i not in dict_params.keys():
      print('There is a DataFrame column that is not in dict_params')
      return

  print(f'Zscores function: columns_reference = {df_real.columns}')
  for i in df_scaled.columns:
    if (df_scaled[i].dtype!=object):
      df_scaled[i] = (df_scaled[i] - dict_params[i]['mean']) / dict_params[i]['std']
  return df_scaled



@utils.__input_type_validation
def undo_Zscores(
  df_scaled,
  df_reference,
  
  _input_type_dict = {
            'df_scaled': pd.DataFrame,
            'df_reference': pd.DataFrame,
            }
  
  ) -> None:
  '''
  desfazer o escalonamento realizado para cada coluna de um DataFrame utilizando
  o "z score"
  '''

  if (any(df_scaled.columns != df_reference.columns)):
    print('undo_Zscores function: Dataframes com colunas diferentes')
    return

  print(f'undo_Zscores function: columns_reference = {df_reference.columns}')
  for i in df_scaled.columns:
    if (df_scaled[i].dtype!=object):
      df_scaled[i] = df_scaled[i]*df_reference[i].std() + df_reference[i].mean()
  #return df_scaled



@utils.__input_type_validation
def undo_Zscores_with_param(
  df_scaled, 
  dict_params,
  
  _input_type_dict = {
            'df_scaled': pd.DataFrame,
            'dict_params': dict,
            }
  
  ) -> pd.DataFrame:
  '''
  desfazer o escalonamento realizado para cada coluna de um DataFrame utilizando
  o "z score" a partir dos parametros

  If the variable is an "np.array", its necessary to convert it to a "DataFrame".

  Example of dict_params:
  dict_params = {
    'columns_dataframe_name1': {'mean':'mean_value1', 'std':'std_value1'},
    'columns_dataframe_name2': {'mean':'mean_value2', 'std':'std_value2'},
    'columns_dataframe_name3': {'mean':'mean_value3', 'std':'std_value3'}
  }
  '''
  df_real = df_scaled.copy()

  for i in df_real.columns:
    if i not in dict_params.keys():
      print('There is a DataFrame column that is not in dict_params')
      return

  print(f'undo_Zscores function: columns_reference = {df_real.columns}')
  for i in df_real.columns:
    if (df_real[i].dtype!=object):
      df_real[i] = df_real[i]*dict_params[i]['std'] + dict_params[i]['mean']
  return df_real



@utils.__input_type_validation
def normalize(
  df_for_norm,
  df_reference,
  
  _input_type_dict = {
            'df_for_norm': pd.DataFrame,
            'df_reference': pd.DataFrame,
            }
  
  ) -> None:
  '''
  Normalizar cada coluna de um DataFrame
  '''
  if (any(df_for_norm.columns != df_reference.columns)):
    print('normalize function: Dataframes com colunas diferentes')
    return

  print(f'normalize function: columns_reference: {df_reference.columns}')
  for i in df_for_norm.columns:
    if (df_for_norm[i].dtype!=object):
      df_for_norm[i] = (df_for_norm[i] - df_reference[i].min()) / (df_reference[i].max() - df_reference[i].min())
  #return df_for_norm


@utils.__input_type_validation
def undo_normalize(
  df_normalized,
  df_reference,

  _input_type_dict = {
            'df_normalized': pd.DataFrame,
            'df_reference': pd.DataFrame,
            }

  ) -> None:
  '''
  desfazer a normalização realizada para cada coluna de um DataFrame
  '''
  if (any(df_normalized.columns != df_reference.columns)):
    print('undo_normalize function: Dataframes com colunas diferentes')
    return

  print(f'undo_normalize function: columns_reference: {df_reference.columns}')
  for i in df_normalized.columns:
    if (df_normalized[i].dtype!=object):
      df_normalized[i] = df_normalized[i]*(df_reference[i].max() - df_reference[i].min()) + df_reference[i].min()
  #return df_normalized