import numpy as np
import os
import json
from .tools import isWSL, native_path, to_posix_path, to_windows_path


# project_info.json 은 두 스키마를 받는다.
#
# 구형: "bids_path" / "bids_path_window" / "audio_path" / "audio_path_window" 절대경로 네 개.
#       fMRIPrep 산출물은 bids_path/derivatives, 전사 산출물은 audio_path/derivatives 로 고정.
# 신형: "root" 하나(어느 OS 형식이든, native_path 로 변환) + "paths" 에 root 상대경로.
#       "paths" 키: rawdata(BIDS raw) · fmriprep(fMRIPrep + 후처리) · audio(원본 wav) ·
#       transcripts(FA_new 등 정본 전사) · cache(loader 의 .npy 캐시, 없으면 파일 옆에 둔다).
#       없는 키는 그 데이터가 로컬에 없다는 뜻이라 get_*_path 가 KeyError 를 낸다.
# 신형을 읽을 때 구형 네 키는 배치가 옛 규약(fmriprep = rawdata/derivatives 등)과 같을 때만 채운다.
# 경로는 info["bids_path"] 를 직접 읽지 말고 get_brain_path / get_audio_path / get_cache_path 로 얻는다.
#
# 레지스트리 위치: 기본은 Speech/_data_Project/<Project>/. 그 project_info.json 이
# {"redirect": "<폴더>"} 뿐이면 project_info.json 과 good_sub.json 을 그 폴더에서 읽는다
# (분석 대상 명세를 데이터셋 안에 두기 위한 것).
PATH_KEYS = ("rawdata", "fmriprep", "audio", "transcripts", "cache")


def get_project_dir(Project):
    """ project_info.json 과 good_sub.json 이 실제로 있는 폴더 (redirect 를 따라간 뒤)

    Args:
        Project (str): 프로젝트 이름

    Returns:
        str: 폴더 경로
    """

    base = os.path.join(os.path.dirname(__file__), "_data_Project", Project)
    json_path = os.path.join(base, "project_info.json")
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"Project '{Project}' isn't registered: {json_path}")
    with open(json_path, encoding="utf-8") as f:
        info = json.load(f)
    if "redirect" in info:
        target = native_path(info["redirect"])
        if not os.path.exists(os.path.join(target, "project_info.json")):
            raise FileNotFoundError(f"Project '{Project}' redirects to {target}, but project_info.json isn't there")
        return target
    return base


def _resolve_new_schema(info):
    """ 신형 스키마의 root/paths 를 절대경로로 풀고 구형 키를 채운다 (in place). """

    root = native_path(info["root"])
    info["root"] = root
    paths = info.setdefault("paths", {})
    unknown = set(paths) - set(PATH_KEYS)
    if unknown:
        raise KeyError(f"project_info.json 'paths' has unknown keys {sorted(unknown)} (allowed: {PATH_KEYS})")
    for key in list(paths):
        rel = str(paths[key]).replace("\\", "/")
        paths[key] = os.path.join(root, rel) if rel not in ("", ".") else root

    # 구형 키는 옛 규약(산출물 = 원본 폴더/derivatives)이 성립하는 배치에서만 채운다.
    # 성립하지 않으면 비워 둬서, 옛 코드가 틀린 폴더를 조용히 쓰는 대신 KeyError 로 멈춘다.
    bids = _legacy_root(paths.get("rawdata"), paths.get("fmriprep"))
    if bids is not None:
        info["bids_path"], info["bids_path_window"] = to_posix_path(bids), to_windows_path(bids)
    audio = _legacy_root(paths.get("audio"), paths.get("transcripts"))
    if audio is not None:
        info["audio_path"], info["audio_path_window"] = to_posix_path(audio), to_windows_path(audio)
    return info


def _legacy_root(raw, deriv):
    """ 구형 키(bids_path / audio_path)에 넣을 폴더. deriv 가 raw/derivatives 꼴이 아니면 None. """

    if deriv is None: return raw
    parent, name = os.path.split(deriv.rstrip("/\\"))
    if name != "derivatives": return None
    if raw is not None and os.path.normpath(raw) != os.path.normpath(parent): return None
    return parent


def get_full_info(Project):
    """ 저장되어 있는 프로젝트 정보 불러오기

    Args:
        Project (str): 프로젝트 이름

    Returns:
        dict: json형태의 정보. 신형 스키마면 root/paths 가 절대경로로 풀려 있다 (구형 키는 옛 배치일 때만)
    """

    base = get_project_dir(Project)
    with open(os.path.join(base, 'project_info.json'), encoding="utf-8") as f:
        info = json.load(f)
    if "root" in info:
        info = _resolve_new_schema(info)

    return info


def _get_path(Project, key, legacy_key, legacy_derivatives):
    """ 신형이면 paths[key], 구형이면 legacy_key (+ /derivatives) """

    info = get_full_info(Project)
    if "paths" in info:
        if key not in info["paths"]:
            raise KeyError(f"Project '{Project}' has no '{key}' path in project_info.json "
                           f"(has: {sorted(info['paths'])})")
        return info["paths"][key]
    path = info[legacy_key] if isWSL() else info[legacy_key + "_window"]
    if legacy_derivatives: path = os.path.join(path, "derivatives")
    return path



def run_numbers(run):
    """ project_info 항목의 'runs' 를 run 번호 리스트로 정규화

    'runs' 가 없으면 [] (run 라벨 없이 name 만 쓴다),
    정수 n 이면 [1, ..., n] (구형 표기),
    리스트면 그 번호 그대로 (예: [2] → run-2 만 존재).

    Args:
        run (dict): project_info.json 의 run 항목

    Returns:
        list[int]: run 번호
    """

    runs = run.get("runs")
    if runs is None: return []
    if isinstance(runs, int): return list(range(1, runs+1))
    return [int(r) for r in runs]


