import numpy as np


def resampling(x, y, x_new, method='linear'):
    """ 데이터의 새로운 x에 대응되는 y를 출력

    Args:
        x (1d array): 데이터의 x (onset).
        y (1d array): 데이터의 y (value).
        x_new (1d array): 추출할 값의 x.
        method (str, optional): 보간법. Defaults to 'linear'.
            - 'linear'
            - 'quadratic'
            - 'cubic'
            - 'nearest'    
            
    Returns:
        array: 리샘플링된 y
    """
    
    from scipy.interpolate import interp1d
    interp_model = interp1d(x, y, method, bounds_error=False, fill_value=0)
    y_new = interp_model(x_new)
    return y_new


def hrf_convolution(y, TR, sample=1):
    """ HRF 적용하기

    Args:
        y (1d array): input data
        TR (number): TR(s)
        sample (int, optional): TR당 샘플 개수. Defaults to 1.
        
    Returns:
        array: BOLD signal
    """
    
    from nltools.external import glover_hrf
    hrf = glover_hrf(TR, sample)
    y_new = np.convolve(y, hrf, mode="full")[:len(y)]
    return(y_new)
    