# MRIting Preprocessing
(코드는 [`/Free-Speech/Speech/Preprocessing/EPI.py`](../Speech/Preprocessing/EPI.py) 참고)

3T와 다른 점
- 7T EPI SDC 
- Replace 7T anat to 3T anat
<br/>
<br/>
<br/>

## 1. bids 데이터 생성
[dcm2bids](https://unfmontreal.github.io/Dcm2Bids/)를 먼저 설치한다.

타겟하는 폴더 위치(여기선 `/Free-Speech/MRIting/_DATA_fMRI`)에서 아래 명령어를 실행하여 bids folder를 생성한다.
```bash
dcm2bids_scaffold
```


원하는 ima 데이터를 받고 압축을 푼 다음, [`preprocessing_allinone.sh`](./preprocessing_allinone.sh)의 dcm2bids단락을 실행한다. 단 3T와 7T인지 확인하고 맞는 단락을 실행해야 한다.\
예시 파일) sub-0302의 파일은 서버에서
- ses-1 (7T): `CNIR05/7TMRIdata/2023_01/20230131_JYS_MRITING`
- ses-2 (3T): `CNIR05/3TMRIdata/2023_02/20230201_JYS_MRITING`


```bash
################# dcm2bids #######################
# check sub & ima folder
sub=0502
ses1_input=/mnt/c/Users/Kwon/Downloads/20230314_MRITING_BKR_BKR/
ses2_input=/mnt/c/Users/Kwon/Downloads/20230315_MRITING_BKR_BKR/


# other param
project=MRIting
script_path=/mnt/d/Functions/Speech/Preprocessing


#### dcm2bids
# session 1
python ${script_path}/dcm2bids_all.py ${project} ${ses1_input} ${sub} --ses 1

# session 2
python ${script_path}/dcm2bids_all.py ${project} ${ses2_input} ${sub} --ses 2
```

<br/>
<br/>
<br/>

## 2. fMRIprep
[fMRIprep 도커](https://fmriprep.org/en/stable/installation.html)를 설치한 뒤,\
[`preprocessing_allinone.sh`](./preprocessing_allinone.sh)의 fMRIprep 단락을 실행한다.

__단, 3T & 7T 모두 bids format 처리가 되어있어야 한다.__


```bash
################# fMRIprep #######################
#### fmriprep
sub=0502
bids_path=/mnt/d/MRIting/_DATA_fMRI
fmriprep-docker ${bids_path} ${bids_path}/derivatives participant --participant-label ${sub}  --n_cpus 8 --fs-license-file ~/freesurfer/license.txt --skip_bids_validation
```

실행이 되지 않을 경우 `fmriprep-docker` 실행 변수를 자신의 컴퓨터 환경에 맞게 수정하자.
다음 단계로 넘어가기 전에 `/Free-Speech/MRIting/_DATA_fMRI/derivatives/sub-.html`을 보고 prep이 잘 되었나 확인하자.
<br/>
<br/>
<br/>

## 3. 후처리
나머지 후처리는 `Free-Speech/speech_3T`와 동일