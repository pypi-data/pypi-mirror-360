import numpy as np
import pandas as pd

def _ensure_that_input_is_valid_data_for_metrics(y_true, y_pred):
    '''
    input -> list, tupla, np.ndarray, pd.DataFrame
    '''
    
    if isinstance(y_true, pd.DataFrame):
        y_true = y_true.values.ravel()
    if isinstance(y_pred, pd.DataFrame):
        y_pred = y_pred.values.ravel()

    if isinstance(y_true, (list, tuple)):
        y_true = np.array(list(y_true))
    if isinstance(y_pred, (list, tuple)):
        y_pred = np.array(list(y_pred))

    if isinstance(y_true, np.ndarray) and isinstance(y_pred, np.ndarray):
        if (y_true.shape != y_pred.shape):
            y_true = y_true.ravel()
            y_pred = y_pred.ravel()
        
        msg = 'ERROR: The input data is not valid. `y_true` does not have the same shape as `y_pred`'
        if (y_true.shape != y_pred.shape): raise ValueError(msg)
        
    return y_true, y_pred


def c_coeff(y_true = 'class numpy.ndarray',
            y_pred = 'class numpy.ndarray'
            ): #https://www.sciencedirect.com/science/article/abs/pii/S0376738817311572?via%3Dihub
    '''
    Coeficiente proposto por Wessling et al (1997) (https://doi.org/10.1016/0376-7388(93)E0168-J)

    The neural network works predictively if C is smaller than 1. For C=l, the
    predicted permeability for an unknown polymer would be  equal to the average
    permeability of all polymers presented in the set (which is, in fact, useless).

    '''
    y_true, y_pred = _ensure_that_input_is_valid_data_for_metrics(y_true, y_pred)
    
    denominador = sum(abs(y_true.mean() - y_true))
    if denominador!=0:
        return sum(abs(y_pred-y_true))/denominador
    else:
        return np.nan

def r2(y_true, y_pred):
    y_true, y_pred = _ensure_that_input_is_valid_data_for_metrics(y_true, y_pred)
    return 1 - np.sum(np.square(np.subtract(y_true, y_pred)))/np.sum(np.square(np.subtract(y_true, np.mean(y_true) )))

def neg_r2(y_true, y_pred):
    return -r2(y_true, y_pred)

def rmse(y_true, y_pred):
    y_true, y_pred = _ensure_that_input_is_valid_data_for_metrics(y_true, y_pred)
    return np.sqrt( np.sum(np.square(np.subtract(y_true, y_pred)))/len(y_true) )

def mape(y_true, y_pred):
    y_true, y_pred = _ensure_that_input_is_valid_data_for_metrics(y_true, y_pred)
    return np.sum( np.absolute( np.divide( np.subtract(y_true, y_pred), y_true) ))/len(y_true)