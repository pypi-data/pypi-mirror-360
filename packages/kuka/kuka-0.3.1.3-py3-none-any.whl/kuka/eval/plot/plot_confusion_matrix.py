import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix
import numpy as np

from .. import utils

@utils.__input_type_validation
def plot_confusion_matrix(
    y_true, 
    y_pred, 
    labels=None, 
    cmap='Blues', 
    figsize=(6, 5),
    
    _input_type_dict = {
        'y_true': (np.ndarray, list), 
        'y_pred': (np.ndarray, list), 
        'labels': (list, tuple, None), 
        'cmap': str, 
        'figsize': (tuple, list)
    }
    
    ) -> None:

    # get the CM
    cm = confusion_matrix(y_true, y_pred)

    # Graphic:
    plt.figure(figsize=figsize)
    sns.heatmap(cm, annot=True, fmt='d', cmap=cmap, linewidths=0.5,
                xticklabels=labels, yticklabels=labels)

    # Add title and labels
    plt.xlabel('Prediction')
    plt.ylabel('True')
    plt.title('Confusion Matrix')
    plt.show()