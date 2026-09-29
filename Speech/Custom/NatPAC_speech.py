# %%
# custom functions for speech_3T project
import numpy as np
from Speech.load_project_info import get_good_sub
# 과제 키 → (Project, ses, task 이름, 기본 run 목록). Project 는 폴더가 아니라
# _data_Project/ 레지스트리 키다. 새 과제는 여기 한 줄만 추가한다.
TASK_KEYS = {
    "TA":  ("NatPAC_speech", "01", "speechFREE",   [1]),            # think-aloud
    "TA2": ("NatPAC_speech", "11", "speechFREE",   [1]),            # ses-11 think-aloud
    "3":   ("NatPAC_speech", "10", "speechTOPICS", [1]),            # three topics
    "R":   ("NatPAC_speech", "02", "REST",         [1]),            # resting
    "G":   ("NatPAC_speech", "08", "speechMC",     [1]),            # game (MC)
    "M":   ("NatPAC_speech", "02", "speechMOVIE",  [1]),            # movie recall
    "MV":  ("NatPAC_other",  "02", "movieGUEST",   [1]),            # movie viewing (run-2 는 runs=[2])
    "MK":  ("NatPAC_monkey", "11", "movieMONKEY",  [1, 2, 3, 4, 5]),  # Monkey Kingdom 시청, 5 run
}


def good_subs(taskname, exception=[], runs=None):
    """ NatPAC 과제별 분석 대상 피험자 불러오기

    Args:
        taskname (str): 과제 키. TASK_KEYS 참조
            - TA: think aloud (ses-01)
            - TA2: ses-11 think-aloud
            - 3: three topics
            - R: resting
            - G: game
            - M: movie recall
            - MV: movie viewing (movieGUEST)
            - MK: movie viewing (movieMONKEY, run 1~5)
        exception (string list, optional): 예외 subject list. Defaults to [].
        runs (int or int list, optional): 가져올 run 번호. None 이면 키의 기본 run
            (MK 는 5개 전부, 나머지는 run-1). 여러 run 이면 피험자마다 run 별로 한 항목씩.

    Returns: [Project, sub, ses, task] list — task 는 "movieMONKEY_run-3" 꼴
    """
    if taskname not in TASK_KEYS:
        raise KeyError(f"Unknown task key '{taskname}'. (Exist keys: {', '.join(TASK_KEYS)})")
    Project, ses, task, default_runs = TASK_KEYS[taskname]
    if runs is None: runs = default_runs
    elif isinstance(runs, int): runs = [runs]

    subs_info = []
    ses_list = [ses+"RR", ses+"R", ses+"A", ses+"N", ses]
    for ses in ses_list:
        for run in runs:
            task_run = f"{task}_run-{run}"
            try:
                subs_list = get_good_sub(Project, ses=ses, target_run=task_run)
            except KeyError:        # 그 세션 라벨이나 run 이 good_sub.json 에 없으면 건너뛴다.
                continue            # JSON 파싱 오류·파일 없음은 그대로 올린다 (예전엔 bare except 로 빈 목록이 됐다)
            for sub in subs_list:
                subs_info.append([Project, sub, ses, task_run])

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