import numpy as np
from scipy.stats import gamma


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


def monkey_hrf(tr, contrast_type='mion', duration=32.0, dt=None, normalize_to_peak=True):
    """
    Leite et al. (2002)
    """
    if dt is None:
        dt = tr
        
    # time axis
    t = np.arange(0, duration, dt)
    
    # parameters setting
    taus = np.array([1.5, 4.5, 13.5])
    if contrast_type.lower() == 'bold':
        amplitudes = np.array([-0.89, 3.09, -1.20])
    elif contrast_type.lower() == 'mion':
        amplitudes = np.array([-0.21, 0.41, 0.80])
    else:
        raise ValueError("contrast_type must be 'mion' or 'bold'")
    hrf = np.zeros_like(t, dtype=float)
    for a, tau in zip(amplitudes, taus):
        hrf += (a / tau) * np.exp(-t / tau)  
        
    # Baseline correction / Normalization
    hrf = hrf - hrf[-1]
    hrf[0] = 0.0
    if normalize_to_peak:
        peak_val = np.max(np.abs(hrf))
        if peak_val != 0:
            hrf /= peak_val
    
    return hrf



def _gamma_difference_hrf(
    tr,
    oversampling=16,
    time_length=32,
    onset=0.0,
    delay=6,
    undershoot=16.0,
    dispersion=1.0,
    u_dispersion=1.0,
    ratio=0.167,
):
    """Compute an hrf as the difference of two gamma functions
    Parameters
    ----------
    tr: float, scan repeat time, in seconds
    oversampling: int, temporal oversampling factor, optional
    time_length: int, hrf kernel length, in seconds
    onset: float, onset of the hrf
    Returns
    -------
    hrf: array of shape(length / tr * oversampling, float),
         hrf sampling on the oversampled time grid
    """
    dt = tr / oversampling
    time_stamps = np.linspace(0, time_length, int(time_length / dt))
    time_stamps -= onset / dt
    hrf = gamma.pdf(
        time_stamps, delay / dispersion, dt / dispersion
    ) - ratio * gamma.pdf(time_stamps, undershoot / u_dispersion, dt / u_dispersion)
    hrf /= hrf.sum()
    return hrf


def spm_hrf(tr, oversampling=16, time_length=32.0, onset=0.0):
    """Implementation of the SPM hrf model.

    Args:
        tr: float, scan repeat time, in seconds
        oversampling: int, temporal oversampling factor, optional
        time_length: float, hrf kernel length, in seconds
        onset: float, onset of the response

    Returns:
        hrf: array of shape(length / tr * oversampling, float),
            hrf sampling on the oversampled time grid

    """

    return _gamma_difference_hrf(tr, oversampling, time_length, onset)


def glover_hrf(tr, oversampling=16, time_length=32, onset=0.0):
    """Implementation of the Glover hrf model.

    Args:
        tr: float, scan repeat time, in seconds
        oversampling: int, temporal oversampling factor, optional
        time_length: int, hrf kernel length, in seconds
        onset: float, onset of the response

    Returns:
        hrf: array of shape(length / tr * oversampling, float),
            hrf sampling on the oversampled time grid

    """

    return _gamma_difference_hrf(
        tr,
        oversampling,
        time_length,
        onset,
        delay=6,
        undershoot=12.0,
        dispersion=0.9,
        u_dispersion=0.9,
        ratio=0.35,
    )


def spm_time_derivative(tr, oversampling=16, time_length=32.0, onset=0.0):
    """Implementation of the SPM time derivative hrf (dhrf) model.

    Args:
        tr: float, scan repeat time, in seconds
        oversampling: int, temporal oversampling factor, optional
        time_length: float, hrf kernel length, in seconds
        onset: float, onset of the response

    Returns:
        dhrf: array of shape(length / tr, float),
              dhrf sampling on the provided grid

    """

    do = 0.1
    dhrf = (
        1.0
        / do
        * (
            spm_hrf(tr, oversampling, time_length, onset + do)
            - spm_hrf(tr, oversampling, time_length, onset)
        )
    )
    return dhrf


def glover_time_derivative(tr, oversampling=16, time_length=32.0, onset=0.0):
    """Implementation of the flover time derivative hrf (dhrf) model.

    Args:
        tr: float, scan repeat time, in seconds
        oversampling: int, temporal oversampling factor, optional
        time_length: float, hrf kernel length, in seconds
        onset: float, onset of the response

    Returns:
        dhrf: array of shape(length / tr, float),
              dhrf sampling on the provided grid

    """

    do = 0.1
    dhrf = (
        1.0
        / do
        * (
            glover_hrf(tr, oversampling, time_length, onset + do)
            - glover_hrf(tr, oversampling, time_length, onset)
        )
    )
    return dhrf


