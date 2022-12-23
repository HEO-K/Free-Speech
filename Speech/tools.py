import os
import numpy as np
import glob


def isWSL():
    """ WSL환경인지 확인

    Returns: 
        bool
    """
    
    now = os.getcwd()
    if now[0] == "/": return(True)
    else: return(False)
    
 