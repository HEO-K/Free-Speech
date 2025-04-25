# %%
import numpy as np
import os
import json
from Speech.tools import isWSL



############################## 파라메터 수정 필요 ####################################
# 정보 파일 저장 위치: Speech/_data_Project/Project_Name/에 저장됨
if  isWSL(): base_path = "/mnt/d/Functions/Speech/_data_Project"
else: base_path = "D:/Functions/Speech/_data_Project"

# 프로젝트 이름 
Project_name = "Paranoia"
os.makedirs(os.path.join(base_path,Project_name), exist_ok=True)
# bids path
bids_path = "/mnt/f/Paranoia/_DATA_fMRI"
# for WSL environment, ubuntu면 빈 문자열으로
bids_path_window = "F:/Paranoia/_DATA_fMRI" 

# audio path
audio_path = "/mnt/f/Moth/_DATA_Audio"
audio_path_window = "F:/Moth/_DATA_Audio"


####################################################################################
ses = input("세션 이름('ses-'제외)을 입력, 띄어쓰기로 구분 (ex, '01 02'), 없으면 그냥 엔터")

ses_info = dict()
if len(ses.strip()) > 0:
    for ses_name in ses.strip().split(" "):
        ses_info["ses-"+ses_name] = []
else:
    ses_info["info"] = []
for key in ses_info:
    text = "런 이름을 입력하세요 (T1포함). 더이상 없을 경우 esc"
    if key != "info": text = f"{key}의 "+text
    while True:
        name = input(text)
        name = name.strip()
        if len(name) > 0:
            runinfo = {"name": name}
            types = input(f"{name}의 종류를 입력하세요 (anat, fmap, func).")
            runinfo["type"] = types
            if types.strip() == "func":
                runs = input(f"{name}의 개수를 입력하세요. 1개 이상일 경우 run라벨이 붙습니다.")
                try:
                    runs = int(runs)
                    if runs>0: runinfo["runs"] = runs
                except: pass
            modality = input(f"{name}의 모달리티를 입력하세요. 예시 | EPI: bold | T1: T1w | GRE: phase, magnitude 각각 런 있어야 함 | MP2RAGE: MP2RAGE, UNI는 UNIT1 | topup용 반대 dir: epi")
            if len(modality.strip()) > 0: runinfo['modality'] = modality
        else: break
        ses_info[key].append(runinfo)


#####################################################################################
# 여기부턴 바꾸지 않는다.
# json 생성

project_data = {
    'Name': Project_name,
    'bids_path': bids_path,
    'bids_path_window': bids_path_window,
    'audio_path': audio_path,
    'audio_path_window': audio_path_window
}

for key in ses_info:
    project_data[key] = ses_info[key]




# 저장
json_path = os.path.join(base_path, Project_name, "project_info.json")
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(project_data, f, indent=4)

# %%
