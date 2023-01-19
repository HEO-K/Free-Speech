import os
import numpy as np
import glob

    
def load_audio_boundary(Project, sub, runname, boundary, ses=None, tr=1.0, limiting=True, threshold=1.8):
    """ Audio boundary 읽어오기

    Args:
        Project (str): 프로젝트명
        sub (str): sub number
        runname (str): task이름, ex) speechTOPIC_run-1
        boundary (str):
            - ev1: 참여자's 대주제
            - ev2: 참여자's 소주제
            - sentence: 문장 종료
            - silence: 침묵 시작
        ses (str or int, optional): session number, Defaults to None.
        tr (float, optional): TR (초)
        limiting (bool, optional): 주제와 중복되지 않는 silence, sentence. Defaults to True.
        threshold (float, optional): silence 기준(초). Defaults to 1.8.

        
    Returns:
       array: event boundary(초)
    """
    from . import load_project_info
    audio_path = load_project_info.get_audio_path(Project)
    audio_path = os.path.join(audio_path, "sub-"+sub)
    if ses != None:
        audio_path = os.path.join(audio_path, "ses-"+str(ses))
    
    if boundary == "ev1" or boundary == "ev2":
        filename = "*"+runname+"_event.txt"
    else: filename = "*"+runname+"_"+boundary+".txt"
    
    try:
        filepath = glob.glob(os.path.join(audio_path,filename))[0]
    except:
        return 
    
    tr = tr*1000
    
    # file load
    with open(filepath, 'r') as f:
        ev = f.readlines()
    ev = list(filter(None, ev))
    if boundary == "ev1":
        ev = ev[ev.index("[1]\n")+1:ev.index("[2]\n")]
    if boundary == "ev2":
        ev = ev[ev.index("[2]\n")+1:]
    if boundary == "silence":
        ev = list(filter(None,ev[0].split("\t")))
        for i in range(len(ev)):
            ev[i] = ev[i].split(":")
        ev = np.array(ev)
        ev = np.array(ev, float)
        ev = ev[ev[:,1]>threshold*tr,0]
    ev = np.round(np.array(ev, float)/tr)
    ev = np.array(ev, int)
    
    if boundary == "silence" or boundary == "sentence":
        if limiting:
            with open(glob.glob(os.path.join(audio_path,"*"+runname+"_event.txt"))[0], 'r') as f:
                evs = f.readlines()
            evs = list(filter(None, evs))
            ev1 = evs[evs.index("[1]\n")+1:evs.index("[2]\n")]
            ev1 = np.round(np.array(ev1, int)/tr)
            ev1 = np.array(ev1, int)
            ev2 = evs[evs.index("[2]\n")+1:]
            ev2 = np.round(np.array(ev2, int)/tr)
            ev2 = np.array(ev2, int)
            
            try:
                for i in range(-10,11):
                    ev = np.array(list(set(ev)-set(ev1+i)-set(ev2+i)))
            except:
                print("there's no independent "+ boundary+". just return all")
                
            ev.sort() 
    return ev
    

def load_sentence(Project, sub, runname, ses=None):
    """ 텍스트 읽어오기

    Args:
        Project (str): 프로젝트명
        sub (str): sub number
        runname (str): task이름, ex) speechTOPIC_run-1
        ses (str or int, optional): session number, Defaults to None.
        
    Returns:
       list: 문장으로 이뤄져 있는 리스트
    """
    from . import load_project_info
    audio_path = load_project_info.get_audio_path(Project,derivatives=False)
    audio_path = os.path.join(audio_path, "sub-"+sub)
    if ses != None:
        audio_path = os.path.join(audio_path, "ses-"+str(ses))
    
    filename = f"*task-{runname}_STT_new.txt"
    
    try:
        filepath = glob.glob(os.path.join(audio_path,filename))[0]
    except:
        return 
    
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()
    for i, line in enumerate(lines):
        lines[i] = line.strip()
    return lines


def load_TA(Project, sub, runname, ses=None, TR=None):
    """ TA 읽어오기

    Args:
        Project (str): 프로젝트명
        sub (str): sub number
        runname (str): task이름, ex) speechTOPIC_run-1
        ses (str or int, optional): session number, Defaults to None.
        TR (int, optional): TR로 나눠진 TA, Defaults to None.
        
    Returns:
        - TR=None의 경우: [start, end, word]의 리스트
        - TR을 준 경우: 한 TR내 [word들]의 리스트
    """
    
    from . import load_project_info
    audio_path = load_project_info.get_audio_path(Project,derivatives=False)
    audio_path = os.path.join(audio_path, "sub-"+sub)
    if ses != None:
        audio_path = os.path.join(audio_path, "ses-"+str(ses))
    
    filename = f"*task-{runname}_FA_new.txt"
    
    
    TA = []
    words = []
    filepath = glob.glob(os.path.join(audio_path, filename))[0]
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()
    for line in lines:
        time_and_word = line.split()
        times = [int(time_and_word[0]), int(time_and_word[1])]
        TA.append(times)
        words.append(time_and_word[2])
        
    
    if TR == None:
        for i, word in enumerate(TA):
            TA[i] = word+[words[i]]
        return TA
    
    else:
        words = np.array(words)
        word_start = []
        for t in TA:
            word_start.append(t[0])
        word_start = np.array(word_start)
        TA_words = []
        TRs = np.arange(0,np.max(TA)/1000+TR,TR)*1000
        for i in range(len(TRs)-1):
            TA_words.append(list(words[(word_start>=TRs[i])&(word_start<TRs[i+1])]))
        return(TA_words)    


