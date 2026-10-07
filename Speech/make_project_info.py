# %%
import numpy as np
import os
import json
from Speech.tools import isWSL, native_path, to_windows_path



############################## 파라메터 수정 필요 ####################################
# 레지스트리 키 위치: Speech/_data_Project/Project_Name/ 에는 redirect 한 줄만 두고,
# project_info.json 본문은 데이터셋 안 <root>/registry/Project_Name/ 에 저장됨
if  isWSL(): base_path = "/mnt/d/Functions/Speech/_data_Project"
else: base_path = "D:/Functions/Speech/_data_Project"

# 프로젝트 이름
Project_name = "Paranoia"
# 데이터 루트 — 어느 OS 형식이든 된다 (tools.native_path 가 변환)
root = "F:/Paranoia"
# root 상대경로. 로컬에 없는 데이터는 키를 지운다 (README "프로젝트 등록" 참고)
paths = {
    "rawdata": "rawdata",
    "fmriprep": "derivatives/fmriprep",
    "audio": "sourcedata/audio",
    "transcripts": "derivatives/transcripts",
    "cache": "derivatives/cache",
}


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
                runs = input(f"{name}의 runs 를 입력하세요. 정수 n 이면 run-1~n, 리스트(예: [2], [1, 3])면 그 번호만 run 라벨이 붙습니다. 없으면 엔터")
                try:
                    runs = json.loads(runs)
                    if isinstance(runs, int) and runs > 0: runinfo["runs"] = runs
                    elif isinstance(runs, list) and len(runs) > 0: runinfo["runs"] = [int(r) for r in runs]
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
    'root': root,
    'paths': paths,
}

for key in ses_info:
    project_data[key] = ses_info[key]




# 저장 — 본문은 데이터셋 안 registry, Speech 쪽에는 그 폴더를 가리키는 redirect
registry = os.path.join(native_path(root), "registry", Project_name)
os.makedirs(registry, exist_ok=True)
with open(os.path.join(registry, "project_info.json"), "w", encoding="utf-8") as f:
    json.dump(project_data, f, indent=4)

os.makedirs(os.path.join(base_path, Project_name), exist_ok=True)
with open(os.path.join(base_path, Project_name, "project_info.json"), "w", encoding="utf-8") as f:
    json.dump({"redirect": to_windows_path(registry).replace("\\", "/")}, f, indent=4)

# %%
