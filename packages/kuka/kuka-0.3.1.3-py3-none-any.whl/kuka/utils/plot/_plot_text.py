import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure
from matplotlib.axes import Axes

from .._input_function_validation import _input_function_validation

_input_val_dict = {
    'text' : ( str, None),
    '_fontsize' : ( (float,int), 'range', [0, np.inf])
}

@_input_function_validation(_input_val_dict)
def _plot_text(text:str, _fontsize:float=12) -> tuple[Figure, Axes]:
    '''
    Plot a text in matplotlib. Useful to show some simple LaTeX codes.
    '''
    fig, ax = plt.subplots( figsize=(0.1, 0.1))
    ax.text(0, 0, f'{text}', fontsize=_fontsize)
    # ax.remove()
    # Remove axis
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
    # Remove boders
    ax.spines[:].set_visible(False)
    return fig, ax