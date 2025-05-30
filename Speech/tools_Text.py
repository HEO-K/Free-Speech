import os
import numpy as np
import glob

def load_audio_boundary(Project, sub, runname, boundary, ses=None, tr=1000, limiting=True, threshold=3.5):
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
            - long_pause: 길게 쉰 문장 종료
            - center: ev1 중심
        ses (str or int, optional): session number, Defaults to None.
        tr (float, optional): TR (ms)
        limiting (bool, optional): 주제와 중복되지 않는 silence, sentence. Defaults to True.
        threshold (float, optional): silence 기준(초). Defaults to 3.5TR.
        

        
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
    elif boundary == "center":
        filename = "*"+runname+"_event.txt"
    elif boundary == "silence": 
        filename = "*"+runname+"_"+boundary+".txt"
    else:
        filename = "*"+runname+"_sentence.txt"
    
    try:
        filepath = glob.glob(os.path.join(audio_path,filename))[0]
    except:
        raise FileNotFoundError(f"sub-{sub}_task-{filename} don't exist")
    
    
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
        sen_end = np.setdiff1d(sen_end, ev1_end)
        if len(sen_end) == 0:
            return "no boundary"
        elif len(sen_end) > len(ev1_end):
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
            ev = np.array(sen_sim/tr, int)
        else:
            ev = np.array(sen_end/tr, int)
    elif boundary == 'long_pause':
        ev = []
        FA = np.array(load_FA(Project, sub, runname, ses))[:,:2].astype(int)
        with open(filepath, 'r') as f:
            sen = f.readlines() 
        sen = np.array(sen, int) 
        sen_FA = [[FA[0,0], sen[0]]]
        for t in range(len(sen)-1):
            try:
                end = np.where(FA[:,1]==sen[t])[0][0]
                sen_FA.append([FA[end+1,0],sen[t+1]])
            except: pass
        sen_FA = np.array(sen_FA)
        for i in range(sen_FA.shape[0]-1):
            if sen_FA[i+1,0]-sen_FA[i,1]>threshold*tr: ev.append(sen_FA[i,1])
        ev = np.array(np.array(ev)/tr, int)        
                 
    else:
        # file load
        with open(filepath, 'r') as f:
            ev = f.readlines()
        ev = list(filter(None, ev))
        if boundary == "ev1":
            ev = ev[ev.index("[1]\n")+1:ev.index("[2]\n")]
        elif boundary == "ev2":
            ev = ev[ev.index("[2]\n")+1:]
        elif boundary == "silence":
            ev = list(filter(None,ev[0].split("\t")))
            for i in range(len(ev)):
                ev[i] = ev[i].split(":")
            ev = np.array(ev)
            ev = np.array(ev, float)
            ev = ev[ev[:,1]>threshold*tr,0]
        
        elif boundary == 'center':
            ev = ev[ev.index("[1]\n")+1:ev.index("[2]\n")]
            ev = np.array(ev, float)
            center = [ev[0]/2]
            for i in range(len(ev)-1):
                center.append(ev[i]/2+ev[i+1]/2)
            ev = center
                
        
        ev = (np.array(ev, float)/tr).astype(int)
        
        
        if boundary == "silence" or boundary == "sentence":
            if limiting:
                with open(glob.glob(os.path.join(audio_path,"*"+runname+"_event.txt"))[0], 'r') as f:
                    evs = f.readlines()
                evs = list(filter(None, evs))
                ev1 = evs[evs.index("[1]\n")+1:evs.index("[2]\n")]
                ev1 = np.array(np.array(ev1, int)/tr, int)
                ev2 = evs[evs.index("[2]\n")+1:]
                ev2 = np.array(np.array(ev2, int)/tr, int)

                
                try:
                    for i in range(-3,4):
                        ev = np.setdiff1d(ev, ev1+i)
                        ev = np.setdiff1d(ev, ev2+i)
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
    
    filename = f"*task-{runname}*_FA_new.txt"
    
    
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


def get_sentence_FA(Project, sub, runname, ses=None, only_timestamp=False, tr=1000):
    """ 문장 단위의 FA 

    Args:
        Project (str): 프로젝트명
        sub (str): sub number
        runname (str): task이름, ex) speechTOPIC_run-1
        ses (str or int, optional): session number, Defaults to None.
        
    Returns:
        [start, end, sentence]의 리스트

    """

    FA = load_FA(Project, sub, runname, ses=ses)
    words = np.array(FA)[:,-1]
    
    s = 0
    
    sen_FA = []
    for i in range(1,len(words)):
        if words[i][-1] == ".":
            sen_FA.append([FA[s][0], FA[i][1], " ".join(words[s:i+1])])
            s = i+1
    if sen_FA[-1][1] != FA[-1][1]:
        sen_FA.append([FA[s][0], FA[-1][1], " ".join(words[s:])])
    
    if only_timestamp:
        sen_FA = np.array(sen_FA)
        sen_FA = sen_FA[:,:-1].astype(int)
        sen_FA = (sen_FA/tr).astype(int)
    return(sen_FA)


