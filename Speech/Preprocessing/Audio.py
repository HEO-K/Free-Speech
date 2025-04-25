import requests
import json
import glob
import numpy as np
import os
import warnings

# STT
def Clova_STT(file_path, lang="ko-KR", output="", save_STT=True, showresults=False):
    """ 오디오 파일의 받아쓰기 결과(_STT.txt) & 단어 정렬 결과(_FA.txt) 저장
    
        Args: 
            file_path (str): 오디오 파일 경로
            lang (str): 받아쓸 언어 (default: ko-KR)
            output (str): STT, FA결과 저장할 경로 (default: 오디오 파일 위치)
            save_STT: STT결과 저장 여부 (default: True)
            showresults: 결과 출력 여부 (default: False)
    """
    
    invoke_url = 'Clova URL'
    secret = 'Clova secret key'          
    request_body = {
        'language': lang,
        'completion': 'sync',
        'callback': None,
        'userdata': None,
        'wordAlignment': True,
        'fullText': True,
        'forbiddens': None,
        'boostings': None,
        'diarization': None,
    }
    headers = {
        'Accept': 'application/json;UTF-8',
        'X-CLOVASPEECH-API-KEY': secret
    }
    files = {
        'media': open(file_path, 'rb'),
        'params': (None, json.dumps(request_body, ensure_ascii=False).encode('UTF-8'), 'application/json')
    }
    response = requests.post(headers=headers, url=invoke_url + '/recognizer/upload', files=files)
    # 클로바 요청
    results = response.text

    #  STT와 FA결과
    results = json.loads(results)
    sentences = results['segments']
    full_text = results['text']
    FA = sentences[0]['words']
    for i in range(1,len(sentences)):
        FA = FA + sentences[i]['words']
    # 결과 저장하기
    if len(output) == 0:
        if save_STT:
            f_stt = open(file_path.split(".")[0]+"_STT.txt", 'w', encoding="utf-8")
            f_stt.write(full_text)
            f_stt.close()
        f_FA = open(file_path.split(".")[0]+"_FA.txt", 'w', encoding="utf-8")
        for i in range(len(FA)):
            f_FA.write('{0:<8}{1:<8}{2}\n'.format(FA[i][0], str(FA[i][1]), str(FA[i][2])))
        f_FA.close()
    else:
        try:
            filename = os.path.basename(file_path).split(".")[0]
            if save_STT:
                f_stt = open(os.path.join(file_path, filename+"_STT.txt"), 'w', encoding="utf-8")
                f_stt.write(full_text)
                f_stt.close()
            f_FA = open(os.path.join(file_path, filename+"_FA.txt"), 'w', encoding="utf-8")
            for i in range(len(FA)):
                f_FA.write('{0:<8}{1:<8}{2}\n'.format(FA[i][0], str(FA[i][1]), str(FA[i][2])))
            f_FA.close()
        except:
            warnings.warn(f'Path "{output}" does not exist. Save at audio path "{os.path.dirname(file_path)}"')
            if save_STT:
                f_stt = open(file_path.split(".")[0]+"_STT.txt", 'w', encoding="utf-8")
                f_stt.write(full_text)
                f_stt.close()
            f_FA = open(file_path.split(".")[0]+"_FA.txt", 'w', encoding="utf-8")
            for i in range(len(FA)):
                f_FA.write('{0:<8}{1:<8}{2}\n'.format(FA[i][0], str(FA[i][1]), str(FA[i][2])))
            f_FA.close()            
    if showresults: return(results)

# second processing
def apply_FA(file_path):
    """ _FA_new.txt파일을 통해 _STT_new.txt를 생성
    
        Args: 
            file_path (str): _FA_new.txt 파일 경로
    """
    STT_new = []
    try: f_FA_new = open(file_path, 'r', encoding="utf-8")
    except: f_FA_new = open(file_path.replace(".wav", "_audio.wav"), 'r', encoding="utf-8")
    FA_new_lines = f_FA_new.readlines()
    for line in FA_new_lines:
        try:
            word = " ".join(line.split()[2:])
            STT_new.append(word)
        except:
            pass

    STT_new = " ".join(STT_new).split(". ")
    f_stt_new = open(file_path[:-11]+"_STT_new.txt", 'w', encoding="utf-8")
    for i in range(len(STT_new)):
        if i == len(STT_new)-1:
            f_stt_new.write(STT_new[i])
        else:
            f_stt_new.write(STT_new[i]+".\n")
    f_stt_new.close()


# audiostamp
def audiostamp(input, output_folder="./"):
    """ FA_new.txt를 통해 문장의 종결 지점 & topic boundary를 추가해야 할 더미 파일 저장

    Args:
        input (str): *_FA_new.txt
        output_folder (str, optional): 결과 파일 위치. Defaults to "./".
    """
    os.makedirs(output_folder, exist_ok=True)
    with open(input, 'r', encoding="utf-8") as f:
        text = f.readlines()
    # speech time
    timestamp = []
    for line in text:
        line = line.split()
        timestamp.append(line[:2])
    timestamp = np.array(timestamp, dtype=int)
    # sentence
    sentence = []
    for line in text:
        if line.strip()[-1] == "." or line.strip()[-1] == "?":
            sentence.append(line.split()[1])
    # save
    # sentence
    with open(os.path.join(output_folder, filename+"_sentence.txt"), 'w', encoding="utf-8") as f:
        for time in sentence:
            f.write(time)
            if not time == sentence[-1]: f.write("\n")
    # save
    # dummy: topic
    with open(os.path.join(output_folder, filename+"_event.txt"), 'w', encoding="utf-8") as f:
        f.write("[1]\n\n[2]\n")
        
        

def Clova_confidence(file_path, lang="ko-KR"):
    """ Clova STT의 confidence를 출력
        Args: 
            file_path (str): 오디오 파일 경로
    """
    
    invoke_url = 'https://clovaspeech-gw.ncloud.com/external/v1/2227/2752bda02f64f65c39aef44ddfe935dd3a6a7c9c061e687484f67707ee3f975c'
    secret = '03bbf8f1bea54866bbd108c26845160e'          
    request_body = {
        'language': lang,
        'completion': 'sync',
        'callback': None,
        'userdata': None,
        'wordAlignment': True,
        'fullText': True,
        'forbiddens': None,
        'boostings': None,
        'diarization': None,
    }
    headers = {
        'Accept': 'application/json;UTF-8',
        'X-CLOVASPEECH-API-KEY': secret
    }
    files = {
        'media': open(file_path, 'rb'),
        'params': (None, json.dumps(request_body, ensure_ascii=False).encode('UTF-8'), 'application/json')
    }
    response = requests.post(headers=headers, url=invoke_url + '/recognizer/upload', files=files)
    # 클로바 요청
    results = response.text
        
    #  STT와 FA결과
    results = json.loads(results)
    results = results["segments"]
    scores = []
    for line in results:
        scores.append(line['confidence'])
    
    return(np.array(scores))