def spm_dispersion_derivative(tr, oversampling=16, time_length=32.0, onset=0.0):
    """Implementation of the SPM dispersion derivative hrf model.

    Args:
        tr: float, scan repeat time, in seconds
        oversampling: int, temporal oversampling factor, optional
        time_length: float, hrf kernel length, in seconds
        onset: float, onset of the response

    Returns:
        dhrf: array of shape(length / tr * oversampling, float),
              dhrf sampling on the oversampled time grid

    """

    dd = 0.01
    dhrf = (
        1.0
        / dd
        * (
            _gamma_difference_hrf(
                tr, oversampling, time_length, onset, dispersion=1.0 + dd
            )
            - spm_hrf(tr, oversampling, time_length, onset)
        )
    )
    return dhrf

    
def hrf_convolution(y, TR, sample=1, method="glover"):
    """ HRF 적용하기

    Args:
        y (1d array): input data
        TR (float): TR (ms). 다른 로더·glm 과 같은 단위 — 7T speech 는 1600
        sample (int, optional): TR당 샘플 개수. Defaults to 1.
        method (str, optional): "glover"(사람 BOLD) / "mion" / "bold"(원숭이, Leite 2002)

    Returns:
        array: BOLD signal
    """
    TR_s = TR / 1000                                             # 커널 함수는 초 단위
    if method == "glover":
        hrf = glover_hrf(TR_s, sample)
    elif method in ("mion", "bold"):
        hrf = monkey_hrf(TR_s, contrast_type=method, dt=TR_s/sample)
    else:
        raise ValueError(f"unknown method: {method}")
    return np.convolve(y, hrf, mode="full")[:len(y)]


def glm(input, X, apply_hrf=True, tr=1000, intercept=True, **kwargs):
    """ General linear model

    Args:
        input (array): Input [voxel, times] (1d 면 voxel 1개로 본다)
        X (array): Design matrix [condition, times] (1d 면 condition 1개)
        apply_hrf (bool, optional): Apply hrf at X. Defaults to True.
        tr (int, optional): tr (ms). Defaults to 1000.
        intercept (bool, optional): 설계행렬에 상수항을 넣을지. Defaults to True.
            False 면 예전처럼 상수항 없이 푼다 — 입력과 HRF 회귀자가 모두 시간축 평균 0 일 때만
            True 와 같다 (입력만 z-score 해도 boxcar 회귀자 평균이 0 이 아니라 값이 달라진다).
        **kwargs: hrf_convolution 에 그대로 전달 (sample, method)

    Returns:
        Array: [condition, voxel] — 상수항 beta 는 돌려주지 않는다
    """

    input = np.atleast_2d(np.asarray(input, dtype="float64"))   # [voxel, times]
    X = np.atleast_2d(np.asarray(X, dtype="float64"))           # [condition, times]
    if input.shape[1] != X.shape[1]:
        raise ValueError(f"input times ({input.shape[1]}) != X times ({X.shape[1]})")
    n = X.shape[0]

    if apply_hrf:
        X_hrf = np.array([hrf_convolution(X[i,:], tr, **kwargs) for i in range(n)]).T
    else:
        X_hrf = X.T                                              # [times, condition]

    if intercept:
        X_hrf = np.column_stack([X_hrf, np.ones(X_hrf.shape[0])])

    # pinv(X) @ y — pinv(XᵀX)Xᵀ 보다 조건수가 낫다
    betas = np.linalg.pinv(X_hrf) @ input.T                      # [condition(+1), voxel]
    return betas[:n]

def empirical_p_value(actual_score, permuted_scores, alternative="two-sided"):
    """ Calculate empirical p-value from permutation test

    Args:
        actual_score (float): actual value
        permuted_scores (array format): null distribution
        alternative (str, optional): alternative hypothesis.. Defaults to "two-sided".

    Returns:
        float: p value
    """

    permuted_scores = np.array(permuted_scores)
    n_permutations = len(permuted_scores)
    if alternative == 'greater':
        C = np.sum(permuted_scores >= actual_score)
    elif alternative == 'less':
        C = np.sum(permuted_scores <= actual_score)
    elif alternative == 'two-sided':
        null_mean = np.mean(permuted_scores)
        actual_dist = np.abs(actual_score - null_mean)
        permuted_dists = np.abs(permuted_scores - null_mean)
        C = np.sum(permuted_dists >= actual_dist)
    else:
        raise ValueError("alternative should be 'two-sided', 'less', 'greater'")

    p_value = (C + 1) / (n_permutations + 1)
    return p_value
    
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


