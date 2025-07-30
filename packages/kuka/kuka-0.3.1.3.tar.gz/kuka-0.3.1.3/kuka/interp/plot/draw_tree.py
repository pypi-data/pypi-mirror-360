import pandas as pd
import re
import graphviz
import sklearn.tree
import IPython.display

from .. import utils

@utils.__input_type_validation
def draw_tree(
    t,
    dados,
    size=10,
    ratio=1,
    precision=0,
    
    _input_type_dict = {
        't': object,
        'dados': pd.DataFrame,
        'size': int,
        # 'ratio': ,
        # 'precision': ,
    },

    ) -> None:

    s=sklearn.tree.export_graphviz(t, out_file=None, feature_names=dados.columns, filled=True,
                                   special_characters=True, rotate=True, precision=precision)
    IPython.display.display(graphviz.Source(re.sub('Tree {', 
                                                   f'Tree {{ size={size}; ratio={ratio}', s)))