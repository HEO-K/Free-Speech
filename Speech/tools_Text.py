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
            - sen_limited: 주제 변환 아닌 문장 종료 중 쉬는 시간 길이 비슷한 같은 수의 주제
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
    elif boundary == "silence": 
        filename = "*"+runname+"_"+boundary+".txt"
    else:
        filename = "*"+runname+"_sentence.txt"
    
    try:
        filepath = glob.glob(os.path.join(audio_path,filename))[0]
    except:
        return "No files"
    
    
    if boundary == "sen_limited":
        times = np.array(load_FA(Project, sub, runname, ses))[:,:2].astype(int)
            
        with open(glob.glob(os.path.join(audio_path,"*"+runname+"_event.txt"))[0], 'r') as f:
            evs = f.readlines()
        evs = list(filter(None, evs))
        ev1_end = np.array(evs[evs.index("[1]\n")+1:evs.index("[2]\n")], dtype=int)
        
        with open(filepath, 'r') as f:
            sen_end = f.readlines()
        sen_end = np.array(sen_end, dtype=int)
        
        # 같은 것은 솎아내기
        sen_end = set(sen_end) - set(ev1_end)
        sen_end = list(sen_end)
        sen_end.sort()
        sen_end = np.array(sen_end)
        
        # ev1의 침묵 시간
        ev1_sil = []
        for ev1 in ev1_end:
            try:
                index = np.where(times[:,1]==ev1)[0][0]
                ev1_sil.append(times[index+1,0]-times[index,1])
            except: pass
            
        ev1_sil_mean = np.mean(ev1_sil)
                
        # sentence의 침묵 시간
        sen_sil = []
        for sen in sen_end:
            try:
                index = np.where(times[:,1]==sen)[0][0]
                sen_sil.append([times[index+1,0]-times[index,1],sen])
            except: pass
        sen_sil = np.array(sen_sil)
          
        sen_sil_diff = np.absolute(sen_sil[:,0]-ev1_sil_mean)
        from scipy.stats import rankdata
        sen_sim = sen_sil[rankdata(sen_sil_diff)<len(ev1_end)+1,1]

        tr = tr*1000
        ev = np.round(sen_sim/tr).astype(int)
        
    else:
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
    audio_path = load_project_info.get_audio_path(Project,derivatives=True)
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


def load_FA(Project, sub, runname, ses=None, TR=None):
    """ FA 읽어오기

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
    audio_path = load_project_info.get_audio_path(Project,derivatives=True)
    audio_path = os.path.join(audio_path, "sub-"+sub)
    if ses != None:
        audio_path = os.path.join(audio_path, "ses-"+str(ses))
    
    filename = f"*task-{runname}_FA_new.txt"
    
    
    FA = []
    words = []
    filepath = glob.glob(os.path.join(audio_path, filename))[0]
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()
    for line in lines:
        time_and_word = line.split()
        times = [int(time_and_word[0]), int(time_and_word[1])]
        FA.append(times)
        words.append(time_and_word[2])
        
    
    if TR == None:
        for i, word in enumerate(FA):
            FA[i] = word+[words[i]]
        return FA
    
    else:
        words = np.array(words)
        word_start = []
        for t in FA:
            word_start.append(t[0])
        word_start = np.array(word_start)
        FA_words = []
        TRs = np.arange(0,np.max(FA)/1000+TR,TR)*1000
        for i in range(len(TRs)-1):
            FA_words.append(list(words[(word_start>=TRs[i])&(word_start<TRs[i+1])]))
        return(FA_words)    



def get_phrase_FA(Project, sub, runname, ses=None):
    """ 절 단위의 FA 

    Args:
        Project (str): 프로젝트명
        sub (str): sub number
        runname (str): task이름, ex) speechTOPIC_run-1
        ses (str or int, optional): session number, Defaults to None.
        
    Returns:
        [start, end, phrase]의 리스트

    """
    
    from .tools_NLP import etri_dparse
    text = " ".join(load_sentence(Project, sub, runname, ses=ses))
    FA = load_FA(Project, sub, runname, ses=ses, TR=None)
    
    # 문장 구조 분석
    dparse_results = etri_dparse(text)
    
    phrase_FA = []
    line_start = 0
    for line in dparse_results:
        word_index = np.arange(len(line["word"]))+line_start
        words = [word["text"] for word in line["word"]]
        phrase_begin = 0
        for phrase_tag in line['phrase_dependency']:
            if phrase_tag['label'] == "S":   # 문장 태그
                phrase = " ".join(words[phrase_begin:phrase_tag['end']+1])   # 절
                phrase_timestamp = [FA[word_index[phrase_begin]][0], FA[word_index[phrase_tag['end']]][1]]
                phrase_FA.append(phrase_timestamp+[phrase])

                # 절 시작 업데이트
                phrase_begin = phrase_tag['end']+1
        
        
        # 결과가 단 하나의 문장으로만 이뤄진 경우 'S'라벨이 없다 -> 그냥 추가
        if len(phrase_FA) < 1:
            phrase = " ".join(words[phrase_begin:])
            phrase_timestamp = [FA[word_index[phrase_begin]][0], FA[word_index[-1]][1]]
            phrase_FA.append(phrase_timestamp+[phrase])
        elif phrase_FA[-1][-1].split()[-1] != words[-1]:
            phrase = " ".join(words[phrase_begin:])
            phrase_timestamp = [FA[word_index[phrase_begin]][0], FA[word_index[-1]][1]]
            phrase_FA.append(phrase_timestamp+[phrase])           
        # 현재 줄의 단어 인덱스 업데이트
        line_start += len(line["word"])
    
    return(phrase_FA)