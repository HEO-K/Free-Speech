# %%
# custom functions for speech_3T project
import numpy as np
from Speech.load_project_info import get_good_sub
def good_subs(taskname, exception=[]):
    """ speech_3T의 피험자 불러오기

    Args:
        taskname (str): 과제명 (TA, M, G, 3)
            \- TA: think aloud
            \- M: movie
            \- G: game
            \- 3: three topics
        exception (string list, optional): 예외 subject list. Defaults to [].
        
    Returns: [Project, sub, ses,task] list
    """
    
    if taskname == "TA":
        Project = "NatPAC_speech"
        tasks = ["speechFREE_run-1"]
        sess = [["01", "01R", "11", "11R"]]
    elif taskname == "M":
        Project = "NatPAC_speech"
        tasks = ["speechMOVIE_run-1"]
    elif taskname == "G":
        Project = "NatPAC_speech"
        tasks = ["speechMC_run-1"]   
    elif taskname == "3": 
        Project = "NatPAC_speech"
        tasks = ["speechTOPICS_run-1"] 
        sess = [["10", "10R"]]
    subs_info = []
    for task, ses_list in zip(tasks, sess):
        for ses in ses_list:
            try:
                subs_list = get_good_sub(Project, ses=ses,target_run=task)
                for sub in subs_list:
                    subs_info.append([Project, sub, ses, task])  
            except: pass
    return subs_info
# %%
