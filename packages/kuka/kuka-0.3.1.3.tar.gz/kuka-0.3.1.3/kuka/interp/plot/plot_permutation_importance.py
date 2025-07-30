import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from ..importance import permutation_importance
from .. import utils

@utils.__input_type_validation
def plot_permutation_importance(
    model,
    x_val, #DataFrame
    y_val, #DataFrame
    scoring='r2_score',
    n_repeats = 30,
    height = 0.8,
    espaco_colunas = 0.2,
    figsize = [6.4, 4.8],
    separar_por_cor = False,
    bycolor = 'dict',
    bar_labels = False,
    fontsize_bar_labels = 10,
    
    _input_type_dict = {
      'model': object,
      'x_val': pd.DataFrame, #DataFrame
      'y_val': pd.DataFrame, #DataFrame
      'scoring': str,
      'n_repeats': int,
      'height': (int, float),
      'espaco_colunas': (int, float),
      'figsize': (list, tuple),
      'separar_por_cor': bool,
      'bycolor': dict,
      'bar_labels': bool,
      'fontsize_bar_labels': (int, float),
    },
    
    ) -> tuple:
  '''
  Exemplo para variável "bycolor"

  bycolor = {'variável1':'color1',
             'variável2':'color1',
             'variável3':'color3',
             'variável4':'color1',
             'variável5':'color3',}

  '''
  x_val_columns = x_val.columns

  color = dict(zip(x_val_columns,[sns.color_palette("tab10")[0]]*len(x_val_columns))) if separar_por_cor==False else bycolor

  #https://medium.com/horadecodar/gr%C3%A1ficos-de-barra-com-matplotlib-85628bfc4351#:~:text=barh()%3A,os%20seguintes%20par%C3%A2metros%3A

  r = permutation_importance(
    model, x_val, y_val,
    n_repeats=n_repeats,
    scoring=scoring
    )

  importancias = pd.DataFrame( columns=['mean','std'] )

  # Filter out amounts greater than 2*std
  for i in r['importances_mean'].argsort()[::-1]:
    if r['importances_mean'][i] - 2 * r['importances_std'][i] > 0:
      importancias.loc[x_val_columns[i]] = [r['importances_mean'][i], r['importances_std'][i]]

  fig, ax = plt.subplots( figsize = figsize)

  y_pos = np.arange(0, len(importancias.index)*(height+espaco_colunas), height+espaco_colunas)

  for i,column in enumerate(importancias.index):
    ax.barh(y_pos[i],
            importancias['mean'].iloc[i],
            height = height,
            xerr=importancias['std'].iloc[i],
            align='center',
            color=color[column])

  ax.set_yticks(y_pos, labels=importancias.index)

  ax.set_xlabel('Importância (a.u.)')

  if bar_labels == True:

    for i,column in enumerate(importancias.index):
      ax.annotate(round(importancias['mean'].iloc[i],2),
                xy=(importancias['mean'].iloc[i], y_pos[i]),
                xytext=(20,2), # 5 points vertical offset
                textcoords="offset points",
                ha='center', va='bottom',
                #fontsize=15,
                rotation=0,
                fontsize=fontsize_bar_labels
                )

  return importancias, (fig, ax)