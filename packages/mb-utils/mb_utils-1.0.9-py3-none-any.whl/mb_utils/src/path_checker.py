##Function to check paths

import os
import pandas as pd

__all__ = ['check_path']

def check_path(path,logger=None) -> bool:
    """
    Function to check the path
    Input:
        path: path to be checked (list or pandas.DataFrame)
    Output:
        list: True if path exists else False
    """
    if type(path) != list or type(path) != pd.DataFrame or type(path) != pd.core.series.Series:
        path = [path]
    if type(path) == pd.core.series.Series:
        path = path.values.tolist()
    
    res = [True if os.path.exists(p) else False for p in path]
    if logger:
        logger.info('Path not found: {}'.format(path.count(False)))
    return res