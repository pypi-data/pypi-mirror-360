import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import (MultipleLocator, AutoMinorLocator)
import matplotlib
import sklearn

from .. import utils

def rmse(v_real,v_pred):
  return np.sqrt(sklearn.metrics.mean_squared_error(v_real,v_pred)) #leia sobre sklearn.metrics.mean_squared_error
def mape(v_real,v_pred):
  return sklearn.metrics.mean_absolute_percentage_error(v_real,v_pred) #https://scikit-learn.org/stable/modules/model_evaluation.html#mean-absolute-percentage-error


@utils.__input_type_validation
def plot_predictions(
    y_real = 'list',
    y_pred = 'list',
    figsize = [15., 6.],
    y_scale = 'default', #log ou linear
    put_major_label_tick_every = 'default',
    put_minor_label_tick_every = 'default',
    show_error_axis = True,
    error_axis = 'absolute or relative',
    font_size = 11.,
    report_big_relative_errors = True,
    big_errors_limit = 100,

    _input_type_dict = {
        'y_real': (list, tuple, np.ndarray),
        'y_pred': (list, tuple, np.ndarray),
        'figsize': (list, tuple),
        'y_scale': str,
        'put_major_label_tick_every': (str, int, float),
        'put_minor_label_tick_every': (str, int, float),
        'show_error_axis': bool,
        'error_axis': str,
        'font_size': (int, float),
        'report_big_relative_errors': bool,
        'big_errors_limit': (int, float),
    }

    ) -> object:

  if len(y_real)!=len(y_pred):
    print('ERRO: tamanho de y_real (',len(y_real),') é diferente do tamanho de y_pred (',len(y_pred),')')
    return

  matplotlib.rcParams['font.size'] = font_size

  if show_error_axis==True:
    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot(3, 1, (1, 2))
  else:
    fig, ax = plt.subplots(figsize=figsize)

  len_x = len(y_real)
  x = np.arange(1, len_x+1, 1)

  if put_major_label_tick_every=='default': put_major_label_tick_every = round( len_x/10, -1 )
  if put_minor_label_tick_every=='default': put_minor_label_tick_every = round( put_major_label_tick_every/2, 0 )

  ax.plot(x, y_pred,
          linewidth=2.8,
          label='Predito')

  ax.plot(x, y_real,
          linewidth=1.0,
          ls='--',
          marker='o',
          label='real',
          )


  ax.set(xlim=[0, len_x+1])
  ax.grid(True, which='both', axis='x', linestyle='-', color='lightgray')
  ax.xaxis.set_major_locator(MultipleLocator(put_major_label_tick_every))
  ax.xaxis.set_minor_locator(MultipleLocator(put_minor_label_tick_every))

  ax.set_ylabel('Permeabilidade (barrer)')

  plt.legend(loc='best')

  if y_scale=='default': y_scale='log'
  plt.yscale(y_scale)

  if show_error_axis==True:

    if (error_axis == 'absolute'):
      error_name = 'Erro absoluto'
      error_values = []
      print('Erro=pred-real')
      for real,pred in zip(y_real,y_pred):
        error_values += [pred-real]
    elif (error_axis == 'relative'):
      error_name = 'Erro relativo (%)'
      error_values = []
      print('Erro=(pred-real)/real')
      for real,pred in zip(y_real,y_pred):
        error_values += [(pred-real)/real*100]
    else:
      print('ERRO: Escolha uma funcao de erro disponivel (rmse, r2 ou mape)')

    if (report_big_relative_errors==True):
      print('Da amostra 1 a',len_x)
      for i in x:
        if (error_values[i-1]>big_errors_limit) or (error_values[i-1]<-big_errors_limit):
          print('Amostra',i,':',error_values[i-1])


    plt.tick_params('x', labelbottom=False)

    ax2 = fig.add_subplot(3, 1, 3, sharex=ax)
    ax2.set_xlabel('Amostra')
    ax2.set_ylabel(error_name)
    #print(error_values)
    #aux_delta = (max(error_values.min())-min(error_values))*0.05
    #ax[0].set_ylim([min(error_values)-aux_delta, max(error_values)-aux_delta])

    ax2.bar(x,error_values, color='tomato')
    ax2.plot(x,error_values, color='firebrick', label='Erro')

    if (error_axis == 'absolute'):
      ax2.plot(x, [rmse(y_real,y_pred)]*len_x,
                linewidth=1.0,
                ls='--',
                label='RMSE',
                color='firebrick'
                )
    elif (error_axis == 'relative'):
      ax2.plot(x, [mape(y_real,y_pred)]*len_x,
                linewidth=1.0,
                ls='--',
                label='MAPE',
                color='firebrick'
                )

    plt.legend(loc='best')

    return fig, (ax, ax2)
  else:
    ax.set_xlabel('Amostra')

    return fig, ax