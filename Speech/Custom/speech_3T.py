# %%
# custom functions for speech_3T project
import numpy as np
from Speech.load_project_info import get_good_sub


# 피험자 목록 불러오기
def good_subs(taskname, exception=[]):
    """ speech_3T의 피험자 불러오기

    Args:
        taskname (str): 과제명 (TA, 3, Z, S, LTA, L3, L, R)
            \- TA: think aloud
            \- 3: three topics
            \- Z: zig-zag
            \- S: all speech tasks (only speech_3T_v2)
            \- LTA: listening think aloud
            \- L3: listening three topics
            \- L: all listening tasks
            \- R: resting
        exception (string list, optional): 예외 subject list. Defaults to [].
        
    Returns: [Project, sub, task] list
    
    """
    if taskname == "TA":
        Projects = ["speech_3T","speech_3T_v2"]
        tasks = ["speechFREE", "speechFREE"]
    elif taskname == "3":
        Projects = ["speech_3T","speech_3T_v2"]
        tasks = ["speechTOPIC_run-1", "speechTOPIC"]    
    elif taskname == "Z":
        Projects = ["speech_3T_v2"]
        tasks = ["speechSTROLL"]    
    elif taskname == "S":
        Projects = ["speech_3T_v2","speech_3T_v2","speech_3T_v2"]
        tasks = ["speechFREE", "speechTOPIC", "speechSTROLL"]       
    elif taskname == "L3":
        Projects = ["speech_3T","speech_3T_v2"]
        tasks = ["listeningTOPIC", "listeningTOPIC"]       
    elif taskname == "LTA":
        Projects = ["speech_3T","speech_3T_v2"]
        tasks = ["listeningFREE", "listeningFREE"]      
    elif taskname == "L":
        Projects = ["speech_3T_v2","speech_3T_v2"]
        tasks = ["listeningFREE", "listeningTOPIC"]
    elif taskname == "R":
        Projects = ["speech_3T","speech_3T_v2"]
        tasks = ["REST", "REST"]  

    if taskname == "S":
        subs_info = []
        subs = []
        for Project, task in zip(Projects, tasks):
            if len(subs)<1:
                subs = get_good_sub(Project, target_run=task)
            else:
                subs = list(set(subs).intersection(set(get_good_sub(Project, target_run=task))))
        subs.sort()
        for sub in subs:
            for Project, task in zip(Projects, tasks):
                subs_info.append([Project, sub, task])
    elif taskname == "L":
        subs_info = []
        subs = []
        for Project, task in zip(Projects, tasks):
            if len(subs)<1:
                subs = get_good_sub(Project, target_run=task)
            else:
                subs = list(set(subs).intersection(set(get_good_sub(Project, target_run=task))))
        subs.sort()
        for sub in subs:
            for Project, task in zip(Projects, tasks):
                subs_info.append([Project, sub, task])  
    else:
        subs_info = []
        for Project, task in zip(Projects, tasks):
            subs_list = get_good_sub(Project, target_run=task)
            for sub in subs_list:
                subs_info.append([Project, sub, task])   
    
    # 예외 피험자
    final_subs = []
    for [Project, sub, task] in subs_info:
        if sub not in exception: final_subs.append([Project, sub, task])
                
    return final_subs