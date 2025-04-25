# %%
# custom functions for speech_3T project
import numpy as np
import os
from Speech.load_project_info import get_good_sub


# 피험자 목록 불러오기
def good_subs(taskname, exception=[]):
    """ speech_3T의 피험자 불러오기

    Args:
        taskname (str): 과제명 (TA, 3, 3H, Z, S, LTA, L3, L, R, M, A)
            \- TA: think aloud
            \- 3: three topics
            \- 3H: three topics_about human 
            \- Z: zig-zag
            \- S: all speech tasks (only speech_3T_v2)
            \- LTA: listening think aloud
            \- L3: listening three topics
            \- L: all listening tasks
            \- R: resting
            \- M: movie recall
            \- A: Autobigraphical recall
            \- T: Z thinking
        exception (string list, optional): 예외 subject list. Defaults to [].
        
    Returns: [Project, sub, task] list
    
    """
    if taskname == "TA":
        Projects = ["speech_3T","speech_3T_v2", "speech_3T_v3"]
        tasks = ["speechFREE", "speechFREE", "speechFREE"]
    elif taskname == "3":
        Projects = ["speech_3T","speech_3T_v2"]
        tasks = ["speechTOPIC_run-1", "speechTOPIC"]    
    elif taskname == "3H":
        Projects = ["speech_3T_v3"]
        tasks = ["speechTOPIC"]   
    elif taskname == "Z":
        Projects = ["speech_3T_v2", "speech_3T_v3", "speech_3T_v4"]
        tasks = ["speechSTROLL", "speechSTROLL",  "speechSTROLL"]    
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
        Projects = ["speech_3T","speech_3T_v2", "speech_3T_v3"]
        tasks = ["REST", "REST", "REST"]  
    elif taskname == "M":
        Projects = ["KDS_movie", "KDS_movie", "KDS_movie"]
        tasks = ["recall_run-1", "recall_run-2", "recall_run-3"]
    elif taskname == "A":
        Projects = ["speech_3T_v3", "speech_3T_v4"]
        tasks = ["speechRECALL", "speechRECALL"]
    elif taskname == "T":
        Projects = ["speech_3T_v4"]
        tasks = ["thinkSTROLL"]        

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


def load_think_transition(Project, sub, tr=1000):
    from Speech.load_project_info import get_audio_path
    tr = tr/1000
    audio_path = get_audio_path(Project, False)
    text_file = os.path.join(audio_path, f"sub-{sub}", f"sub-{sub}_task-THINK_transition.txt")
    with open(text_file, "r") as f:
        lines = f.readlines()
        start = int(lines[0].replace("start:",""))
        transitions = np.array(lines[1:], float)
        transitions = (transitions/tr).astype(int)
    return([start, transitions])




def load_roi(name, output="mask", vox="3.0"):
    roi_list={
        "HPC": ["Brainnetome", [215,216,217,218],],
        "PCN": ["Schaefer2018_400Parcels_17Networks", [144,145,146,147,148,351,352,353,354,355,356,357]],
        "IPS": ["Schaefer2018_400Parcels_17Networks", [122,123,124,125,126,325,326,327,328]],
        "rIPS": ["Schaefer2018_400Parcels_17Networks", [325,326,327,328]],
        "rIPL": ["Schaefer2018_400Parcels_17Networks", [325,326,327,328,304]],
        "PCun": ["Schaefer2018_400Parcels_17Networks", list(np.arange(154,161))+list(np.arange(363,368))],
        "A1": ["Schaefer2018_400Parcels_17Networks", [44,45,244,245]],
        
    }
    
    from Speech.tools_EPI import get_parcel_roi_mask
    roi_mask = get_parcel_roi_mask(roi_list[name][0], roi_list[name][1], size=vox)
    
    if output=="mask": return(roi_mask)
    elif output=="all": return([roi_mask, roi_list[name]])
    elif output=="info": return(roi_list[name])
    else: raise Exception("output option is wrong. It would be ['mask','info','all']")
    
    

def load_colors(name, scale=1, alpha=None):
    color_list={
        "PCN": [159,176,208],
        "IPS": [233,168,31],
        "rIPS": [233,168,31],
        "rIPL": [233,168,31],
        "PCun": [252,243,50],
        "HPC": [171,0,237],
        "ev1": [255,65,74],
        "ev": [255,65,74],
        "topic": [255,65,74]
        
    }
    
    color = color_list[name]

    if alpha:
        color.append(alpha)
        
    color = np.array(color)
    color = color*(scale/255)

    if scale==255: color = color.astype(int)

    return color
    
    
    
def set_matplotlib():
    import matplotlib as mpl
    import matplotlib.font_manager as fm

    from Speech.tools import isWSL
    if isWSL():
        fname = '/mnt/c//Users/Kwon/AppData/Local/Microsoft/Windows/Fonts/Helvetica.ttf'
    else:
        fname = 'C:/Users/Kwon/AppData/Local/Microsoft/Windows/Fonts/Helvetica.ttf'

    fe = fm.FontEntry(
        fname=fname,
        name="Helvetica")
    fm.fontManager.ttflist.insert(0, fe) # or append is fine
    mpl.rcParams['font.family'] = fe.name
    mpl.rc('font', family = 'Helvetica', size = 10)
    mpl.rc('savefig', transparent = True)
    spines = {"top": False, "right": False}
    mpl.rc('axes.spines', **spines)

    