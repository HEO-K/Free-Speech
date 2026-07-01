# %%
# custom functions for speech_3T project
import numpy as np
from Speech.load_project_info import get_good_sub
def good_subs(taskname, exception=[]):
    """ speech_3T의 피험자 불러오기

    Args:
        taskname (str): 과제명 (TA, M, G, 3)
            - TA: think aloud
            - M: movie
            - G: game
            - 3: three topics
        exception (string list, optional): 예외 subject list. Defaults to [].
        
    Returns: [Project, sub, ses,task] list
    """
    
    if taskname == "TA":
        Project = "NatPAC_speech"
        task = "speechFREE_run-1"
        ses = "01"
    elif taskname == "3": 
        Project = "NatPAC_speech"
        task = "speechTOPICS_run-1"
        ses = "10"
        
        
    subs_info = []
    ses_list = [ses+"R", ses+"A", ses]
    for ses in ses_list:
        try:
            subs_list = get_good_sub(Project, ses=ses,target_run=task)
            for sub in subs_list:
                subs_info.append([Project, sub, ses, task])  
        except: pass
    
    # 예외 피험자
    final_subs = []
    for [Project, sub, ses, task] in subs_info:
        if sub not in exception: final_subs.append([Project, sub, ses, task])
    final_subs.sort()        
    return final_subs