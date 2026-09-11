# %%
import numpy as np
import nibabel as nib
import glob
import os
from . import load_project_info
from .tools import isWSL   # 정의는 tools.py 한 곳에만 둔다 (예전엔 여기에 중복 정의돼 있었다)


# make epi path
def get_epipath(Project, sub, taskname, ses=None, smooth=True, epi_space="MNI152NLin2009cAsym"):
    """ EPI path 불러오기

    Args:
        Project (str): Project 이름.
        sub (str): sub 번호.
        taskname (str): task 이름, run이 있을 경우 포함되어야.
        ses (str, optional): ses 번호. Defaults to None.
        smooth (bool, optional): Smoothing 유무. Defaults to True.
    Returns: 
        Path string
    """
    info = load_project_info.get_full_info(Project)
    if isWSL()==True: 
        base = info["bids_path"]
    else: 
        base = info["bids_path_window"]
    
    if smooth: preprocess = "_desc-DN_sc_dt_hp_sm.nii.gz"
    else: preprocess = "_desc-DN_sc_dt_hp.nii.gz"
    if ses == None: 
        seslabel = ""
        epi_path = os.path.join(base, "derivatives", f"sub-{sub}", "func")
    else: 
        seslabel = f"_ses-{ses}"
        epi_path = os.path.join(base, "derivatives", f"sub-{sub}", f"ses-{ses}", "func")
    
    epi_name = f"sub-{sub}{seslabel}_task-{taskname}_space-{epi_space}{preprocess}"
    filepath = os.path.join(epi_path, epi_name)
   
    return(filepath)
    


#############################################################################################
# load epi
def loader(Project, sub, taskname, ses=None, confound_interp='linear', save=False,
           zscoring=True, smooth=True, epi_space="MNI152NLin2009cAsym", dtype="float16"):
    """ EPI를 불러오기

    Args:
        Project (str): Project 이름.
        sub (str): sub 번호.
        taskname (str): task 이름, run이 있을 경우 포함되어야.
        ses (str, optional): ses 번호. Defaults to None.
        confound_interp (str or False, optional): FD>0.5이상을 처리하는 방법. Defaults to 'linear'.
        zscoring (bool, optional): zscoring 여부. Defaults to True.
        smooth (bool, optional): smoothing 여부. Defaults to True.
        epi_space (str, optional): epi 공간. Defaults to "MNI152NLin2009cAsym".
        dtype (str, optional): 데이터 형식
    Returns: 
        4d EPI array
    """
    import pandas as pd
    from scipy.stats import zscore

    if confound_interp not in (False, "linear"):
        raise ValueError(f"confound_interp must be False or 'linear' (got {confound_interp!r})")

    filepath = get_epipath(Project, sub, taskname, ses, smooth, epi_space)
    # 캐시 파일명은 결과에 영향을 주는 옵션을 전부 담는다.
    # 기본 옵션(zscoring=True, float16)은 예전 이름(_raw / _linear)을 그대로 써서 기존 캐시가 유효하다.
    tag = "raw" if confound_interp == False else confound_interp
    if not zscoring:
        tag += "_nozscore"
    if np.dtype(dtype) != np.float16:
        tag += "_" + np.dtype(dtype).name
    npypath = filepath[:-7] + f"_{tag}.npy"

    if not save and os.path.exists(npypath):
        try:
            return np.load(npypath)
        except (OSError, ValueError) as e:      # 손상된 npy 만 다시 만든다 (MemoryError 등은 그대로 올린다)
            print(f"[loader] cache unreadable, rebuilding: {npypath} ({e})")

    epi = np.array(nib.load(filepath).get_fdata())
    fov = list(epi.shape[:-1])
    tr = epi.shape[-1]
    epi = epi.reshape(-1, tr)
    if zscoring:
        epi = zscore(epi, axis=1)
    if confound_interp == "linear":
        confound = np.loadtxt(filepath.split('_space')[0] + "_desc-FDoutlier.txt", int)
        epi[:, confound == 1] = np.nan
        epi = pd.DataFrame(epi.T).interpolate().to_numpy().T
    epi = epi.astype(dtype).reshape(fov + [tr])

    tmp_path = npypath[:-4] + ".tmp.npy"       # 쓰다 죽어도 반쯤 쓰인 캐시가 남지 않게
    np.save(tmp_path, epi)
    os.replace(tmp_path, npypath)


    # return
    return(epi)


