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
        TR (float): TR (second)
        sample (int, optional): TR당 샘플 개수. Defaults to 1.
        
    Returns:
        array: BOLD signal
    """
    
    from nltools.external import glover_hrf
    hrf = glover_hrf(TR, sample)
    y_new = np.convolve(y, hrf, mode="full")[:len(y)]
    return(y_new)


def eventseg_HMM(data, N, add_edge=True, scoring="diff"):
    """ HMM event segmentation from Baldassano et al. (2017).

    Args:
        data ([unit, time] array): input data
        N: number of events
        add_edge: include edge(0,end) at boundaries
        scoring (str): scoring method, default is diff
            - diff: within - across
            - ratio: (within+1) / (across+1)
        
    Returns:
        [boundaries, score]
    """
    
    import brainiak.eventseg.event
    TRs = data.shape[1]
    hmm_sim = brainiak.eventseg.event.EventSegment(N)
    hmm_sim.fit(data.T)
    
    
    bounds = np.where(np.diff(np.argmax(hmm_sim.segments_[0], axis=1)))[0]
    bounds_all = [0] + list(bounds) + [TRs]
    
    # score (within ev VS across ev)
    corrmat = np.corrcoef(data.T)
    within_mask = np.zeros_like(corrmat)
    for i in range(len(bounds_all)-1):
        within_mask[bounds_all[i]:bounds_all[i+1],bounds_all[i]:bounds_all[i+1]] = 1
    within_mask = np.triu(within_mask, k=1)
    across_mask = np.zeros_like(corrmat)
    for i in range(len(bounds_all)-2):
        across_mask[bounds_all[i]:bounds_all[i+1],bounds_all[i+1]:bounds_all[i+2]] = 1
    across_mask = np.triu(across_mask, k=1)
    
    if scoring == "diff":
        score = np.mean(corrmat[within_mask==1])-np.mean(corrmat[across_mask==1])
    elif scoring == "ratio":
        score = (np.mean(corrmat[within_mask==1])+1)/(np.mean(corrmat[across_mask==1])+1)
    else:
        raise NameError('Unknown scoring method ("diff", "ratio")')
    
    if add_edge: return([bounds_all,score])
    else: return([bounds,score])