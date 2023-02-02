# %%
# 이 단락은 수정하지 않는다.
import requests
import json
import glob
import numpy as np
import os


# 받아쓰기 function
def Clova_STT(file_path):
    """ 오디오 파일 위치에 단어 정렬 결과(_FA.txt) 저장
    
        Args: 
            file_path (str): 오디오 파일 경로
    """
    
    invoke_url = 'https://clovaspeech-gw.ncloud.com/external/v1/2227/2752bda02f64f65c39aef44ddfe935dd3a6a7c9c061e687484f67707ee3f975c'
    secret = '03bbf8f1bea54866bbd108c26845160e'          
    request_body = {
        'language': 'ko-KR',
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

    # FA결과
    results = json.loads(results)
    sentences = results['segments']
    FA = sentences[0]['words']
    for i in range(1,len(sentences)):
        FA = FA + sentences[i]['words']
    # 결과 저장하기
    f_FA = open(file_path.split(".")[0]+"_FA.txt", 'w', encoding="utf-8")
    for i in range(len(FA)):
        f_FA.write('{0:<8}{1:<8}{2}\n'.format(FA[i][0], str(FA[i][1]), str(FA[i][2])))
    f_FA.close()
    return "Finished"


# %%
# 아래 변수는 내 환경에 맞게 조절한다.
# 그룹 & 세션 별로 모든 오디오 파일에 대해서 코드가 돌아간다.
audio_path = "D:\MRIting\_DATA_Audio"   # 오디오 파일 저장되어있는 최상위 폴더
group_number = '01'        # 그룹 번호(ex, 0701이라면 앞의 07만)
session = "1"              # 세션


# 받아쓰기 및 수정
for sex in ["01", "02"]:
    subname = "sub-"+group_number+sex
    sesname = "ses-"+session
    wildcard = "*"+subname+"*.wav"
    filepath = os.path.join(audio_path, subname, sesname, wildcard)
    
    files = glob.glob(filepath)
    for file in files:
        Clova_STT(file)
        input(os.path.basename(file)[:-4]+"_FA.txt를 수정한 뒤, '_FA_new.txt' 라는 이름으로 저장한다. 완료했으면 엔터키")
    


# session 1이라면 둘을 합치는 과정이 필요하다.
if session == "1":
    os.makedirs(os.path.join(audio_path, "_for_posthoc", "group-"+group_number), exist_ok=True)
    
    import openpyxl
    import pandas as pd
    subname = "sub-"+group_number+"01"
    subname_woman = "sub-"+group_number+"02"
    sesname = "ses-"+session
    
    FA_wildcard = "*"+subname+"*_audio_FA_new.txt"

    
    FA_files = glob.glob(os.path.join(audio_path, subname, sesname, FA_wildcard))
    
    # 존재하는 모든 _FA_new.txt 파일에 대해서 수행
    for file in FA_files:
        # 남자 시간
        man_file = file.split("_audio_FA_new.txt")[0] + "_timestamp.txt"
        
        with open(man_file, "r") as f:
            start_time = f.readline()
            start_time = start_time.split(":")
            hour = int(start_time[0][-2:])
            minute = int(start_time[1])
            second = int(start_time[2])
            milsec = int(start_time[3])
            time_man = milsec+1000*second+minute*60*1000+hour*60*60*1000
            f.close()
        
        # 여자 시간
        woman_file = subname_woman+os.path.basename(man_file)[8:]
        woman_file = os.path.join(audio_path, subname_woman, sesname, woman_file)
        with open(woman_file, "r") as f:
            start_time = f.readline()
            start_time = start_time.split(":")
            hour = int(start_time[0][-2:])
            minute = int(start_time[1])
            second = int(start_time[2])
            milsec = int(start_time[3])
            time_woman = milsec+1000*second+minute*60*1000+hour*60*60*1000
            f.close()
        
        
        # 딜레이 계산
        delay = time_man-time_woman

        
        all_FA = pd.DataFrame({"speaker":[], "start":[], "end":[], "word":[]})
        # 남성 FA
        i=0
        with open(file, "r", encoding="utf-8") as f:
            FA = f.readlines()
            for line in FA:
                if delay>0:
                    all_FA.loc[i] = ["M", int(line.split()[0]), int(line.split()[1]), line.split()[2]]
                    i += 1
                else:
                    all_FA.loc[i] = ["M", int(line.split()[0])+abs(delay), int(line.split()[1])+abs(delay), line.split()[2]]
                    i += 1
        # 여성 FA
        with open(woman_file.split('_timestamp.txt')[0]+"_audio_FA_new.txt", "r", encoding="utf-8") as f:
            FA = f.readlines()
            for line in FA:
                if delay>0:
                    all_FA.loc[i] = ["W", int(line.split()[0])+abs(delay), int(line.split()[1])+abs(delay), line.split()[2]]
                    i += 1
                else:
                    all_FA.loc[i] = ["W", int(line.split()[0]), int(line.split()[1]), line.split()[2]]
                    i += 1
        
        # 정렬 완료
        all_FA_sorted = np.array(all_FA.sort_values(by="start"))
        
        new_FA_line = pd.DataFrame({"speaker":[], "start":[], "end":[], "line":[]})
        line = 0
        start_sex = all_FA_sorted[0,0]
        start_time = all_FA_sorted[0,1]
        end_time = all_FA_sorted[0,2]
        start_line = all_FA_sorted[0,3]
        
        for word in all_FA_sorted[1:,:]:
            if start_sex == word[0]:
                start_line = start_line + " " + word[3]
                end_time = word[2]
            else:
                new_FA_line.loc[line] = [start_sex, start_time, end_time, start_line]
                line += 1
                start_sex = word[0]
                start_time = word[1]
                end_time = word[2]
                start_line = word[3]    
        new_FA_line.loc[line] = [start_sex, start_time, end_time, start_line]        
        
        # 새로운 정렬된 FA를 엑셀로 저장
        exel_filename = file.split('_audio_FA_new.txt')[0]
        exel_filename = "group-" + group_number + "_ses-1_task" + exel_filename.split("task")[-1] + "_posthoc.xls"
        exel_filename = os.path.join(audio_path, "_for_posthoc", "group-"+group_number, exel_filename)
        new_FA_line.to_excel(exel_filename)
        
        
# %%
