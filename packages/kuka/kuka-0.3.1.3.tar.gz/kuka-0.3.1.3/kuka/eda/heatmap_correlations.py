from scipy.stats import pearsonr
from scipy.stats import spearmanr
from matplotlib import rcParams
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from .. import utils

@utils.__input_type_validation
def heatmap_correlations(
    method = 'pearson or spearman',
    df = 'pandas_DataFrame',
    x = 'all',
    y = 'all',
    allow_duplicates = True,
    color = 'di',
    graphic = 'coeff',
    min_periods = 2,
    figsize = 'default',
    use_external_fig_and_ax = False,
    external_fig_and_ax = 'tuple of fig and ax, respectively',
    verbose_n_periods=False,
    
    _input_type_dict = {
        'method': str,
        'df': pd.DataFrame,
        'x': (str, list, tuple),
        'y': (str, list, tuple),
        'allow_duplicates': bool,
        'color': str,
        'graphic': str,
        'min_periods': int,
        'figsize': (str, list, tuple),
        'use_external_fig_and_ax': bool,
        'external_fig_and_ax': (list, tuple),
        'verbose_n_periods': bool,
    },

    **kwargs_heatmap
    
    ) -> object:

  
  '''
  URGENTLY NEEDED OPTIMIZATION
  Returns a heatmap plot with pearson's coefficients or their p-values.

  method    = "pearson" or "spearman"
  df      = Dataframe
  x and y = list of x and y heatmap columns/axis
  color   = "di" or "mono"
  graphic = "coeff" or "pvalue"
  '''
  if (x=='all'):
    x = df.columns

  # converter colunas numéricas para "float"
  float_df_columnsx = []
  for i in x:
    try:
      df[i] = df[i].astype(float)
    except:
      print(f'heatmap_pearson function: X column "{i}" is a {df[i].dtype}')
    else:
      float_df_columnsx += [i]
  x = float_df_columnsx


  if (y=='all'):
    y = df.columns

  # converter colunas numéricas para "float"
  float_df_columnsy = []
  for i in y:
    try:
      df[i] = df[i].astype(float)
    except:
      print(f'heatmap_pearson function: Y column "{i}" is a {df[i].dtype}')
    else:
      float_df_columnsy += [i]
  y = float_df_columnsy


  coeff_heatmap = pd.DataFrame( columns=x, index=y, dtype=float)
  pvalue_heatmap = pd.DataFrame( columns=x, index=y, dtype=float )
  for i in x: #columns
    #print(i)
    for j in y: #index
      df_aux = df[[i,j]].dropna()

      #Retirar duplicadas nas coordenadas de "df_aux"
      if (allow_duplicates==False):
        old_df = df_aux
        new_df = pd.DataFrame( columns=[i,j] )
        lines_new_df = []
        for index in old_df.index:
          line_old_df = f'{df.loc[index,i]} {df.loc[index,j]}'
          if not(line_old_df in lines_new_df):
            lines_new_df += [line_old_df]
            new_df.loc[index, [i,j] ] = old_df.loc[index, [i,j]]
        df_aux = new_df

      if (df_aux.shape[0]==0):
        coeff_heatmap.loc[j,i], pvalue_heatmap.loc[j,i] = (np.nan, np.nan)
        continue
      columnx = df_aux.iloc[:,0]
      columny = df_aux.iloc[:,1]

      if (columnx.shape[0]>=min_periods):
        if method=='pearson': coeff_heatmap.loc[j,i], pvalue_heatmap.loc[j,i] = pearsonr( columnx, columny )
        if method=='spearman': coeff_heatmap.loc[j,i], pvalue_heatmap.loc[j,i] = spearmanr( columnx, columny )
        if verbose_n_periods==True: print(i, 'n=', columnx.shape[0])
      else:
        coeff_heatmap.loc[j,i], pvalue_heatmap.loc[j,i] = (np.nan, np.nan)

  ## GRAFICO ##
  if (graphic=='coeff'):
    graphic = np.around(coeff_heatmap,2)
  elif (graphic=='pvalue'):
    graphic = np.around(pvalue_heatmap,3)

  if (use_external_fig_and_ax == False):
    if figsize=='default':
      fig, ax = plt.subplots(figsize=( 1*len(x)+3, 1*len(y) ))
    else:
      fig, ax = plt.subplots( figsize=figsize )
  if (use_external_fig_and_ax == True):
      fig, ax = external_fig_and_ax

  if color=='mono':
    colors = ('#00076e', '#1b00ff', '#d0cbff', '#FFFFFF', '#d0cbff', '#1b00ff', '#00076e')
  elif (color=='di'):
    colors = ('#7e0000', '#ff0000', '#fecfcf', '#FFFFFF', '#d0cbff', '#1b00ff', '#00076e')
  cmap = sns.blend_palette(colors, input='rgb', as_cmap=True)
  sns.heatmap( graphic, annot=True, cmap=cmap, ax=ax, center=0, **kwargs_heatmap)

  return fig, ax, (coeff_heatmap, pvalue_heatmap)