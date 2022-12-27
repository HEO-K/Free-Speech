# fMRI Preprocessing
[다음](https://n-kwon.notion.site/20221004-780d16024f3149ae91cdca3376a8ee63) session을 preprocessing 해보자. (TR=1s, 3×3×3mm^3^)





## 1. bids format 생성
먼저 CNIR 서버에서 다음 파일을 다운로드 하고 압축을 푼다.
`3TMRIdata/2022_10/HK_SPEECH_20221004KHY`\
`preprocessing_allinone.sh`의 dcm2bids 단락의 `input` 변수를 수정하자.
그리고 이 Free-Speech 폴더 위치에서 해당 단락을 실행.

```bash
input=압축 푼 폴더 경로
project=speech_3T
sub=001
script_path=Speech/Preprocessing

python ${script_path}/dcm2bids_all.py ${project} ${input} ${sub}
```

그러면 아래와 같이 bids format의 run이름 --> Raw 폴더의 매칭 결과를 출력하고 bids format을 만든다.
![Folder matching](./img/dcm2bids.png)




## 2. fMRIprep
[fMRIprep 도커](https://fmriprep.org/en/stable/installation.html)를 설치한 뒤,\
`preprocessing_allinone.sh`의 fMRIprep 단락을 Free-Speech 폴더 위치에서 실행

```bash
subs="001"
bids_path=speech_3T/_DATA_fMRI

for sub in $subs
do
fmriprep-docker ${bids_path} ${bids_path}/derivatives participant --participant-label ${sub}  --n_cpus 20 --fs-license-file ~/freesurfer/license.txt --skip_bids_validation
done
```

실행이 되지 않을 경우 `fmriprep-docker` 실행 변수를 자신의 컴퓨터 환경에 맞게 수정하자.
다음 단계로 넘어가기 전에 `speech_3T/_DATA_fMRI/derivatives/sub-001.html`을 보고 prep이 잘 되었나 확인하자.





## 3. 후처리
나머지 후처리를 진행한다. [AFNI](https://afni.nimh.nih.gov/)가 필요하다.
* Save motion plot & Updata good subject list
* Denosing (global signal, FD, 6 motion, 6 motion derivatives, 6 aCompCor)
* Scaling (mean=0)
* Detrending 
* Frequency filtering (bandpass: 0.01 ~ 99999 (Hz))
* Smoothing (2→3, 2.5→4, 3→5 (mm))
`preprocessing_allinone.sh`의 preprocess 단락을 Free-Speech 폴더 위치에서 실행

```bash
subs="001"
project=speech_3T
script_path=Speech/Preprocessing

for sub in $subs
do
python ${script_path}/afterprep_all.py ${project} ${sub}
done
```

실행 결과 아래와 같은 파일들이 생성\
![Results](./img/process_all.png)


모션 이미지는 `speech_3T/_DATA_fMRI/derivatives/sub-001/figures/sub-001_motion.png`로 저장된다.
![Motion](./img/sub-001_motion.png)





## 내 데이터에 적용해보기
내 환경에 맞추어 `Speech/_data_Project/`의 프로젝트 정보를 생성하면 된다.\
`Speech/make_project_info.py`를 통해 프로젝트 정보를 만들거나, 직접 프로젝트 폴더를 생성해서 `project_info.json`을 만들면 된다.


```python3
# %%
import numpy as np
import os
import json

# 정보 파일 저장 위치: _data_Project/Project_Name/에 저장됨
base_path = "D:/Functions/Speech/_data_Project"
#base_path = "/mnt/d/Functions/Speech/_data_Project"



#####################################################################################
# 프로젝트 이름 
Project_name = "Speech_3T"
os.makedirs(os.path.join(base_path,Project_name), exist_ok=True)
# bids path
bids_path = "/mnt/d/speech_3T/_DATA_fMRI"
# for WSL environment, ubuntu면 빈 문자열으로
bids_path_window = "D:/speech_3T/_DATA_fMRI" 
# session이 존재하면 그 개수를, 아니면 0
sessions = 0

audio_path = "/mnt/d/speech_3T/_DATA_Audio"
audio_path_window = "D:/speech_3T/_DATA_Audio"



#####################################################################################
# run 정보, 세션이 여러개라면 이중 리스트를 만들어야 한다. 하나면 단일 리스트 (ex: [[ses1],[se2]])
# task 이름은 bids format에서 task-XXX로 붙는 이름이다.
# fMRI protocol 이름은 위 task이름이 기준이다. task-speech_run-1(task name) --> SPEECH1(protocol name) 
# 위의 조건에 맞지 않을 경우 실행 안되므로 protocol이름을 수정하거나 아니면 코드를 수정한다.
run_name = ["REST", "speechFREE", "speechTOPIC", "listeningFREE", "listeningTOPIC", "T1"] # T1도 포함해야.

# 각 task마다 최대 run수 (T1포함-> T1은 0으로), bids의 run-XX이 안나오게 하길 원한다면 0으로,
# run-1이 무조건 붙어 있게 하고프면 1으로 하면 된다.
# session마다 만들어야 하며, 역시 여러 세션이면 이중 리스트, 아니면 단일 리스트로
run_numbers = [0,0,2,0,0,0]



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

```