def load_episode_score(Project, sub, runname, ses=None):
    """ 문장 episode score 불러오기 

    Args:
        Project (str): 프로젝트명
        sub (str): sub number
        runname (str): task이름, ex) speechTOPIC_run-1
        ses (str or int, optional): session number, Defaults to None.
        
    Returns:
        1d array

    """
    from . import load_project_info
    audio_path = load_project_info.get_audio_path(Project,derivatives=True)
    audio_path = os.path.join(audio_path, "sub-"+sub)
    if ses != None:
        audio_path = os.path.join(audio_path, "ses-"+str(ses))
    
    filename = f"*task-{runname}_episode.txt"
    filepath = glob.glob(os.path.join(audio_path, filename))[0]
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()
    score = []
    for line in lines:
        try: 
            score.append(int(line))
        except: 
            pass
    return np.array(score, int)



def load_NSP(Project, sub, runname, ses=None, raw=True, save=False, 
             reverse=False, time=None, time_criteria="end"):
    """ Load or Save NSP score

    Args:
        Project (str): 프로젝트명
        sub (str): sub number
        runname (str): task이름, ex) speechTOPIC_run-1
        ses (str or int, optional): session number, Defaults to None.
        raw (bool, optional): get raw NSP. Default to True.
        save (bool, optional): Save file? Defaults to True.
        reverse (bool, optional): Transition value?
        time (int, optional): Load NSP with time. None or TR(ms)
        time_criteria (str, optional): Time criteria. end or start
    """

    from . import load_project_info
    audio_path = load_project_info.get_audio_path(Project, derivatives=True)
    audio_path = os.path.join(audio_path, "sub-"+sub)
    if ses != None:
        audio_path = os.path.join(audio_path, "ses-"+str(ses))
    
    if raw: misc = "_raw"
    else: misc = ""
    
    if ses == None: filename = f"sub-{sub}_task-{runname}_NSP{misc}.txt"
    else: filename = f"sub-{sub}_ses-{ses}_task-{runname}_NSP{misc}.txt"
    
    
    if save:
        from .tools_NLP import get_NSP
        text = np.array(get_sentence_FA(Project, sub, runname, ses=ses))[:,-1]
        NSP = get_NSP(text, raw=raw)   
        if ses == None: filename = f"sub-{sub}_task-{runname}_NSP{misc}.txt"
        else: filename = f"sub-{sub}_ses-{ses}_task-{runname}_NSP{misc}.txt"
        with open(os.path.join(audio_path, filename), "w", encoding="utf-8") as f:
            for score in NSP:
                f.write(str(score) + "\n")
    else:
        try:
            with open(os.path.join(audio_path, filename), "r", encoding="utf-8") as f:
                nextprop = f.readlines()
                NSP = np.array(nextprop, float)
        except:
            from .tools_NLP import get_NSP
            text = np.array(get_sentence_FA(Project, sub, runname, ses=ses))[:,-1]
            NSP = get_NSP(text, raw=raw)   
            if ses == None: filename = f"sub-{sub}_task-{runname}_NSP{misc}.txt"
            else: filename = f"sub-{sub}_ses-{ses}_task-{runname}_NSP{misc}.txt"
            with open(os.path.join(audio_path, filename), "w", encoding="utf-8") as f:
                for score in NSP:
                    f.write(str(score) + "\n")

    if reverse: NSP = -np.array(NSP)

    if time==None: return(NSP)
    else:
        time = int(time)
        FA = get_sentence_FA(Project, sub, runname, ses=ses)
        if time_criteria == "end": FA = (np.array(FA)[:,1]).astype(int)/time
        else: FA = (np.array(FA)[1:,0]).astype(int)/time

        if len(FA) != len(NSP): FA = FA[:len(NSP)]
        return(NSP, FA.astype(int))



