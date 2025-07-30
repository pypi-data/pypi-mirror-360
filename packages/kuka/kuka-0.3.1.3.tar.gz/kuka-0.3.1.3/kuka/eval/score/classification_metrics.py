from sklearn.metrics import precision_score, recall_score, f1_score
import numpy as np
import pandas as pd
from .. import utils


@utils.__input_type_validation
def classification_metrics(
    y_real,
    y_pred,
    
    _input_type_dict = {
        'y_real': np.ndarray,
        'y_pred': np.ndarray,
    }
    
    ) -> pd.DataFrame:
    #Macro - simple media
    precision_macro = precision_score(y_real, y_pred, average="macro")
    recall_macro = recall_score(y_real, y_pred, average="macro")
    f1_macro = f1_score(y_real, y_pred, average="macro")

    #weighted media
    precision_weighted = precision_score(y_real, y_pred, average="weighted")
    recall_weighted = recall_score(y_real, y_pred, average="weighted")
    f1_weighted = f1_score(y_real, y_pred, average="weighted")

    aux = pd.DataFrame( data = [[precision_macro, recall_macro, f1_macro],
                                [precision_weighted, recall_weighted, f1_weighted]
                                ],
                        columns = ['precision', 'recall', 'f1'],
                        index = ['macro', 'weighted'])
    return aux