def expand_run_names(run_info, only_func=True, sep="_run-"):
    """ 세션의 run 항목 리스트 → run 이름 리스트

    Args:
        run_info (list[dict]): project_info.json 의 세션 항목 (예: info["ses-01"])
        only_func (bool, optional): func 만 남길지. Defaults to True.
        sep (str, optional): name 과 번호 사이 구분자. Defaults to "_run-".

    Returns:
        list[str]: 'name_run-N' (runs 없으면 'name')
    """

    runnames = []
    for run in run_info:
        if only_func and run.get("type") != "func": continue
        nums = run_numbers(run)
        if nums: runnames += [f"{run['name']}{sep}{i}" for i in nums]
        else: runnames.append(run["name"])
    return runnames


def get_run_names(Project, ses=None, only_func=True):
    """ Run 이름 생성기

    Args:
        Project (str): 프로젝트 이름
        ses (str, optional): 세션 번호, Defaults to None.
        only_func (bool, optional): func 만 남길지. Defaults to True.

    Returns:
        list: 모든 run 리스트
    """

    info = get_full_info(Project)
    if ses == None: run_info = info['info']
    else: run_info = info["ses-"+ses]

    return expand_run_names(run_info, only_func=only_func)


def get_good_sub(Project, ses=None, target_run=None):
    """ 모션 괜찮은 피험자들 번호 목록
    
    Args:
        Project (str): 프로젝트 이름
        ses (str, optional): 세션 번호, Defaults to None.
        target_run (str, optional): 특정 run만 출력할지, 아니면 모든 run 각각. Defaults to None.
        
    Returns:
        target_run 있을 경우: 피험자 번호 list
        traget_run 없을 경우: dict, key: run, value: 피험자 번호 list
    """
    
    with open(get_good_sub_path(Project), encoding='utf-8') as f:
        info = json.load(f)
    
    if ses == None:
        info = info["info"]
    else:
        info = info["ses-"+ses]
    
    if target_run == None:
        return(info)
    if target_run not in info:
        # 예전엔 print 만 하고 None 을 돌려줘 호출자가 for sub in None 으로 죽거나
        # bare except 로 삼켜 빈 목록이 됐다. 없는 run 은 KeyError 로 알린다.
        exist = ", ".join(f"'{name}'" for name in info.keys())
        raise KeyError(f"Run '{target_run}' isn't in good_sub.json of {Project}"
                       f"{'' if ses is None else ' ses-'+str(ses)}. (Exist runs: {exist})")
    return(info[target_run])
            


def get_good_sub_path(Project):
    """ good_sub.json 경로 (redirect 를 따라간 폴더 안) """

    return os.path.join(get_project_dir(Project), "good_sub.json")


def get_brain_path(Project, derivatives=True):
    """ nii 이미지 파일 저장 경로 불러오기

    Args:
        Project (str): 프로젝트 이름
        derivatives (bool, optional): True 면 fMRIPrep(+후처리) 폴더, False 면 BIDS raw. Defaults to True.

    Returns:
        path : Brain image data path
    """

    if derivatives: return _get_path(Project, "fmriprep", "bids_path", True)
    return _get_path(Project, "rawdata", "bids_path", False)


def get_audio_path(Project, derivatives=True):
    """ Audio 파일 저장 경로 불러오기

    Args:
        Project (str): 프로젝트 이름
        derivatives (bool, optional): True 면 전사 산출물(FA_new 등) 폴더, False 면 원본 wav 폴더. Defaults to True.

    Returns:
        path : Audio data path
    """

    if derivatives: return _get_path(Project, "transcripts", "audio_path", True)
    return _get_path(Project, "audio", "audio_path", False)


def get_cache_path(Project):
    """ loader 류가 만드는 .npy 캐시를 둘 폴더

        신형 스키마의 paths.cache. 없으면 None — 호출자는 지금처럼 원본 파일 옆에 둔다.

    Args:
        Project (str): 프로젝트 이름

    Returns:
        str or None
    """

    info = get_full_info(Project)
    return info.get("paths", {}).get("cache")


def cache_file_path(Project, source_path, base_path, filename):
    """ 캐시 파일의 실제 경로 — paths.cache 가 있으면 base_path 기준 상대 구조를 cache 아래에 그대로 만든다

    Args:
        Project (str): 프로젝트 이름
        source_path (str): 캐시의 원본이 있는 폴더 (예: .../derivatives/sub-001/func)
        base_path (str): 그 원본의 데이터 루트 (get_brain_path / get_audio_path 결과)
        filename (str): 캐시 파일명

    Returns:
        str: 캐시 경로. cache 폴더는 만들어 둔다
    """

    cache = get_cache_path(Project)
    if cache is None: return os.path.join(source_path, filename)
    rel = os.path.relpath(source_path, base_path)
    folder = os.path.join(cache, rel) if rel != "." else cache
    os.makedirs(folder, exist_ok=True)
    return os.path.join(folder, filename)


def get_epi_info(Project, task, ses=None):
    """ EPI 정보 불러오기

    Args:
        Project (str): 프로젝트 이름
        task (str): 과제 이름
        ses (str, optional): session

    Returns:
        dict : information dictionary
    """

    if "_run-" in task:
        task = task.split("_run-")[0]
    info = get_full_info(Project)
    if ses: 
        ses = str(ses)
        info = info[f"ses-{ses}"]
    else:
        info = info["info"]
    
    find = 0
    for runs in info:
        if runs["name"] == task:
            find = 1
            return runs
    if find == 0:
        raise KeyError(f"Cannot find {task}")
    