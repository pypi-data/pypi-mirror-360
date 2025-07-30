import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from .. import utils

@utils.__input_type_validation
def heatmap_corr(
    df,
    x='all',
    y='all',
    method='pearson',
    min_periods=1,
    color='di',

    _input_type_dict = {
        'df': pd.DataFrame,
        'x': (str, list, str),
        'y': (str, list, str),
        'method': str,
        'min_periods': int,
        'color': str,
    }

    ) -> pd.DataFrame :

  df = df.loc[:, x+y]
  corr_pear = df.corr( min_periods=min_periods, method=method )

  if (x=='all'):
    x = corr_pear.columns.tolist()
    
  if (y=='all'):
    y = corr_pear.columns.tolist()

  heatmap_pearson = pd.DataFrame( columns=x, index=y )
  heatmap_pearson = corr_pear.loc[y,x]

    #GRAFICO#
  f, ax = plt.subplots(figsize=( 1*len(x)+3, 1*len(y) ))
  if color=='mono':
    colors = ('#00076e', '#1b00ff', '#d0cbff', '#FFFFFF', '#d0cbff', '#1b00ff', '#00076e')
  elif (color=='di'):
    colors = ('#7e0000', '#ff0000', '#fecfcf', '#FFFFFF', '#d0cbff', '#1b00ff', '#00076e')
  cmap = sns.blend_palette(colors, input='rgb', as_cmap=True)
  sns.heatmap(heatmap_pearson, annot=True, cmap=cmap, ax=ax, center=0)

  return heatmap_pearson