def load_NSP_boundary(Project, sub, runname, ses=None, raw=True, bin=[-10,2], tr=1000, boundary="end"):
    """ Load boundary TR based on next sentence prediction score

    Args:
        Project (str): 프로젝트명
        sub (str): sub number
        runname (str): task이름, ex) speechTOPIC_run-1
        ses (str or int, optional): session number, Defaults to None.
        raw (bool, optional): Use raw NSP, Defaults to False
        bin (list, optional): Bin(0% to 100% if raw=True / raw value if raw=False). Defaults to [-10,2].
        tr (int, optional): TR (ms). Defaults to 1000.
        boundary (str, optional): sentence 'start' or 'end', Defaults to end
    Returns:
        TR boundary array (int)
    """
    nextprop = load_NSP(Project, sub, runname, ses=ses, raw=raw)
    
                
    sentence = np.array(get_sentence_FA(Project, sub, runname, ses=ses))[:,:-1].astype(int)

    if boundary == 'start':
        sentence = sentence[1:,0]
    elif boundary == "end":
        sentence = sentence[:-1,1]
    else:
        raise Exception("Boundary option shoud be 'start' or 'end'")

    if raw:
        bound = sentence[(nextprop>bin[0])&(nextprop<bin[1])]
    else:
        bound = sentence[(nextprop>np.percentile(nextprop, bin[0]))&
                        (nextprop<=np.percentile(nextprop, bin[1]))] 
    
    return np.array(bound/tr, int)


def load_PL(Project, sub, runname, ses=None, tr=1000):
    """ Load pause length

    Args:
        Project (str): 프로젝트명
        sub (str): sub number
        runname (str): task이름, ex) speechTOPIC_run-1
        ses (str or int, optional): session number, Defaults to None.
        tr (int, optional): TR (ms). Defaults to 1000.

    Returns:
        PL list
    """    
    from .tools import isWSL

    fa = np.array(get_sentence_FA(Project, sub, runname))[:,:-1].astype(int)
    pause = [fa[i,0]-fa[i-1,1] for i in range(1,fa.shape[0])]
    pause = np.array(pause, int)/tr
    return pause
        


def load_PL_boundary(Project, sub, runname, ses=None, bin=[80,100], tr=1000):
    """ Load boundary TR based on pause length

    Args:
        Project (str): 프로젝트명
        sub (str): sub number
        runname (str): task이름, ex) speechTOPIC_run-1
        ses (str or int, optional): session number, Defaults to None.
        bin (list, optional): Bin(0 to 100). Defaults to [80,100].
        tr (int, optional): TR (ms). Defaults to 1000.

    Returns:
        TR boundary array (int)
    """
    from .tools import isWSL

    fa = np.array(get_sentence_FA(Project, sub, runname, ses=ses))[:,:-1].astype(int)
    sentence = fa[:-1,1]
    pause = [fa[i,0]-fa[i-1,1] for i in range(1,fa.shape[0])]

    bound = sentence[(pause>np.percentile(pause, bin[0]))&
                    (pause<=np.percentile(pause, bin[1]))] 
    
    return np.array(bound/tr, int)



def load_embeddings(Project, sub, runname, ses=None, save=False):
    from . import load_project_info
    audio_path = load_project_info.get_audio_path(Project, derivatives=True)
    audio_path = os.path.join(audio_path, "sub-"+sub)
    if ses != None:
        audio_path = os.path.join(audio_path, "ses-"+str(ses))
    
    if ses == None: filename = f"sub-{sub}_task-{runname}_embedding.npy"
    else: filename = f"sub-{sub}_ses-{ses}_task-{runname}_embedding.npy"
    
    if save:
        from .tools_NLP import get_sentence_embedding
        sentence = np.array(get_sentence_FA(Project, sub, runname, ses=ses))[:,-1]
        embeddings = get_sentence_embedding(sentence)
        np.save(os.path.join(audio_path, filename), embeddings)
    else:
        try:
            embeddings = np.load(os.path.join(audio_path, filename))
        except:
            from .tools_NLP import get_sentence_embedding
            sentence = np.array(get_sentence_FA(Project, sub, runname, ses=ses))[:,-1]
            embeddings = get_sentence_embedding(sentence)
            np.save(os.path.join(audio_path, filename), embeddings)
            
    
    return(embeddings)


def get_embedding_distance(Project, sub, runname, ses=None, metric='cosine'):
    from sklearn.metrics import pairwise_distances
    embeddings = load_embeddings(Project, sub, runname, ses=ses)
    dist_matrix = pairwise_distances(embeddings, metric=metric)
    return np.diag(dist_matrix, k=1)


def get_boundary_sentence(Project, sub, runname, boundary='ev1', ses=None):
    FA = np.array(get_sentence_FA(Project, sub, runname, ses=None))
    end = (FA[:,1]).astype(int)
    ev = load_audio_boundary(Project, sub, runname, boundary, ses=None, tr=1)
    mask = []
    for t in end:
        if t in ev: mask.append(1)
        else: mask.append(0)
    return(np.array(mask,bool))