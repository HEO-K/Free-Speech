# %%
import numpy as np
import os
import json

# 정보 파일 저장 위치: Speech/_data_Project/Project_Name/에 저장됨
base_path = "D:/Functions/Speech/_data_Project"
#base_path = "/mnt/d/Functions/Speech/_data_Project"



#####################################################################################
# 프로젝트 이름 
Project_name = "MRIting"
os.makedirs(os.path.join(base_path,Project_name), exist_ok=True)
# bids path
bids_path = "/mnt/d/MRIting/_DATA_fMRI"
# for WSL environment, ubuntu면 빈 문자열으로
bids_path_window = "D:/MRIting/_DATA_fMRI" 
# session이 존재하면 그 개수를, 아니면 0
sessions = 2

audio_path = "/mnt/d/MRIting/_DATA_Audio"
audio_path_window = "D:/MRIting/_DATA_Audio"



#####################################################################################
# run 정보, 세션이 여러개라면 이중 리스트를 만들어야 한다. 하나면 단일 리스트 (ex: [[ses1],[se2]])
# task 이름은 bids format에서 task-XXX로 붙는 이름이다.
# fMRI protocol 이름은 위 task이름이 기준이다. task-speech_run-1(task name) --> SPEECH1(protocol name) 
# 위의 조건에 맞지 않을 경우 실행 안되므로 protocol이름을 수정하거나 아니면 코드를 수정한다.
run_name = [["RATING", "INTRO", "CHATTING", "T1", "UNI", "INV1", "INV2", "TRUTHLIE"],
            ["RECALL", "RESTING", "SPEECH", "T1", "UNI", "INV1", "INV2", "MOVIE"]] # T1도 포함해야.

# 각 task마다 최대 run수 (T1포함-> T1은 0으로), bids의 run-XX이 안나오게 하길 원한다면 0으로,
# run-1이 무조건 붙어 있게 하고프면 1으로 하면 된다.
# session마다 만들어야 하며, 역시 여러 세션이면 이중 리스트, 아니면 단일 리스트로
run_numbers = [[6,3,0,0,0,0,0,0], 
               [3,0,0,0,0,0,0,3]]



#####################################################################################
# 여기부턴 바꾸지 않는다.
# json 생성
if sessions == 0:
    info = []
    for i in range(len(run_name)):
        run_data = {}
        run_data['name'] = run_name[i]
        if run_numbers[i]: run_data['runs'] = run_numbers[i]
        # try:
        #     if run_type[i]: run_data['type'] = run_type[i]
        # except: pass
        info.append(run_data)

    project_data = {
        'Name': Project_name,
        'bids_path': bids_path,
        'bids_path_window': bids_path_window,
        'audio_path': audio_path,
        'audio_path_window': audio_path_window,
        'info': info
    }

else: 
    project_data = {
        'Name': Project_name,
        'bids_path': bids_path,
        'bids_path_window': bids_path_window
    }

    for ses in range(sessions):
        info = []
        for i in range(len(run_name[ses])):
            run_data = {}
            run_data['name'] = run_name[ses][i]
            if run_numbers[ses][i]: run_data['runs'] = run_numbers[ses][i]
            # try:
            #     if run_type[ses][i]: run_data['type'] = run_type[ses][i]
            # except: pass
            info.append(run_data)
            
        project_data["ses-"+str(ses+1)] = info
        

# 저장
json_path = os.path.join(base_path, Project_name, "project_info.json")
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(project_data, f, indent=4)

# %%
