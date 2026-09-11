# %%
# custom functions for speech_3T project
import numpy as np
from Speech.load_project_info import get_good_sub
def good_subs(taskname, exception=[]):
    """ speech_3T의 피험자 불러오기

    Args:
        taskname (str): 과제명 (TA, M, G, 3, R)
            - TA: think aloud
            - TA2: ses-11 think-aloud
            - M: movie recall
            - G: game
            - 3: three topics
            - R: resting
            - MV: movie viewing
        exception (string list, optional): 예외 subject list. Defaults to [].
        
    Returns: [Project, sub, ses,task] list
    """
    
    if taskname == "TA":
        Project = "NatPAC_speech"
        task = "speechFREE_run-1"
        ses = "01"
    elif taskname == "TA2":
        Project = "NatPAC_speech"
        task = "speechFREE_run-1"
        ses = "11"
    elif taskname == "3": 
        Project = "NatPAC_speech"
        task = "speechTOPICS_run-1"
        ses = "10"
    elif taskname == "R":
        Project = "NatPAC_speech"
        task = "REST_run-1"
        ses = "02"
    elif taskname == "G":
        Project = "NatPAC_speech"
        task = "speechMC_run-1"
        ses = "08"    
    elif taskname == "MV":
        Project = "NatPAC_other"
        task = "movieGUEST_run-1"
        ses = "02"   
    elif taskname == "M":
        Project = "NatPAC_speech"
        task = "speechMOVIE_run-1"
        ses = "02"     
    subs_info = []
    ses_list = [ses+"RR", ses+"R", ses+"A", ses+"N", ses]
    for ses in ses_list:
        try:
            subs_list = get_good_sub(Project, ses=ses, target_run=task)
        except KeyError:        # 그 세션 라벨이나 run 이 good_sub.json 에 없으면 건너뛴다.
            continue            # JSON 파싱 오류·파일 없음은 그대로 올린다 (예전엔 bare except 로 빈 목록이 됐다)
        for sub in subs_list:
            subs_info.append([Project, sub, ses, task])
    
    # 예외 피험자
    final_subs = []
    for [Project, sub, ses, task] in subs_info:
        if sub not in exception: final_subs.append([Project, sub, ses, task])
    final_subs.sort()        
    return final_subs



def load_roi(name, output="mask", voxel="1.5"):
    roi_list={
        "HPC": ["Brainnetome", [215,216,217,218],],
        "PCN": ["Schaefer2018_400Parcels_17Networks", [144,145,146,147,148,351,352,353,354,355,356,357]],
        "IPS": ["Schaefer2018_400Parcels_17Networks", [122,123,124,125,126,325,326,327,328]],
        "rIPS": ["Schaefer2018_400Parcels_17Networks", [325,326,327,328,304]],  # 304
        "PMC-core": ["Schaefer2018_400Parcels_17Networks", list(np.arange(154,161))+list(np.arange(363,368))],
        "PCun": ["Schaefer2018_400Parcels_17Networks", list(np.arange(154,161))+list(np.arange(363,368))],
        "A1": ["Schaefer2018_400Parcels_17Networks", [44,45,244,245]],
        "RSC": ["Schaefer2018_400Parcels_17Networks", [144,145,351,352]],
        "PCC": ["Schaefer2018_400Parcels_17Networks", [147,148,356,357]],
        "AG": ["Schaefer2018_400Parcels_17Networks", [149,150,359,360]],
    }
    
    from Speech.tools_EPI import get_parcel_roi_mask
    roi_mask = get_parcel_roi_mask(roi_list[name][0], roi_list[name][1], voxel=voxel)
    
    if output=="mask": return(roi_mask)
    elif output=="all": return([roi_mask, roi_list[name]])
    elif output=="info": return(roi_list[name])
    else: raise Exception("output option is wrong. It would be ['mask','info','all']")