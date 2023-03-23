# Free-Speech
Speech 실험의 A-to-Z\
해당 repository는 WSL(Ubuntu-20.04) 환경에서 제작되었습니다. \
[WSL 설치](https://n-kwon.notion.site/Windows-Subsystem-for-Linux-abd46c09ce084bbea874fafc9a6cc99f)
<br/>
<br/>

## 목차
0. [전체 구성](#0-전체-구성)
1. [실험 코드](#1-실험-코드)
2. [Preprocessing (fMRI, Audio) 해보기](#2-preprocessing-fmri-audio-해보기)
3. [분석 코드](#3-분석-코드)
4. [MRIting](#4-mriting)
5. [NatPAC dcm2bids](#5-natpac-dcm2bids)
<br/>
<br/>
<br/>

## 0. 전체 구성 및 간단 사용법
- [`Analysis_Code`](Analysis_Code): 분석 코드
- [`Experiment_Code`](Experiment_Code): 실험 코드
- [`MRIting`](MRIting): MRIting 전용 전처리
- [`NatPAC`](NatPAC): NatPAC dcm2bids
- [`Speech`](Speech): python 모듈
- [`speech_3T`](speech_3T): preprocessing & speech_3T DATA
- [`Speech_linux.pth`](Speech_linux.pth): Speech python 모듈 경로 설정 파일 (Linux OS)
- [`Speech_window.pth`](Speech_window.pth): Speech python 모듈 경로 설정 파일 (Window OS)
<br/>

__사용법__
1. 이 github repository를 다운로드
2. Speech 모듈을 사용해야 하므로 `Speech_OS.pth`를 자신의 컴퓨터에 맞게 수정한다. ([`Speech_linux.pth`](Speech_linux.pth) 내용 참고)
3. `Speech/_data_Poject/자신의_프로젝트`의 project_info.json의 bids_path를 자신의 컴퓨터에 맞게 수정한다.\
    ex) `MRIting`의 preprocessing을 따라 하고 싶다면, [`Speech/_data_Project/MRIting/project_info.json`](Speech/_data_Project/MRIting/project_info.json)의 bids_path를 자신의 컴퓨터 상에서의 `repository_다운_경로/Free-Speech/MRIting/_DATA_fMRI`로 수정해야 한다.
<br/>
<br/>
<br/>

## 1. 실험 코드
[`Experiment_Code`](Experiment_Code)에 각 실험의 코드와 그 설명이 있습니다.
- [`MRIting`](Experiment_Code/MRIting): MRIting 실험 코드
- [`NatPAC`](Experiment_Code/NatPAC): 7T NatPAC Speech 실험 코드
- [`speech_3T`](Experiment_Code/speech_3T): 3T Free Speech 실험 코드
<br/>
<br/>
<br/>

## 2. Preprocessing (fMRI, Audio) 해보기
[`speech_3T`](speech_3T)의 `README.md`를 참고하자.
<br/>
<br/>
<br/>

## 3. 분석 코드
[`Analysis_Code`](Analysis_Code)에 각 실험의 코드 노트북이 있습니다.
- [`Keyword modeling`](Analysis_Code/Keyword_modeling.ipynb): 오디오 녹음으로부터 키워드 벡터 뽑아내기
- [`Topic boundary effect`](Analysis_Code/Topic_boundary_effect.ipynb): 주제 변환 시점의 boundary effect 확인하기
<br/>
<br/>
<br/>

## 4. MRIting
MRIting 전용 fMRI, audio preprocessing\
[`MRIting`](MRIting)의 `README.md`를 참고하자.
<br/>
<br/>
<br/>

## 5. NatPAC dcm2bids
NatPAC데이터를 bids format으로 변환\
[`NatPAC`](NatPAC)의 `README.md`를 참고하자.