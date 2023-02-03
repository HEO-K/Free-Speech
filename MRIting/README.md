# MRIting Preprocessing
(코드는 [`/Free-Speech/Speech/Preprocessing/EPI.py`](../Speech/Preprocessing/EPI.py) 참고)\

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

원하는 ima 데이터를 받고 압축을 푼 다음, [`preprocessing_allinone.sh`](./preprocessing_allinone.sh)의 dcm2bids단락을 실행한다. 단 3T와 7T인지 확인하고 맞는 단락을 실행해야 한다.

```bash
################# 3T dcm2bids #######################
mri=3T
project=MRIting
input=압축_푼_ima폴더
sub=0302
ses=2
script_path=/Free-Speech/Speech/Preprocessing
python ${script_path}/dcm2bids_all.py ${project} ${input} ${sub} --ses ${ses}


################# 7T dcm2bids #######################
# 돌리려면 matlab 필요
# /usr/local/MATLAB/R2021b/bin/activate_matlab.sh
mri=7T
project=MRIting
input=압축_푼_ima폴더
sub=0302
ses=1
script_path=/Free-Speech/Speech/Preprocessing
python ${script_path}/dcm2bids_all.py ${project} ${input} ${sub} --ses ${ses}
if [ $mri = 7T ]
then
    python /Free-Speech/MRIting/7T.py ${project} ${input} ${sub} --ses ${ses}
fi
```

<br/>
<br/>
<br/>

## 2. fMRIprep
[fMRIprep 도커](https://fmriprep.org/en/stable/installation.html)를 설치한 뒤,\
[`preprocessing_allinone.sh`](./preprocessing_allinone.sh)의 fMRIprep 단락을 실행한다.\

__단, 3T & 7T 모두 bids format 처리가 되어있어야 한다.__


```bash
################# fMRIprep #######################
subs="0302"
bids_path=/Free-Speech/MRIting/_DATA_fMRI  # 1에서 만든 bids path

for sub in $subs
do
fmriprep-docker ${bids_path} ${bids_path}/derivatives participant --participant-label ${sub}  --fs-license-file ~/freesurfer/license.txt --skip_bids_validation --ignore slicetiming
done
```

실행이 되지 않을 경우 `fmriprep-docker` 실행 변수를 자신의 컴퓨터 환경에 맞게 수정하자.
다음 단계로 넘어가기 전에 `speech_3T/_DATA_fMRI/derivatives/sub-.html`을 보고 prep이 잘 되었나 확인하자.
<br/>
<br/>
<br/>

## 3. 후처리
나머지 후처리는 `Free-Speech/speech_3T`와 동일