def normalized_cross_correlation(x, y, maxlags=None):
    """
    matplotlib.pyplot.xcorr, normed=True

    Parameters:
    - x (array_like)
    - y (array_like)
    - maxlags (int, defalt=None): number of delay. [-maxlags, maxlags]

    Returns:
    - lags (numpy.ndarray): 각 상관 계수에 해당하는 지연(lag) 값들.
    - c_norm (numpy.ndarray): 정규화된 교차 상관 계수 값들.
    """
    x = np.asarray(x)
    y = np.asarray(y)

    # 일반적으로 시계열 상관 분석에서는 평균을 제거하는 것이 좋습니다.
    # matplotlib.xcorr는 이 작업을 자동으로 수행하지 않습니다.
    # 만약 plt.xcorr와 '정확히' 같은 동작을 원한다면 이 두 줄을 주석 처리해야 합니다.
    x_demeaned = x - np.mean(x)
    y_demeaned = y - np.mean(y)

    # numpy.correlate는 'full' 모드로 모든 가능한 지연에 대해 계산하며, 정규화되지 않습니다.
    # 이 함수는 y를 x에 대해 "슬라이딩"하며 각 겹치는 부분의 내적을 계산합니다.
    c = np.correlate(x_demeaned, y_demeaned, mode='full')

    # lags (지연) 값 계산
    # np.correlate(a, v, mode='full')의 결과 길이는 len(a) + len(v) - 1 입니다.
    # 중앙 인덱스가 lag 0 에 해당합니다.
    lags = np.arange(1 - y.size, x.size)

    # 정규화 (matplotlib.xcorr의 normed=True와 유사하게)
    # 이는 각 시계열의 L2 노름(norm)을 사용하여 정규화합니다.
    # 시계열 x와 y의 제곱합 (평균이 제거된 상태)
    s_xx = np.sum(x_demeaned**2)
    s_yy = np.sum(y_demeaned**2)

    # 정규화 인자
    norm_factor = np.sqrt(s_xx * s_yy)

    if norm_factor == 0:
        # 분모가 0인 경우 (예: 모든 값이 동일한 시계열, 즉 분산이 0인 경우)
        c_norm = np.zeros_like(c, dtype=float)
    else:
        c_norm = c / norm_factor

    # maxlags가 지정된 경우 해당 범위로 결과 자르기
    if maxlags is not None:
        if not (0 <= maxlags < min(x.size, y.size)):
            # maxlags는 입력 시계열 길이보다 작아야 합니다.
            # 또한, matplotlib의 xcorr는 maxlags를 양수로 받습니다.
            raise ValueError(f"maxlags ({maxlags}) must be a non-negative integer less than min(len(x), len(y)).")
        
        # lags에서 -maxlags부터 maxlags 범위에 해당하는 인덱스를 찾습니다.
        valid_indices = np.where((lags >= -maxlags) & (lags <= maxlags))[0]
        
        lags = lags[valid_indices]
        c_norm = c_norm[valid_indices]

    return lags, c_norm


def partial_correlation(X, a, b):
    """
    r(X, a | b)의 계산,

    Args:
        x (np.ndarray): 전체 데이터 배열 (n_samples, n_features).
        a_indices (list): 편상관을 계산할 변수들의 인덱스 리스트.
        b_indices (list): 통제할(covariate) 변수들의 인덱스 리스트.

    Returns:
        Partial correlation.
    """
    from sklearn.linear_model import LinearRegression
    X = np.array(X)
    a = np.array(a).reshape(-1,1)
    n_samples = X.shape[0]
    b = np.array(b).reshape(-1,1)
    model_x = LinearRegression()
    model_x.fit(b, X)
    res_X = X - model_x.predict(b)
    model_a = LinearRegression()
    model_a.fit(b, a)
    res_A = a - model_a.predict(b)
    res_X_std = (res_X - res_X.mean(axis=0)) / (res_X.std(axis=0, ddof=1) + 1e-10)
    res_A_std = (res_A - res_A.mean(axis=0)) / (res_A.std(axis=0, ddof=1) + 1e-10)
    pcorr_matrix = (res_X_std.T @ res_A_std) / (n_samples - 1)
    return np.clip(pcorr_matrix, -1.0, 1.0)
