# MRIting 실험 코드
## 실험 구성
MRIting은 이틀에 걸쳐 진행된다.
![`task`](./img/task_sturucture.png)

#### Day 1
1. Rating 1
2. Introduction 1
3. Rating 2
4. Introduction 2
5. Rating 3
6. Introduction 3
7. Rating 4
8. Chatting
9. Rating 5
10. Truthlie game
11. Rating 6
#### Day 2
1. Recall
2. Speech
3. Resting
4. Watching movie
<br/>
<br/>
<br/>

## 각 과제 설명
#### Rating ([`Ses1_RATING.m`](Ses1_RATING.m))
나와 상대의 인상 평가를 진행한다. Day 1 과제 사이사이에 진행한다.
![`rating`](./img/rating.png)
<br/>
<br/>

#### Introduction ([`Ses1_INTRO.m`](Ses1_INTRO.m))
10분 동안 자기 소개를 한다. 
- Introduction 1: 화면에 제시되는 주제, 혹은 자유 주제에 대해 본인을 소개한다.
- Introduction 2: 서로 같은 생각을 가진 찬반 주제에 대해 이야기한다.
- Introduction 3: 서로 상반된 생각을 가진 찬반 주제에 대해 이야기한다.
<br/>

#### Chatting ([`Ses1_CHATTING.m`](Ses1_CHATTING.m))
15분 동안 서로 자유롭게 대화한다. 화면에 제시된 주제에 대해 이야기하거나, 자유 주제에 대해 이야기한다.
<br/>
<br/>

#### Truthlie game ([`Ses1_TRUTHLIE.m`](Ses1_TRUTHLIE.m))
20분 동안 상대방에 대한 다섯개의 문장 중 2개의 거짓된 문장을 찾는다.
![`truthlie`](./img/truthlie.png)
<br/>
<br/>

#### Recall ([`Ses2_RECALL.m`](Ses2_RECALL.m))
어제 진행한 실험을 자세히 회상한다.
<br/>
<br/>

#### Speech ([`Ses2_SPEECH.m`](Ses2_SPEECH.m))
10분 동안 주제 없이 생각나는대로 이야기한다.
<br/>
<br/>

#### Resting ([`Ses2_RESTING.m`](Ses2_RESTING.m))
10분 동안 편안하게 쉰다.
<br/>
<br/>

#### Watching movie ([`Ses2_MOVIE.m`](Ses2_MOVIE.m))
영화를 감상한다.
<br/>
<br/>
<br/>


## 실험 진행 및 결과
각 실험의 스크립트를 실행한다.
<br/>
<br/>

결과는 `DATA` 폴더 내에 `sub-XXX/ses-XX` 폴더가 생성되어 그 안에 파일로 저장된다.\
각 Task마다
- `_timepoint.txt`: event 파일
- `XXX.wav`: 오디오 녹음 파일 (말하는 과제 전부)
가 생성되며, rating의 경우 각 질문에 대한 event 파일이 생성된다. (`_impression.csv`, `_impression.mat`)
