# Speech
Free-Speech 실험의 python 모듈\
프로젝트 등록(`_data_Project`) → 전처리(`Preprocessing`) → 분석 도구(`tools_*`) 순으로 쓴다.\
리눅스(WSL)와 윈도우 양쪽에서 돌지만, AFNI·pycortex가 필요한 단계는 리눅스 전용이다.
<br/>
<br/>

## 목차
0. [전체 구성](#0-전체-구성)
1. [설치 및 설정](#1-설치-및-설정)
2. [프로젝트 등록](#2-프로젝트-등록)
3. [모듈 안내](#3-모듈-안내)
4. [Preprocessing 파이프라인](#4-preprocessing-파이프라인)
5. [데이터 규약](#5-데이터-규약)
6. [주의사항](#6-주의사항)
<br/>
<br/>
<br/>

## 0. 전체 구성
- [`load_project_info.py`](load_project_info.py): 프로젝트 레지스트리 읽기 — 경로·run·피험자 목록은 전부 여기서
- [`make_project_info.py`](make_project_info.py): 새 프로젝트의 `project_info.json` 을 대화형으로 생성
- [`tools.py`](tools.py): OS 판별(`isWSL`), 색 변환 등 공용 유틸
- [`tools_EPI.py`](tools_EPI.py): EPI 로딩 · atlas · parcel 평균 · ROI mask
- [`tools_Text.py`](tools_Text.py): 강제정렬(FA) · 문장 · 경계 · NSP · 문장 임베딩 로더
- [`tools_Analysis.py`](tools_Analysis.py): HRF · GLM · 리샘플링 · permutation p 값 · 교차상관
- [`tools_NLP.py`](tools_NLP.py): ETRI 형태소·의존구문 · BERT NSP · sentence-transformers 임베딩
- [`tools_Plot.py`](tools_Plot.py): matplotlib 세팅 · surface plot · 별표 · 상관행렬
- [`tools_Surface.py`](tools_Surface.py): 윈도우 용 surface 렌더링 백엔드(surfplot) — `tools_Plot` 이 자동 분기
- [`Preprocessing/`](Preprocessing): `EPI.py`(dcm2bids · 디노이징 · AFNI 후처리), `Audio.py`(Clova STT · 강제정렬), 진입점 `dcm2bids_all.py` · `afterprep_all.py`
- [`Custom/`](Custom): 프로젝트별 편의 함수 — `NatPAC_speech.py` `speech_3T.py` `I_AM_SOLO.py` `MonkeyKingdom_Monkey.py`
- [`_data_Project/`](_data_Project): 프로젝트 레지스트리 — `<Project>/project_info.json` + `good_sub.json`
- [`_data_Atlas/`](_data_Atlas): MNI · Schaefer2018 · Yeo2011 · Brainnetome · HarvardOxford · Tian2020 · NMT(원숭이) · MEBRAIN08
- [`_data_NLP/`](_data_NLP): `stopwords.txt` (`단어/품사`, 단어가 비면 품사 전체 제외)
- [`set_wsl.py`](set_wsl.py): WSL 에서 `.bashrc` 적용 (거의 안 씀)
<br/>
<br/>
<br/>

## 1. 설치 및 설정

__1) 모듈 경로__\
`from Speech import ...` 로 import 하므로 **`Speech` 폴더를 담고 있는 상위 폴더**를 `.pth` 로 `site-packages` 에 올린다.
```
# {anaconda}/envs/{env}/Lib/site-packages/FS_general.pth  (윈도우)
# {anaconda}/envs/{env}/lib/python*/site-packages/FS_general.pth  (리눅스, WSL)
D:/Functions
```
스크립트 안에서 `sys.path` 를 건드리지 않는다. import 가 실패하면 대개 `.pth` 가 없는 환경(`base` 등)을 고른 것이다.

<br/>

__2) 환경변수 (자격증명)__\
키는 코드에 적지 않고 사용자 환경변수에서 읽는다. 
<br/>
윈도우는 아래 예시처럼 등록하고 `WSLENV` 에 `이름/u` 를 추가하면 WSL 에도 전달된다.
<br/>
리눅스의 경우 `~/.bashrc`를 활용하여 환경변수에 등록한다.

| 대상 | 환경변수 | 읽는 곳 |
| --- | --- | --- |
| Clova Speech STT | `CLOVA_INVOKE_URL`, `CLOVA_SECRET` | `Preprocessing/Audio.py` `_clova_credentials()` |
| ETRI OpenAPI | `ETRI_ACCESS_KEY` | `tools_NLP.py` `_etri_access_key()` |

```powershell
[Environment]::SetEnvironmentVariable('ETRI_ACCESS_KEY','<KEY>','User')
```

<br/>

__3) 외부 의존__

| 단계 | 필요한 것 |
| --- | --- |
| `Preprocessing/EPI.py` 후처리(`sc_dt_hp_sm`) | AFNI (`3dTstat` `3dcalc` `3dDetrend` `3dBandpass` `3dmerge`), **리눅스 전용** |
| `Preprocessing/EPI.py` `MP2RAGE` | FSL `bet` `fslmaths` + AFNI `3dSkullStrip`, 리눅스 전용 |
| `Preprocessing/EPI.py` dcm2bids | `dcm2bids` |
| `tools_NLP.get_NSP*` | tensorflow + transformers (`klue/bert-base`) |
| `tools_NLP.get_sentence_embedding` | sentence-transformers |
| `tools_Plot` surface | 리눅스: pycortex (DB `D:/Functions/pycortex/db`) / 윈동우: surfplot + 같은 DB 의 GIFTI |
| 그 외 | numpy · scipy · pandas · nibabel · nilearn · sklearn · matplotlib |

<br/>
<br/>
<br/>

## 2. 프로젝트 등록
**Project 는 폴더가 아니라 레지스트리 키다.** `_data_Project/<Project>/` 에 두 JSON 을 두면 모든 로더가 이름만으로 경로를 찾는다.

__프로젝트 기본 정보 `project_info.json`__ — 데이터 루트 + 세션별 run 목록
```json
{
    "Name": "NatPAC_speech",
    "bids_path": "/mnt/e/NatPAC/_DATA_fMRI",
    "bids_path_window": "E:/NatPAC/_DATA_fMRI",
    "audio_path": "/mnt/e/NatPAC/_DATA_Audio",
    "audio_path_window": "E:/NatPAC/_DATA_Audio",
    "ses-01": [
        {"name": "speechFREE", "type": "func", "runs": 1, "modality": "bold"}
    ]
}
```
- 세션이 없으면 `"info": [...]` 하나로 둔다 (`speech_3T` 가 그 예).
- `runs` 는 정수 n(→ `run-1 … run-n`) 또는 리스트 `[2]`(→ `run-2` 만). 없으면 run 라벨 없이 `name` 만 쓴다.
- `type` 은 `func` `anat` `fmap`, `modality` 는 dcm2bids 매칭용 (`bold` `T1w` `MP2RAGE` `phase` `magnitude` `epi`).
- 기본은 리눅스용 경로(`bids_path`)이지만, 윈도우 환경에서는 Windows 경로(`bids_path_window`)를 둘 다 적는다. `tools.isWSL()` 이 `sys.platform` 으로 고른다.

__`good_sub.json`__ — 분석 대상 피험자. `Preprocessing.EPI.save_motion` 이 FD>0.5 비율이 `threshold` 미만인 run 을 자동으로 추가한다.
```json
{"ses-01": {"speechFREE_run-1": ["003", "005"]}}
```

__프로젝트 만들기__\
[`make_project_info.py`](make_project_info.py) 의 상단 변수(`Project_name` `bids_path` …)를 고치고 실행하면 세션·run 을 물어보며 JSON 을 만든다. 직접 써도 된다.

__프로젝트 읽기__
```python
from Speech import load_project_info as lp
lp.get_good_sub("NatPAC_speech", ses="01", target_run="speechFREE_run-1")   # 피험자 번호 리스트
lp.get_run_names("NatPAC_speech", ses="02")                                 # ['REST_run-1', 'speechMOVIE_run-1']
lp.get_brain_path("NatPAC_speech")                                          # .../_DATA_fMRI/derivatives
lp.get_audio_path("NatPAC_speech", derivatives=False)                       # .../_DATA_Audio
```
<br/>
<br/>
<br/>

## 3. 모듈 안내
모듈이 어떤 기능을 하고, 어떤 함수들이 있는지 설명한다.<br/>
각 함수에 주석이 있으니 자세한 사용 방법은 주석을 참고하자.
<br/>
<br/>

### `tools_EPI` — EPI · atlas
fMRI 데이터를 numpy array로 다루기 위한 함수들이 있다.
```python
from Speech import tools_EPI
epi = tools_EPI.loader(Project, sub, "speechFREE_run-1", ses="01", confound_interp=False)   # (x,y,z,t) float16
ts  = tools_EPI.parcel_averaging("Schaefer2018_400Parcels_17Networks", epi, voxel="1.5")     # (parcel, t)
```

| 함수 | 하는 일 |
| --- | --- |
| `get_epipath(Project, sub, taskname, ses, smooth)` | 전처리 완료된 EPI 경로 불러오기|
| `loader(..., confound_interp, zscoring, smooth, dtype)` | z-score 한 (x,y,z,t) EPI 불러오기|
| `get_atlas(name, voxel)` | Atlas의 정보와 array를 불러오기|
| `get_MNI(voxel, option)` | MNI template 불러오기|
| `masking(epi, mask)` | EPI array를 MNI brain으로 masking |
| `parcel_averaging(parcel, epi, voxel)` | EPI를 parcel별로 평균|
| `get_parcel_roi_mask(parcel, roi, voxel)` | Parcel index로 ROI bool mask 만들기|
| `network_cluster(parcel, epi, averaging)` | Yeo 네트워크별 dictionary|
| `get_network_info(parcel)` | Schaefer atlas의 Yeo 네트워크 정보|
| `fill_parcel_value(parcel, value, roi)` | Parcel 값을 volume 에 채움, 나머지 NaN. |
| `data_to_MNI_nifti` / `data_to_MNI_nilearn` | Numpy array → Nifti1Image (MNI) |

Atlas 이름은 `_data_Atlas/` 의 폴더명 그대로 사용한다.<br/>
Atlas 불러오기 등 복셀 크기를 받아야 하는 경우, `voxel='3.0'`의 인자를 함수에 추가하면 된다. (없을 경우 `_data_Atlas/`에 직접 원하는 voxel size의 atlas를 만들어야 한다.) 

<br/>
<br/>

### `tools_Text` — 발화 텍스트 · 타임스탬프
Word timestamp등을 fMRI 분석에 적합하게 불러오고 변형하는 함수들이 있다.
| 함수 | 하는 일 |
| --- | --- |
| `load_FA(Project, sub, runname, ses)` | `[start, end, word]`를 반환|
| `get_sentence_FA(..., only_timestamp, tr)` | `[start, end, sentence]`를 반환 (문장 경계 = 단어가 `.` 또는 `?` 로 끝남)|
| `load_sentence` | 문장 문자열 리스트를 반환 |
| `get_phrase_FA` | 절 단위 `[start, end, phrase]` 를 반환 |
| `load_audio_boundary(..., boundary, tr)` | (개인 프로젝트용 함수) 저장된 boundary 반환 |
| `load_NSP` / `load_NSP_boundary` | next-sentence-prediction 점수 반환 |
| `load_PL` / `load_PL_boundary` | 문장 간 pause 길이 / pause 백분위 구간의 경계 TR |
| `load_embeddings` / `get_embedding_distance` | 문장 임베딩 `(n, dim)` (`*_embedding.npy` 캐시) / 인접 문장 cosine 거리 |
| `load_episode_score` `load_topic` | (개인 프로젝트용 함수) `*_episode.txt` `*_topic.txt` 읽기 |

fMRI 분석에 사용할 수 있도록 tr 단위로 묶는 기능도 존재. `tr=1600`와 같이 ms 단위를 입력받는다.
<br/>
<br/>

### `tools_Analysis` — 통계 및 분석
fMRI 분석이나 통계에 쓰는 함수들이 있다.
| 함수 | 하는 일 |
| --- | --- |
| `hrf_convolution(y, TR, sample, method)` | Timeseries에 HRF 적용 |
| `glm(input, X, apply_hrf, tr, intercept=True)` | GLM분석 `[condition, voxel]` beta|
| `resampling(x, y, x_new, method)` | 보간 리샘플링 |
| `empirical_p_value` / `p_from_dist` | permutation null 로 p 값 |
| `normalized_cross_correlation(x, y, maxlags)` | Cross correlation 계산 |
| `partial_correlation(X, a, b)` | Partial correlation 계산 |
| `spm_hrf` `glover_hrf` + derivative 들, `monkey_hrf` | HRF 커널  |



<br/>
<br/>

### `tools_NLP` — 한국어 NLP
한국어 전용 NLP 함수.
| 함수 | 하는 일 |
| --- | --- |
| `etri_spokentagger(text, wordlevel, stopwords)` | ETRI 구어 형태소 태깅 |
| `etri_dparse(text)` | ETRI 의존구문분석 |
| `load_stopword(input_list)` | `_data_NLP/stopwords.txt` + 추가 불용어 로딩 |
| `get_NSP(text, raw)` / `get_NSP_embedding` | klue/bert-base NSP 점수와 임베딩 호출 |
| `get_sentence_embedding(text, model_name)` | `paraphrase-multilingual-MiniLM-L12-v2` 임베딩 |

<br/>
<br/>

### `tools_Plot` · `tools_Surface` — 그림
여러 결과를 그리기 위한 함수. Brain surface plot을 그리기 위한 함수도 있다.
```python
from Speech import tools_Plot
tools_Plot.set_matplotlib()                         # Helvetica 10pt, top/right spine 제거, savefig 투명
fig = tools_Plot.plot_fsaverage_atlas("Schaefer2018_400Parcels_17Networks", {1: 0.3, 2: -0.1}, view="both", cmap="RdBu_r")
fig = tools_Plot.mni_surface_fsaverage_plot(volume, voxel="1.5", view="both", vmin=-1, vmax=1)
```

| 함수 | 하는 일 |
| --- | --- |
| `set_matplotlib()` | 필자가 선호하는 기본 세팅 |
| `plot_star(p, x, y, plot_dagger, ax)` | p 값을 `*` `**` `***` 로 플롯 |
| `timeseries_with_error(data, x, ...)` | 평균 ± 오차 timeseries를 플롯 |
| `plot_colorline(x, y, z, cmap)` | 궤적을 값에 따라 색칠 |
| `mni_surface_plot(vol, voxel, view)` / `mni_surface_fsaverage_plot` | MNI volume 을 mni152 / fsaverage 표면에 플롯 |
| `plot_fsaverage_atlas(atlas, {parcel: 값 or rgb}, view)` | parcel (Schaefer2018) 단위 값을 fsaverage에 플롯 |
| `plot_roi` `plot_mask` `plot_RGBA` | ROI · mask 등을 원하는 색으로 surface에 plot|
| `mni_surface_2dplot(v1, v2, cmap)` / `make_colormap` | 2D colormap 플롯 / colormap png 생성 (`pycortex/colormaps`) |
| `save_mni_img(vol, view, filename, path)` | surface 그림을 png 로 다운로드 |
| `medbrain_surface_plot` | MEBRAIN(원숭이) 표면 |

surface계열 플롯은 리눅스 환경에서는 pycortex 뷰어, 윈도우에서는 `tools_Surface`(surfplot)로 자동 분기해 matplotlib figure를 돌려준다.

<br/>
<br/>

### `Custom` — 프로젝트별 편의 함수
개인 편의용. 예시만 하나 둔다.
| 모듈 | 함수 |
| --- | --- |
| `NatPAC_speech` | `good_subs(taskname, exception)` → `[Project, sub, ses, task]` 리스트 출력

<br/>
<br/>
<br/>

## 4. Preprocessing 파이프라인
```
dcm2bids_all.py → fMRIPrep(외부) → afterprep_all.py
                                      save_motion → DN → sc_dt_hp_sm → 중간파일 삭제
Audio: Clova_STT → *_FA.txt → 사람이 수동 교정 → *_FA_new.txt → apply_FA → *_STT_new.txt
```

<br/>

__1) dcm2bids__ (`Preprocessing/dcm2bids_all.py`)
```bash
python Speech/Preprocessing/dcm2bids_all.py <Project> <dcm 폴더> <sub> [--ses 01]
```
`project_info.json` 의 run 이름으로 스캐너 프로토콜명을 매칭(`check_dcm`)해 임시 config 를 만들고(`save_config`) dcm2bids 를 돈다. 매칭 결과를 출력하니 빠진 run 이 없는지 확인한다.

<br/>

__2) fMRIPrep__ — 코드화 할 수 없어 직접 fMRIPrep을 돌려야 한다. `derivatives/sub-XXX.html` 을 확인한다.

<br/>

__3) 후처리__ (`Preprocessing/afterprep_all.py`, **리눅스 환경에서만 실행 가능**)
```bash
python /mnt/d/Functions/Speech/Preprocessing/afterprep_all.py NatPAC_speech 016 \
    --ses 01 --threshold 1 --tsnr False --gs True --rm True --epi_space MNI
```

| 인자 | 기본 | 뜻 |
| --- | --- | --- |
| `--ses` | None | 세션 번호 (`01`, 접미사 포함 `01R`) |
| `--threshold` | 0.05 | FD>0.5 인 TR 비율이 이 값 미만이면 `good_sub.json` 에 추가 |
| `--tsnr` | False | Yeo 7 네트워크별 tSNR 그림 저장 |
| `--gs` | True | global signal 을 confound 에 포함 |
| `--rm` | True | `_mean` `_sc` `_sc_dt` 중간파일 삭제 |
| `--epi_space` | MNI | `MNI`(MNI152NLin2009cAsym) 또는 `T1` |

단계별 산출물 (접미사 사슬이 처리 순서):

| 단계 | 함수 | 하는 일 | 산출 |
| --- | --- | --- | --- |
| motion | `save_motion` | FD 그림 + `*_desc-FDoutlier.txt`(FD>0.5) + `good_sub.json` 갱신 | `figures/sub-XXX_ses-YY_motion.png` |
| DN | `DN` | confound regression — FD · 6 motion + derivative · a_comp_cor 6 · (global signal) · Legendre 2차 | `desc-DN` |
| sc · dt · hp · sm | `sc_dt_hp_sm` | AFNI: 평균 100 스케일링 → 1차 detrend → 0.01 Hz 이상 통과 → smoothing (1.5 mm→FWHM 3, 3 mm→5) | `desc-DN_sc_dt_hp_sm` |

<br/>

__4) 오디오__ (`Preprocessing/Audio.py`)

