# %%
import numpy as np
import nibabel as nib
import glob
import os
from . import load_project_info



##############################################################################################
# 리눅스인지 확인 
def isWSL():
    if os.getcwd()[0] == "/": return True
    else: return False
    
# make epi path
def get_epipath(Project, sub, taskname, ses=None, smooth=True):
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
    
    
    if ses == None:
        if smooth: 
            epi_name = "sub-"+sub+"_task-"+taskname+"_sc_dt_hp_sm.nii.gz"
        else: 
            epi_name = "sub-"+sub+"_task-"+taskname+"_sc_dt_hp.nii.gz"
        filepath = os.path.join(base, "derivatives", "sub-"+sub, "func", epi_name)
    else:
        ses = str(ses)
        if smooth:
            epi_name = "sub-"+sub+"_ses-"+ses+"_task-"+taskname+"_sc_dt_hp_sm.nii.gz"
        else:
            epi_name = "sub-"+sub+"_ses-"+ses+"_task-"+taskname+"_sc_dt_hp.nii.gz"
        filepath = os.path.join(base, "derivatives", "sub-"+sub, "ses-"+ses, "func", epi_name)
    
    return(filepath)
    


#############################################################################################
# load epi
def loader(Project, sub, taskname, ses=None, confound_interp='linear', 
           zscoring=True, smooth=True, dtype="float16"):
    """ EPI를 불러오기

    Args:
        Project (str): Project 이름.
        sub (str): sub 번호.
        taskname (str): task 이름, run이 있을 경우 포함되어야.
        ses (str, optional): ses 번호. Defaults to None.
        confound_interp (str, optional): FD>0.5이상을 처리하는 방법. Defaults to 'linear'.
        zscoring (bool, optional): zscoring 여부. Defaults to True.
        dtype (str, optional): 데이터 형식
    Returns: 
        4d EPI array
    """
    import pandas as pd
    from scipy.stats import zscore

    filepath = get_epipath(Project, sub, taskname, ses, smooth)
    if confound_interp == False:
        npypath = filepath[:-7]+"_raw.npy"
    else:
        npypath = filepath[:-7]+"_"+confound_interp+".npy"
    
    try:   # npy존재
        epi = np.load(npypath)
        

    except:
        epi = np.array(nib.load(filepath).get_fdata()).astype(dtype)
        
        # shape info
        fov = list(epi.shape[:-1])
        tr = epi.shape[-1]
        epi = epi.reshape(-1,tr)
        # zscore
        if zscoring:
            epi = zscore(epi, axis=1)
        
        # interp
        if not confound_interp == False:
            confound = np.loadtxt(filepath.split('_sc')[0]+"_desc-FDoutlier.txt", int)
            for i in range(len(confound)):
                if confound[i] == 1: epi[:,i] = np.nan
            epi = pd.DataFrame(epi.T)
            # method
            if confound_interp == 'linear': 
                epi=epi.interpolate()
            epi = np.array(epi).T.reshape((-1,tr))

        np.save(npypath, epi.reshape(fov+[tr]))
        epi = epi.reshape(fov+[tr])


    # return
    return(epi)


# epi masking
def masking(epi, mask, mask_number=1):
    """ epi를 masking

    Args:
        epi (array): EPI array
        mask (array or int): mask array 또는 MNI_복셀mm의 값
        mask_number (int, optional): masking할 mask 값. Defaults to 1.
        
    Returns: 
        2d masked array
    """
    # flatten
    if type(mask) is int:
        mask_data = get_MNI(mask)
    else:
        mask_data = np.array(mask)
    epi = np.array(epi)
    epi_data = epi.reshape(list(mask_data.shape)+[epi.shape[-1]])

    # masking
    epi_mask = epi_data[mask_data==mask_number,:]
    return(epi_mask)