def voxel_str(voxel):
    """ 복셀 크기를 atlas 파일명 규약('3.0', '1.5')의 문자열로 정규화.
    정본은 '3.0' 같은 텍스트지만 3, 3.0, '3' 도 같은 파일을 가리키게 한다 (예전엔 '3' 이 `_3mm` 을 찾아 죽었다). """
    return f"{float(voxel):.1f}"


# epi masking
def masking(epi, mask, mask_number=1):
    """ epi를 masking

    Args:
        epi (array): EPI array
        mask (array or str): mask array, 또는 복셀 크기('3.0') — 그 크기의 MNI brain mask 를 쓴다
        mask_number (int, optional): masking할 mask 값. Defaults to 1.

    Returns:
        2d masked array
    """
    # flatten
    if isinstance(mask, (str, int, float)):
        mask_data = get_MNI(mask, option="mask")
    else:
        mask_data = np.array(mask)
    epi = np.array(epi)
    epi_data = epi.reshape(list(mask_data.shape)+[epi.shape[-1]])

    # masking
    epi_mask = epi_data[mask_data==mask_number,:]
    return(epi_mask)


# get atlas information
def get_atlas(name:str, voxel='3.0', mni_coordinates=False, get_info=True):
    """ Atlas 정보와 그 파일 불러오기

    Args:
        name: atlas 이름
            - "Brainnetome"
            - "Schaefer2018_<N>Parcels_<7/17>Networks"
            - "Yeo2011_<7/17>Networks"
        voxel (str, optional): 복셀 크기(mm) 텍스트, '3.0' / '1.5'. Defaults to '3.0'.
        mni_coordinates (bool, optional): parcel의 MNI 좌표. Defaults to False.

    Returns: 
        [info, data]
            - info: string array of [index,name,(x,y,z)]     
            - data: nii data array
    """
    # get information
    base_path = os.path.dirname(__file__)
    
    file_base = os.path.join(base_path, "_data_Atlas", name)
    info_file = glob.glob(os.path.join(file_base, name+".txt"))[0]
    info = []
    
    if mni_coordinates:
        import pandas as pd
        coor_file = glob.glob(os.path.join(file_base, name+"_coordinates.csv"))[0]
        coor_data = np.array(pd.read_csv(coor_file))
        coor_label = coor_data[:,0]
        
    nii_file = glob.glob(os.path.join(file_base, name+"_"+voxel_str(voxel)+"mm.nii*"))[0]
    data = np.array(nib.load(nii_file).get_fdata())
    
    if get_info:
        with open(info_file, 'r', encoding="utf-8") as f:
            lines = f.readlines()
            for line in lines:
                line = line.strip()
                if line[0] == "0": pass
                else:
                    if mni_coordinates:
                        coordinate = list(coor_data[coor_label==int(line.split()[0]),1:][0])
                        info.append([int(line.split()[0]), line.split()[1]]+coordinate)
                    else:
                        info.append([int(line.split()[0]), line.split()[1]])
        info = np.array(info)
        return([info, data])
    else:
        return(data)


# MNI 불러오기
def get_MNI(voxel, option=None, name="MNI"):
    """ MNI 데이터 불러오기

    Args:
        voxel (str): 복셀 크기(mm) 텍스트, '3.0' / '1.5'.
        option (str, optional): 옵션. Defaults to None.
            - "mask": brain mask
            - "wm": white matter
            - "gm": grey matter
            - "csf": cerebrospinal fluid
            - "seg": results of fsl FAST

    Returns: 
        MNI array
    """
    mni_filename = name+"_"+voxel_str(voxel)+"mm"
    if option!=None:
        mni_filename = mni_filename+"_"+str(option)
    base = os.path.dirname(__file__)
    mni_path = glob.glob(os.path.join(base, "_data_Atlas", name, mni_filename+".nii.gz"))[0]
    mni = np.array(nib.load(mni_path).get_fdata())
    return mni



