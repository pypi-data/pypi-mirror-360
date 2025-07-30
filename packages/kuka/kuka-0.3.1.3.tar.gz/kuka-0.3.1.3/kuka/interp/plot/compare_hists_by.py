import copy
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from .. import utils

@utils.__input_type_validation
def compare_hists_by(
    df1, 
    df2,
    variable = '',
    by = '',
    df1_name = 'default',
    df2_name = 'default',
    alpha = 0.7,
    bins_hist = 1,
    colors_reference = ['b','g','r','c','m','y','k'],
    figsize = [12.8, 7.2],
    
    _input_type_dict = {
        'df1': pd.DataFrame, 
        'df2': pd.DataFrame,
        'variable': str,
        'by': str,
        'df1_name': str,
        'df2_name': str,
        'alpha': (float, int),
        'bins_hist': int,
        'colors_reference': (list, tuple),
        'figsize': (list, tuple),
    }
    
    ) -> object:
  '''
  "variable" precisa ter valores numéricos.

  Essa função retorna "fig" e "ax" do Matplotlib. Portanto, o gráfico criado pode ser editado
  posteriormente, mesmo com certa limitação.

  A lógica dessa função foi copiada da função "plot_stacked_hist_or_bar_by".
  Para melhor compreender esse cógido, ler antes o código da função "plot_stacked_hist_or_bar_by"
  '''
  fig, ax = plt.subplots( 2, 2, figsize=figsize )
  df1.dropna(subset=[variable], inplace=True)
  df2.dropna(subset=[variable], inplace=True)

  x_range_min = min(df1[variable].min(), df2[variable].min())
  x_range_max = max(df1[variable].max(), df2[variable].max())

  #Achar os valores únicos da variável "by" presentes nos dois dataframes (df1 e df2)
  unique_by = (df1[by].unique().tolist() + df2[by].unique().tolist())
  unique_by = list(dict.fromkeys(unique_by))
  unique_by.sort()
  #Definir as cores para cada valor único da variável "by".
  #Caso houver mais valores que o tamanho de "colors_reference", as cores serão repetidas:
  count, colors = (0, [])
  for i in range(len(unique_by)):
    if (count==len(colors_reference)):
      count = 0
    colors += [colors_reference[count]]
    count += 1

  #Histograma - o dicionário para o "x", "height" e "bottom" para plotar um histograma
  histogram_width = (x_range_max-x_range_min)/bins_hist
  histogram_x = np.arange( x_range_min, x_range_max, histogram_width ).tolist()
  histogram_bottoms = dict(zip(histogram_x,len(histogram_x)*[0])) ##valores com o valor da base
  histogram_0 = copy.copy(histogram_bottoms) #variavel referencia - dicionario com valores zerados

  ## Plots individuais ##
  histogram_df = {}
  for (df, position) in [(df1, 0), (df2, 1)]:
    unique_variable = df[variable].unique()
    #variavel referencia - dicionario com valores zerados:
    values_0 = dict(zip(unique_variable,len(unique_variable)*[0]))

    count = 0
    for i in unique_by:
      values = copy.copy(values_0) #armazenará os "value_counts" referentes a vada valor unico de uma variavel
      aux_df = df.loc[df[by]==i, variable]
      hist_aux_df = aux_df.value_counts()
      for j in hist_aux_df.index:
        values[j] += hist_aux_df[j]

      ## Histograma ##
      histogram_values = copy.copy(histogram_0)
      for j in values.keys():
        for k in histogram_x[::-1]:
          if (j>=k):
            histogram_values[k] += values[j]
            break

      ## Grafico ##
      ax[position,0].bar(x=list(histogram_values.keys()), #https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.bar.html#matplotlib.axes.Axes.bar
                        height=list(histogram_values.values()),
                        width=histogram_width,
                        bottom=list(histogram_bottoms.values()),
                        align = 'edge',
                        color = colors[count],
                        #edgecolor='black',
                        #hatch='//',
                        alpha=alpha,
                        label= i
                        )
      if (position==0):
        if (df1_name=='default'):
          title='df1'
        else:
          title=df1_name
      if (position==1):
        if (df2_name=='default'):
          title='df2'
        else:
          title=df2_name
      ax[position,0].set_title(title)
      ax[position,0].set_ylabel('Frequência')
      if (position==0): ax[position,0].set_xticks([]) #ocultar o eixo x
      if (position==1): ax[position,0].set_xlabel(variable)
      ax[position,0].legend();
      #ax[position,0].margins(0.05)
      ## Grafico ##

      for j in histogram_bottoms.keys():
        histogram_bottoms[j] += histogram_values[j]

      count += 1

    histogram_df[position] = histogram_bottoms.copy() #Armazenar valor para depois plotar junto o df1 e df2
    histogram_bottoms = histogram_0.copy()

  ## Plots juntos ##
  ## Grafico ##
  ax = plt.subplot(122)
  for i in (0, 1):
    if (i==0):
      color = 'darkred'
      if (df1_name=='default'):
        label='df1'
      else:
        label=df1_name
    if (i==1):
      color = 'cornflowerblue'
      if (df2_name=='default'):
        label='df2'
      else:
        label=df2_name
    ax.bar(x=list(histogram_df[i].keys()), #https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.bar.html#matplotlib.axes.Axes.bar
                  height=list(histogram_df[i].values()),
                  width=histogram_width,
                  align = 'edge',
                  color = color,
                  #edgecolor='black',
                  #hatch='//',
                  alpha=alpha,
                  label= label
                  )
    ax.legend()
    ax.set(xlabel=variable, ylabel='Frequência')
   ## Grafico ##

  return fig, ax