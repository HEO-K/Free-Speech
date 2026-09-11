import numpy as np
import os
import json
from .tools import isWSL


def get_full_info(Project):
    """ 저장되어 있는 프로젝트 정보 불러오기

    Args:
        Project (str): 프로젝트 이름

    Returns:
        dict: json형태의 정보
    """
    
    base = os.path.dirname(__file__)
    base = os.path.join(base, "_data_Project", Project)
    with open(os.path.join(base, 'project_info.json'), encoding="utf-8") as f:
        info = json.load(f)
    
    return info



def run_numbers(run):
    """ project_info 항목의 'runs' 를 run 번호 리스트로 정규화

    'runs' 가 없으면 [] (run 라벨 없이 name 만 쓴다),
    정수 n 이면 [1, ..., n] (구형 표기),
    리스트면 그 번호 그대로 (예: [2] → run-2 만 존재).

    Args:
        run (dict): project_info.json 의 run 항목

    Returns:
        list[int]: run 번호
    """

    runs = run.get("runs")
    if runs is None: return []
    if isinstance(runs, int): return list(range(1, runs+1))
    return [int(r) for r in runs]


def expand_run_names(run_info, only_func=True, sep="_run-"):
    """ 세션의 run 항목 리스트 → run 이름 리스트

    Args:
        run_info (list[dict]): project_info.json 의 세션 항목 (예: info["ses-01"])
        only_func (bool, optional): func 만 남길지. Defaults to True.
        sep (str, optional): name 과 번호 사이 구분자. Defaults to "_run-".

    Returns:
        list[str]: 'name_run-N' (runs 없으면 'name')
    """

    runnames = []
    for run in run_info:
        if only_func and run.get("type") != "func": continue
        nums = run_numbers(run)
        if nums: runnames += [f"{run['name']}{sep}{i}" for i in nums]
        else: runnames.append(run["name"])
    return runnames


def get_run_names(Project, ses=None, only_func=True):
    """ Run 이름 생성기

    Args:
        Project (str): 프로젝트 이름
        ses (str, optional): 세션 번호, Defaults to None.
        only_func (bool, optional): func 만 남길지. Defaults to True.

    Returns:
        list: 모든 run 리스트
    """

    info = get_full_info(Project)
    if ses == None: run_info = info['info']
    else: run_info = info["ses-"+ses]

    return expand_run_names(run_info, only_func=only_func)


def get_good_sub(Project, ses=None, target_run=None):
    """ 모션 괜찮은 피험자들 번호 목록
    
    Args:
        Project (str): 프로젝트 이름
        ses (str, optional): 세션 번호, Defaults to None.
        target_run (str, optional): 특정 run만 출력할지, 아니면 모든 run 각각. Defaults to None.
        
    Returns:
        target_run 있을 경우: 피험자 번호 list
        traget_run 없을 경우: dict, key: run, value: 피험자 번호 list
    """
    
    base = os.path.dirname(__file__)
    base = os.path.join(base, "_data_Project", Project)
    with open(os.path.join(base, 'good_sub.json'), encoding='utf-8') as f:
        info = json.load(f)
    
    if ses == None:
        info = info["info"]
    else:
        info = info["ses-"+ses]
    
    if target_run == None:
        return(info)
    if target_run not in info:
        # 예전엔 print 만 하고 None 을 돌려줘 호출자가 for sub in None 으로 죽거나
        # bare except 로 삼켜 빈 목록이 됐다. 없는 run 은 KeyError 로 알린다.
        exist = ", ".join(f"'{name}'" for name in info.keys())
        raise KeyError(f"Run '{target_run}' isn't in good_sub.json of {Project}"
                       f"{'' if ses is None else ' ses-'+str(ses)}. (Exist runs: {exist})")
    return(info[target_run])
            


def get_brain_path(Project, derivatives=True):
    """ nii 이미지 파일 저장 경로 불러오기

    Args:
        Project (str): 프로젝트 이름
        derivatives (bool, optional): derivative폴더인지. Defaults to True.

    Returns:
        path : Brain image data path
    """
    info = get_full_info(Project)
    if isWSL(): path = info["bids_path"]
    else: path = info["bids_path_window"]
    
    if derivatives: path = os.path.join(path, "derivatives")
    
    return path
        

def get_audio_path(Project, derivatives=True):
    """ Audio 파일 저장 경로 불러오기

    Args:
        Project (str): 프로젝트 이름
        derivatives (bool, optional): derivative폴더인지. Defaults to True.

    Returns:
        path : Audio data path
    """
    info = get_full_info(Project)
    if isWSL(): path = info["audio_path"]
    else: path = info["audio_path_window"]
    
    if derivatives: path = os.path.join(path, "derivatives")
    
    return path


def get_epi_info(Project, task, ses=None):
    """ EPI 정보 불러오기

    Args:
        Project (str): 프로젝트 이름
        task (str): 과제 이름
        ses (str, optional): session

    Returns:
        dict : information dictionary
    """

    if "_run-" in task:
        task = task.split("_run-")[0]
    info = get_full_info(Project)
    if ses: 
        ses = str(ses)
        info = info[f"ses-{ses}"]
    else:
        info = info["info"]
    
    find = 0
    for runs in info:
        if runs["name"] == task:
            find = 1
            return runs
    if find == 0:
        raise KeyError(f"Cannot find {task}")
    