import numpy as np
import pandas as pd
from .. import utils

from .metrics import *

@utils.__input_type_validation
def display_score(
    m,
    x_train,
    x_test,
    y_train,
    y_test,
    delog_y=False,
    base=10,
    untransform_y = 'Zscore or normalize',
    dict_params_transform = 'dicionario parametros',
    
    _input_type_dict = {
      'm': object,
      'x_train': np.ndarray,
      'x_test': np.ndarray,
      'y_train': np.ndarray,
      'y_test': np.ndarray,
      'delog_y': bool,
      'base': (int, float),
      'untransform_y': str,
      'dict_params_transform': (dict, str)
    }
    
    ) -> pd.DataFrame:
  '''
  função para avaliar RMSE, R2 e OOB_score de modelos de regressão
  
  Exemplo de dict_params_transform para Zscore:
  dict_params_transform = {'mean':'mean_value_for_target_variable', 'std':'std_value_for_target_variable'}
  Exemplo de dict_params_transform para normalize:
  IMPLEMENTAR AINDA
  '''
  y_train_pred = m.predict(x_train)
  y_test_pred = m.predict(x_test)


  if (untransform_y!='Zscore or normalize'):
    if (untransform_y=='Zscore'):
      y_train_pred = y_train_pred*dict_params_transform['std'] + dict_params_transform['mean']
      y_test_pred = y_test_pred*dict_params_transform['std'] + dict_params_transform['mean']
      y_train = y_train*dict_params_transform['std'] + dict_params_transform['mean']
      y_test = y_test*dict_params_transform['std'] + dict_params_transform['mean']
  if (delog_y==True):
    y_train_pred = np.power(base, y_train_pred)
    y_test_pred = np.power(base, y_test_pred)
    y_train = np.power(base,y_train)
    y_test = np.power(base,y_test)


  # print(r2( y_train,y_train_pred ))
  
  # display(y_train)
  # display(y_train_pred)
  res = [ [rmse( y_train,y_train_pred ), r2( y_train,y_train_pred ),
           mape( y_train,y_train_pred ), c_coeff( y_train,y_train_pred )],
          [rmse( y_test,y_test_pred ), r2( y_test,y_test_pred ),
           mape( y_test,y_test_pred ), c_coeff( y_test,y_test_pred )] ]
           #a função display score irá retornar uma tabela
  
  

  score = pd.DataFrame(res, columns=['RMSE','R2','MAPE','C_coeff'], index = ['Treino','Teste'])

  if hasattr(m, 'oob_score_'): #https://www.programiz.com/python-programming/methods/built-in/hasattr

    if (delog_y==False):
      score.loc['OOB'] = [rmse(y_train, m.oob_prediction_), m.oob_score_,
                          mape(y_train, m.oob_prediction_), c_coeff(y_train,m.oob_prediction_)]
    else:
      y_train_pred = np.power(base, m.oob_prediction_)
      score.loc['OOB'] = [rmse(y_train, y_train_pred), m.oob_score_,
                          mape(y_train, y_train_pred), c_coeff(y_train,y_train_pred)]

  return score