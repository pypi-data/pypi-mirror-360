from random import sample
import numpy as np
import pandas as pd
from sklearn import metrics


from .. import utils

@utils.__input_type_validation
def permutation_importance(
    model, #sklearn model
    x_val, #numpy array
    y_val, #numpy array
    n_repeats=5, #int, numero de vezes que cada coluna será embaralhada
    scoring='r2',
    
    _input_type_dict = {
      'model': object,
      'x_val': np.ndarray,
      'y_val': np.ndarray,
      'n_repeats': int,
      'scoring': str,
    }
    
    ) -> np.ndarray:
  #https://scikit-learn.org/stable/modules/permutation_importance.html#:~:text=Outline%20of%20the%20permutation%20importance%20algorithm%C2%B6

  #r2 = r2_score
  #f1 = f1_score

  #define the sklearn score
  score = eval('metrics.'+scoring)

  #calcular o score de referência, sem nenhuma coluna embaralhada
  reference_score = score( y_val, model.predict(x_val))

  # quant. de atributos de entrada
  x_val_columns = x_val.columns
  rows_count = x_val.shape[0]

  #Calcular as importancias individuais para cada embaralhamento e guardar numa
  #matrix de tamanho (linhas, colunas) = (n_variables, n_repeats)
  importance_table = {'importances':np.zeros((len(x_val_columns), n_repeats))}
  for i, column in enumerate(x_val_columns):
    importances_column = []
    for k in range(n_repeats):
      input_model = x_val.copy()

      # Cast the column to a numeric type, handling potential errors
      try:
        input_model[column] = pd.to_numeric(input_model[column])
      except ValueError:
        # Handle cases where conversion is not possible, e.g., keep as is or use alternative strategy
        pass

      input_model[column] = sample( sorted(input_model[column]), rows_count)
      ### MODELO ###
      importances_column += [reference_score - score(y_val, model.predict(input_model))]
      ### MODELO ###
    importance_table['importances'][i] += importances_column


  #Calcular a média e desvio padrão das repetições para cada atributo
  importance_table['importances_mean'] = np.mean(importance_table['importances'], axis=1)
  importance_table['importances_std'] = np.std(importance_table['importances'], axis=1)

  return importance_table