# get atlas information
def get_atlas(name:str, size='3.0', mni_coordinates=False):
    """ Atlas 정보와 그 파일 불러오기

    Args:
        name: atlas 이름
            \- "Brainnetome"
            \- "Schaefer2018_<N>Parcels_<7/17>Networks"
            \- "Yeo2011_<7/17>Networks"
        size (int, optional): 복셀 크기(mm). Defaults to 3mm.
        mni_coordinates (bool, optional): parcel의 MNI 좌표. Defaults to False.

    Returns: 
        [info, data]
            \- info: string array of [index,name,(x,y,z)]     
            \- data: nii data array
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
    
    nii_file = glob.glob(os.path.join(file_base, name+"_"+str(size)+"mm.nii*"))[0]
    data = np.array(nib.load(nii_file).get_fdata())

    
            

    return([info, data])


# MNI 불러오기
def get_MNI(voxel_size, option=None):
    """ MNI 데이터 불러오기

    Args:
        voxel_size (str): 복셀 크기.
        option (str, optional): 옵션. Defaults to None.
            \- "mask": brain mask
            \- "wm": white matter
            \- "gm": grey matter
            \- "csf": cerebrospinal fluid
            \- "seg": results of fsl FAST

    Returns: 
        MNI array
    """
    mni_filename = "MNI_"+str(voxel_size)+"mm"
    if option!=None: 
        mni_filename = mni_filename+"_"+str(option)
    base = os.path.dirname(__file__)
    mni_path = glob.glob(os.path.join(base, "_data_Atlas", "MNI", mni_filename+".nii.gz"))[0]
    mni = np.array(nib.load(mni_path).get_fdata())
    return mni



# atlas averaging
def parcel_averaging(parcel, epi, size='3.0'):
    """ 각 parcel별 평균 timeseries

    Args:
        parcel: atlas, 아래 세 종류의 input 가능
            \- atlas에 있는 이름 (ex, Schaefer2018_<N>Parcels_<7/17>Networks)
            \- result of get_atlas [info, data], info를 기준으로 평균.
            \- atlas array, 존재하는 모든 수의 평균값을 구한다.
        epi(array): (x,y,z,t) or (v,t) array
        size (number, optional): parcel을 이름으로 불러올 경우의 복셀 크기(mm). Defaults to 3mm.

    Returns: 
        (parcel,t) array
    """
    # load parcel
    if type(parcel) == str:
        [info, data] = get_atlas(parcel, size=size)
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
    # load epi
    epi = np.array(epi)
    epi = epi.reshape(list(data.shape)+[epi.shape[-1]])
    # averaging
    avg_parcel = []

    for num in numbers:
        avg_parcel.append(np.nanmean(epi[data==num,:], axis=0))
    return(np.array(avg_parcel))


def get_parcel_roi_mask(parcel, roi, size="3.0"):
    """
    Parcel에서 roi mask 불러오기

    Args:
        parcel: atlas, 아래 세 종류의 input 가능
            \- atlas에 있는 이름 (ex, Schaefer2018_<N>Parcels_<7/17>Networks)
            \- result of get_atlas [info, data], info를 기준으로 평균.
            \- atlas array
        roi: roi index의 list 또는 숫자.
        size (number, optional): parcel을 이름으로 불러올 경우의 복셀 크기(mm). Defaults to 3mm.

    Returns: 
        Mask of roi (boolean array)
        
    """
    # load parcel
    if type(parcel) == str:
        [info, data] = get_atlas(parcel, size)
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
        
        
def network_cluster(parcel, epi, size='3', averaging=False):
    """ Yeo network별로 epi를 나눈 딕셔너리

    Args:
        parcel: network name / [info, data]
            \- "Yeo2011_<7/17>Networks"
            \- "Schaefer2018_<N>Parcels_<7/17>Networks"
            \- [info, data]: results of get_atlas
        epi(array): (x,y,z,t) or (v,t) array
        size (number, optional): parcel을 이름으로 불러올 경우의 복셀 크기(mm). Defaults to 3mm.
        averaging (bool): 네트워크 평균 여부. Defaults to 1.
        

    Returns: 네트워크 딕셔너리
        \- dict("Network_Name") = (voxel,t)
        \- 평균 시, dict("Network_Name") = (1,t)
    """
    # load 
    if type(parcel) == str:
        info, data = get_atlas(parcel, size)
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
            \- "Yeo2011_<7/17>Networks"
            \- "Schaefer2018_<N>Parcels_<7/17>Networks"
            \- info: results of get_atlas, only info

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



def fill_parcel_value(parcel, value, roi="all", size='3.0'):
    """ Atlas에 특정 값 채우기, 외 영역은 NaN

    Args:
        parcel: network name / [info, data]
            \- "Yeo2011_<7/17>Networks"
            \- "Schaefer2018_<N>Parcels_<7/17>Networks"
            \- [info, data]: results of get_atlas
        value: 채울 값
        roi: 타깃 roi. Defaults to 'all' (모든 parcel).
            \- int
            \- index array (1부터 시작)
            \- bool array
        size: atlas voxel size. Defaults to '3.0'

    Returns:
        _type_: _description_
    """
    
    
    # load parcel
    if type(parcel) == str:
        [info, data] = get_atlas(parcel, size)
        numbers = np.array(info[:,0], int)
    else:
        if len(parcel) == 2:
            data = parcel[1]
            info = parcel[0]
            numbers = np.array(info[:,0], int)
        else:
            data = np.nan_to_num(parcel)
            numbers = list(set(list(data.reshape(-1)))-{0})   
             
    brain = np.zeros_like(data)
    brain[:] = np.nan
    
    if roi == 'all':
        if len(value) == len(numbers):
            for i in range(len(value)):
                brain[data==i+1] = value[i]                
        else:
            num_value = len(value)
            num_parcels = len(numbers)
            raise Exception(f"Number of values({num_value}) is not matched with number of parcels({num_parcels})")
    else:
        if type(roi) == int:
            try:
                brain[data==roi] = value
            except:
                raise Exception(f"Roi-'{roi}' is not in atlas")
        
        if (roi[0]==True) or (roi[0]==False):
            try:
                n = 0
                for i in range(len(roi)):
                    if roi[i]: 
                        brain[data==i+1] = value[n]
                        n = n+1
            except:
                num_value = len(value)
                num_parcels = np.sum(roi)
                raise Exception(f"Number of values({num_value}) is not matched with number of rois({num_parcels})")                
        else:
            if len(value) == len(roi):
                for i,n in enumerate(roi):
                    brain[data==n] = value[i]
            else:
                num_value = len(value)
                num_parcels = len(roi)
                raise Exception(f"Number of values({num_value}) is not matched with number of rois({num_parcels})")
    
    return brain    
    



def data_to_MNI_nifti(input, voxel_size='3.0'):
    """ MNI Nifti1Image 이미지화
    
        Args:
            input (array) : input data, mni와 같은 크기여야 함
            voxel_size (str, optional): 복셀 크기(mm). Defaults to '3.0'
            
        Returns: 
            Nifiti1Image
    """
    
    mni_filename = "MNI_"+voxel_size+"mm_mask"
    base = os.path.dirname(__file__)
    mni_path = glob.glob(os.path.join(base, "_data_Atlas", "MNI", mni_filename+"*"))[0]
    mni = nib.load(mni_path)
        
    input_nifti = nib.Nifti1Image(input, mni.affine, mni.header)   
    return input_nifti


def data_to_MNI_nltools(input, voxel_size='3.0'):
    """ MNI nltools.Brain_Data화

    Args:
        input (array): input data, mni와 같은 크기여야 함
        voxel_size (str, optional): 복셀 크기(mm). Defaults to '3.0'.

    Returns:
        nltools.Brain_data
    """
    
    from nltools.data import Brain_Data
    
    nifti = data_to_MNI_nifti(input, voxel_size)
    
    mni_filename = "MNI_"+voxel_size+"mm_mask"
    base = os.path.dirname(__file__)
    mni_path = glob.glob(os.path.join(base, "_data_Atlas", "MNI", mni_filename+"*"))[0]
    
    data = Brain_Data(data=nifti, mask=mni_path)
    
    return data

# %%
