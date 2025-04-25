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
            - diff: (within - across)/N
            - ratio: (within+1) / (across+1)
            - original: (t==t+5) - (t!=t+5), from Baldassano et al. (2017)
        
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
        score = score/N
    elif scoring == "ratio":
        score = (np.mean(corrmat[within_mask==1])+1)/(np.mean(corrmat[across_mask==1])+1)
    elif scoring == "original":
        events = np.argmax(hmm_sim.segments_[0], axis=1)
        corrs = np.diag(corrmat, 5)
        within = corrs[events[:-5] == events[5:]].mean()
        across = corrs[events[:-5] != events[5:]].mean()
        score = within-across
        
        
    else:
        raise NameError('Unknown scoring method ("diff", "ratio", "original")')
    
    if add_edge: return([bounds_all,score])
    else: return([bounds,score])
    
    
    
def glm(input, X, apply_hrf=True, tr=1000):
    """ General linear model 

    Args:
        input (array): Input [voxel, times]
        X (array): Design matrix [condition, times]
        apply_hrf (bool, optional): Apply hrf at X. Defaults to True.
        tr (int, optional): tr (ms). Defaults to 1000.

    Returns:
        Array: [condition, voxel]
    """
    
    input = np.array(input).astype("float32")
    try:
        _, times = input.shape
    except:
        times = len(input)
        input = input.reshape(1, times)
    
    X = np.array(X)
    try:
        n, times = X.shape
    except:
        times = len(X)
        X = X.reshape(1,times)
        n = 1
    
    if apply_hrf:
        X_hrf = []
        for i in range(n):
            X_hrf.append(hrf_convolution(X[i,:],tr/1000))
        X_hrf = np.array(X_hrf).astype("float32").T
    else:
        X_hrf = np.array(X).astype("float32").T
        
    
    betas = np.dot(np.dot(np.linalg.pinv(np.dot(X_hrf.T, X_hrf)), X_hrf.T), input.T)
    return betas
    
    
def p_from_dist(x, dist, alternative="two-sided"):
    """ Calculate p-value from distribution

    Args:
        x (float): value
        dist (array): distribution

    Returns:
        float: p-value
    """
    from scipy.stats import norm
    z = (x-np.mean(dist))/np.std(dist)
    if alternative == "two-sided":
        p = 2*(1-norm.cdf(abs(z)))
    elif alternative == "greater":
        p = 1-norm.cdf(z)
    elif alternative == "less":
        p = norm.cdf(z)
    return(p)