| 함수 | 하는 일 |
| --- | --- |
| `Clova_STT(wav, save_STT, save_confidence, save_speaker)` | **유료** Clova Speech 호출 → `*_STT.txt` `*_FA.txt`(`onset_ms offset_ms 단어`) |
| `apply_FA(FA_new)` | 사람이 교정한 `*_FA_new.txt` → `*_STT_new.txt` |
| `Clova_confidence(wav)` | Clova의 정확도 저장 |

<br/>
<br/>
<br/>

## 5. 데이터 형식 규약
- **fMRI**: `<bids_path>/derivatives/sub-XXX/ses-YY/func/sub-XXX_ses-YY_task-<run>_space-MNI152NLin2009cAsym_desc-DN_sc_dt_hp_sm.nii.gz`. 직접 glob 하지 말고 `tools_EPI.loader` / `get_epipath`. `loader` 캐시는 같은 자리의 `*_raw.npy`(보간 없음) / `*_linear.npy`.
- **오디오 원본**: `<audio_path>/sub-XXX/ses-YY/` 의 wav.
- **오디오 산출물**: `<audio_path>/derivatives/sub-XXX/ses-YY/`. **라이브러리가 쓰는 기본 결과물은 `*_FA_new.txt`** 
- **시각 단위는 ms.** 로더의 `tr` 인자는 출력 단위(ms)라 `tr=1000` 이면 초, `tr=1600` 이면 7T TR, `tr=1` 이면 ms 그대로. `hrf_convolution` 의 `TR` 만 초.
- **atlas 파일명**: `_data_Atlas/<name>/<name>_<voxel>mm.nii(.gz)` + `<name>.txt`(`index name`). 새 해상도는 같은 규약으로 추가한다.
<br/>
<br/>
<br/>

## 6. 주의사항
- `Preprocessing.EPI`의 `DN` `sc_dt_hp_sm` `MP2RAGE` 는 윈도우에서 돌아가지 않으므로 `"Change to WSL"` 만 돌려주고 끝난다.
- `save_motion`은 `good_sub.json` 의 해당 세션·run 항목만 갱신하고 나머지는 보존한다. 깨진 프로젝트 JSON 은 덮어쓰지 않고 에러를 낸다.
- ETRI · Clova 키는 환경변수를 새로 등록한 뒤 터미널·VS Code 를 껐다 켜야 반영된다.
- `set_matplotlib()`의 Helvetica 는 하드코딩된 `C:/Users/Kwon/AppData/Local/Microsoft/Windows/Fonts/Helvetica.ttf` 경로가 박혀 있다. 다른 컴퓨터에서는 함수를 고친다.
- `tools_Surface`는 pycortex DB(`./pycortex/db`)의 `mni152_asym_09c` `fsaverage` `MEBRAIN` 표면을 읽는다. DB가 없으면 surface plot 이 안 된다.
<br/>
<br/>
<br/>