# atlas averaging
def parcel_averaging(parcel, epi, voxel='3.0'):
    """ 각 parcel별 평균 timeseries

    Args:
        parcel: atlas, 아래 세 종류의 input 가능
            - atlas에 있는 이름 (ex, Schaefer2018_<N>Parcels_<7/17>Networks)
            - result of get_atlas [info, data], info를 기준으로 평균.
            - atlas array, 존재하는 모든 수의 평균값을 구한다.
        epi(array): (x,y,z,t) or (v,t) array
        voxel (str, optional): parcel을 이름으로 불러올 경우의 복셀 크기(mm) 텍스트. Defaults to '3.0'.

    Returns:
        (parcel,t) array
    """
    # load parcel
    if type(parcel) == str:
        [info, data] = get_atlas(parcel, voxel=voxel)
        numbers = np.array(info[:,0], int)
    else:
        if type(parcel) == list:
            data = parcel[1]
            info = parcel[0]
            numbers = np.array(info[:,0], int)
        else:
            data = np.nan_to_num(parcel)
            numbers = list(set(list(data.reshape(-1)))-{0})
    data = np.array(data, int)
    # load epi — float16 (loader 기본) 은 누적 오차가 커서 평균 전에 float32 로 올린다
    epi = np.asarray(epi)
    if epi.dtype == np.float16:
        epi = epi.astype(np.float32)
    epi = epi.reshape(list(data.shape)+[epi.shape[-1]])
    # averaging
    avg_parcel = []

    for num in numbers:
        avg_parcel.append(np.nanmean(epi[data==num,:], axis=0))
    return(np.array(avg_parcel))


def get_parcel_roi_mask(parcel, roi, voxel="3.0"):
    """
    Parcel에서 roi mask 불러오기

    Args:
        parcel: atlas, 아래 세 종류의 input 가능
            - atlas에 있는 이름 (ex, Schaefer2018_<N>Parcels_<7/17>Networks)
            - result of get_atlas [info, data], info를 기준으로 평균.
            - atlas array
        roi: roi index의 list 또는 숫자.
        voxel (str, optional): parcel을 이름으로 불러올 경우의 복셀 크기(mm) 텍스트. Defaults to '3.0'.

    Returns:
        Mask of roi (boolean array)

    """
    # load parcel
    if type(parcel) == str:
        [info, data] = get_atlas(parcel, voxel)
        numbers = np.array(info[:,0], int)
    else:
        if len(parcel) == 2:
            data = parcel[1]
            info = parcel[0]
            numbers = np.array(info[:,0], int)
        else:
            data = np.nan_to_num(parcel)
            numbers = list(set(list(data.reshape(-1)))-{0})
    # get roi
    mask = np.zeros_like(data)
    try:
        for i in roi: mask = np.logical_or(mask, data==i)
    except: mask = data==roi
    if np.sum(mask) == 0:
        import warnings
        warnings.warn("ROI is empty. Is roi index is correct?", UserWarning)
    
    return mask.astype(bool)      
        
        
def network_cluster(parcel, epi, voxel='3.0', averaging=False):
    """ Yeo network별로 epi를 나눈 딕셔너리

    Args:
        parcel: network name / [info, data]
            - "Schaefer2018_<N>Parcels_<7/17>Networks" (라벨이 `<7/17>Networks_LH_<Net>_...` 꼴이어야 한다)
            - [info, data]: results of get_atlas
        epi(array): (x,y,z,t) or (v,t) array
        voxel (str, optional): parcel을 이름으로 불러올 경우의 복셀 크기(mm) 텍스트. Defaults to '3.0'.
        averaging (bool): 네트워크 평균 여부. Defaults to 1.


    Returns: 네트워크 딕셔너리
        - dict("Network_Name") = (voxel,t)
        - 평균 시, dict("Network_Name") = (1,t)
    """
    # load
    if type(parcel) == str:
        info, data = get_atlas(parcel, voxel)
    else:
        info, data = parcel
    numbers = np.array(info[:,0], int)
    names = info[:,1]
    epi = np.array(epi)
    epi = epi.reshape(list(data.shape)+[epi.shape[-1]])
    # cluster 
    results = dict()
    start = 0

    for num in numbers:
        # get network name
        name = names[num-1].strip()
        name = name.split("_")[2]
        # get epi
        parcel_epi = epi[data==num,:]
        if name in results.keys():
            results[name] = np.vstack((results[name], parcel_epi))
        else:
            results[name] = parcel_epi
    # averaging
    if averaging:
        for name in results.keys():
            results[name] = np.nanmean(results[name], axis=0)
    return(results)


def get_network_info(parcel):
    """ parcel이 어느 Yeo network인지 출력
    
    Args:
        parcel (str) : network name / info
            - "Yeo2011_<7/17>Networks"
            - "Schaefer2018_<N>Parcels_<7/17>Networks"
            - info: results of get_atlas, only info

    Returns:
        array (number, name) : 인덱스 & 속하는 네트워크
    """
    if type(parcel) == str:
        info, data = get_atlas(parcel)
    else:
        info = parcel
    numbers = np.array(info[:,0], int)
    names = info[:,1]
    results = []
    if numbers[0] == 0:
        numbers = numbers[1:]
    for num in numbers:
        # get network name
        name = names[num-1].strip()
        name = name.split("_")[2]
        results.append([num, name])
    results = np.array(results)
    return(results)



