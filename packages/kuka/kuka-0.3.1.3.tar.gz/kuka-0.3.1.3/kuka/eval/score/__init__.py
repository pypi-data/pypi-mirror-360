'''FUNCTIONS THAT RETURN THE PERFORMANCE OF MODELS BY A TABLE/LIST...'''
# to deploy:
from .metrics import r2
from .metrics import neg_r2
from .metrics import rmse
from .metrics import mape
from .metrics import c_coeff

# from .display_score import display_score
# from .predictions_separate_by_a_variable import predictions_separate_by_a_variable

# from .classification_metrics import classification_metrics

__all__ = [
    #metrics:
    'r2','neg_r2',
    'rmse',
    'mape',
    'c_coeff',
    # #regression:
    # 'display_score',
    # 'predictions_separate_by_a_variable',
    # #categorization:
    # 'classification_metrics',
]