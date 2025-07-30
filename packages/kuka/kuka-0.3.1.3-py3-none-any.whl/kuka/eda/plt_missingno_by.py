import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from .. import utils

@utils.__input_type_validation
def plt_missingno_by(
    df = pd.DataFrame(),
    variable = [],
    by = '',
    consider_none = True,
    consider_zeros = True,
    library = 'plotly or matplotlib',
    matplotlib_figsize = 'default', #[width, height]
    matplotlib_bar_space = 0.8,
    matplotlib_colors = 'default',
    
    _input_type_dict = {
        'df': pd.DataFrame,
        'variable': list,
        'by': str,
        'consider_none': bool,
        'consider_zeros': bool,
        'library': str,
        'matplotlib_figsize': (str, list), #[width, height]
        'matplotlib_bar_space': (int, float),
        'matplotlib_colors': (str, list),
    }
    
    ) -> object:
  '''
  Plotar a qtd de valores existentes da variavel="variable" para cada classe da variável "by"

  OBS.:
  - A espessura das barras é controlada pela largura (width) da figura
  '''
  df = df.copy()

  if (library=='plotly'):
    #https://plotly.com/python/histograms/
    import plotly.graph_objects as go

    fig = go.Figure()

    #Filtrar apenas as linha que possuem dados de "variavel"
    for i in variable:

      if (consider_none==False):
        df.loc[ df[i]=='none', i ] = np.nan
        df.loc[ df[i]=='None', i ] = np.nan

      if (consider_zeros==False):
        df.loc[ df[i]==0, i ] = np.nan

      df_aux = df.loc[ df[i].notna(), by ]

      fig.add_trace(go.Histogram(
          x=df_aux,
          histnorm='',
          name=i, # name used in legend and hover labels
          #marker_color='#EB89B5',
          #opacity=0.75
          ))

    fig.update_layout(
        title_text=f'Quantity of data by each {by}', # title of plot
        xaxis_title_text=by, # xaxis label
        yaxis_title_text='Count', # yaxis label
        bargap=0.2, # gap between bars of adjacent location coordinates
        bargroupgap=0.1 # gap between bars of the same location coordinates
        )

    fig.show()

    return fig

  elif (library=='matplotlib'): #https://matplotlib.org/stable/gallery/lines_bars_and_markers/barchart.html#sphx-glr-gallery-lines-bars-and-markers-barchart-py

    matplotlib_width_bar = 1
    unique_by = df[by].unique()

    #Definir as CORES para cada valor único da variável "by".
    #Caso houver mais valores que o tamanho de "colors_reference", as cores serão repetidas:
    if (matplotlib_colors=='default'):
      matplotlib_colors = ['tab:blue','tab:orange','tab:green','tab:red','tab:purple','tab:brown','tab:pink','tab:gray','tab:olive','tab:cyan'] #Tableau Palette
    count, colors = (0, [])
    for i in range(len(variable)):
      colors += [matplotlib_colors[count]]
      count += 1
      if (count==len(matplotlib_colors)):
        count = 0
    print(colors)

    # tamanho da Figura #
    if (matplotlib_figsize=='default'):
      figsize_height = ( 0.35*len(variable) + matplotlib_bar_space )*len(unique_by) + 1
      matplotlib_figsize = [figsize_height, 4.8]
    print('figsize=',matplotlib_figsize)
    fig, ax = plt.subplots(figsize=matplotlib_figsize)
    # tamanho da Figura #

    x = np.arange(len(unique_by))*( len(variable)+matplotlib_bar_space )*matplotlib_width_bar# the label locations
    multiplier = 0

    for i in variable:

      measurement = [0]*len(unique_by)
      for j,count in zip( unique_by, np.arange(len(unique_by)) ):
        measurement[count] = df.loc[ df[by]==j, i ].dropna().size

      offset = matplotlib_width_bar * multiplier
      graph = ax.bar(x + offset,
                     measurement,
                     matplotlib_width_bar,
                     label=i,
                     color=colors[multiplier])
      ax.bar_label(graph,
                   #fontsize=11,
                   padding=3)

      multiplier += 1

    ax.set_ylabel('Frequência')
    ax.set_xticks(x + (len(variable) - 1)*matplotlib_width_bar*0.5, unique_by)
    ax.legend(loc='best')
    return fig, ax

  else:
    print('Escolha uma biblioteca')