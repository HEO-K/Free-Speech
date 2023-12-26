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



def get_run_names(Project, ses=None):
    """ Run 이름 생성기
    
    Args:
        Project (str): 프로젝트 이름
        ses (str, optional): 세션 번호, Defaults to None.

    Returns:
        list: 모든 run 리스트
    """
       
    info = get_full_info(Project)
    if ses == None: run_info = info['info']
    else: run_info = info["ses-"+ses]  
    runnames = []
    for run in run_info:
        if 'runs' in run.keys():
            for i in range(1, run["runs"]+1):
                runnames.append(run["name"]+"_run-"+str(i))
        else: runnames.append(run["name"])
    if "T1" in runnames: runnames.remove("T1")
        
    return runnames


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
    else:
        try:
            return(info[target_run])
        except:
            msg = "Run "+target_run+" isn't exist. (Exist runs: "
            for name in info.keys():
                msg = msg+"'"+ name + "', "
            msg = msg[:-2] + ")"
            print(msg)
            


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
    