def fill_parcel_value(parcel, value, roi="all", voxel='3.0'):
    """ Atlas에 특정 값 채우기, 외 영역은 NaN

    Args:
        parcel: network name / [info, data]
            - "Yeo2011_<7/17>Networks"
            - "Schaefer2018_<N>Parcels_<7/17>Networks"
            - [info, data]: results of get_atlas
        value: 채울 값
        roi: 타깃 roi. Defaults to 'all' (모든 parcel).
            - int
            - index array (1부터 시작)
            - bool array
        voxel (str, optional): parcel을 이름으로 불러올 경우의 복셀 크기(mm) 텍스트. Defaults to '3.0'.

    Returns:
        array: atlas 와 같은 shape, 채운 parcel 외는 NaN
    """


    # load parcel
    if type(parcel) == str:
        [info, data] = get_atlas(parcel, voxel)
        numbers = np.array(info[:,0], int)
    else:
        if len(parcel) == 2:
            data = parcel[1]
            info = parcel[0]
            numbers = np.array(info[:,0], int)
        else:
            data = np.nan_to_num(parcel)
            numbers = np.setdiff1d(np.unique(data), [0]).astype(int)
    data = np.asarray(data)
    brain = np.full(data.shape, np.nan)

    # roi 해석 → (채울 parcel 번호, 값) 짝
    #   'all'      : numbers 순서대로 (parcel 번호가 1..N 이 아니어도 된다)
    #   int        : 그 parcel 하나, value 는 스칼라
    #   bool array : get_atlas 순서(numbers)에 대한 마스크, 길이 = parcel 수, 값은 True 개수만큼
    #                (Schaefer 처럼 번호가 1..N 이면 예전처럼 i 번째 True → parcel i+1)
    #   index array: 그 번호들 (1부터). [1, 5, 6] 처럼 1 로 시작해도 bool 로 오인하지 않는다
    numbers = np.asarray(numbers, int)
    if isinstance(roi, str):
        if roi != 'all':
            raise ValueError(f"Unknown roi '{roi}' (use 'all', int, bool array, or index array)")
        targets = numbers
        what = "parcels"
    else:
        roi = np.asarray(roi)
        if roi.ndim == 0:
            targets = np.array([int(roi)])
        elif roi.dtype == bool:
            if len(roi) != len(numbers):
                raise ValueError(f"bool roi length({len(roi)}) != number of parcels({len(numbers)})")
            targets = numbers[roi]
        else:
            targets = roi.astype(int)
        what = "rois"
    values = np.atleast_1d(np.asarray(value, dtype=float))
    if len(values) != len(targets):
        raise ValueError(f"Number of values({len(values)}) is not matched with number of {what}({len(targets)})")

    for t, v in zip(targets, values):
        mask = data == t
        if not mask.any():
            raise ValueError(f"Roi-'{t}' is not in atlas")
        brain[mask] = v

    return brain
    



def data_to_MNI_nifti(input, voxel='3.0'):
    """ MNI Nifti1Image 이미지화

        Args:
            input (array) : input data, mni와 같은 크기여야 함
            voxel (str, optional): 복셀 크기(mm) 텍스트. Defaults to '3.0'

        Returns:
            Nifiti1Image
    """

    mni_filename = "MNI_"+voxel_str(voxel)+"mm_mask"
    base = os.path.dirname(__file__)
    mni_path = glob.glob(os.path.join(base, "_data_Atlas", "MNI", mni_filename+"*"))[0]
    mni = nib.load(mni_path)
        
    input_nifti = nib.Nifti1Image(input, mni.affine, mni.header)   
    return input_nifti


def data_to_MNI_nilearn(input, voxel='3.0'):
    """ Nilearn 이미지화

        Args:
            input (array) : input data, mni와 같은 크기여야 함
            voxel (str, optional): 복셀 크기(mm) 텍스트. Defaults to '3.0'

        Returns:
            Nifiti1Image
    """
    from nilearn.image import new_img_like
    nifti_img = data_to_MNI_nifti(input, voxel)
    epi_nilearn = new_img_like(nifti_img, nifti_img.get_fdata())
    return epi_nilearn
# %%
