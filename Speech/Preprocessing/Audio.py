import requests
import json
import glob
import numpy as np
import os
import re
import shlex
import sys
import warnings


def _persist_user_env(name, value, rc_file="~/.bashrc"):
    """ 환경변수 하나를 사용자 단위로 영구 등록한다.

        Windows: HKCU\\Environment 에 쓰고 WM_SETTINGCHANGE 를 알린다
                 (PowerShell 의 SetEnvironmentVariable(..., 'User') 와 같다).
        Linux/WSL/macOS: rc_file 에 `export NAME='value'` 한 줄을 둔다. 같은 이름의
                 export 줄이 이미 있으면 그 줄만 바꾼다.

        Args:
            name (str): 환경변수 이름
            value (str): 값
            rc_file (str): Linux 에서 쓸 셸 설정 파일 (default: ~/.bashrc)

        Returns:
            등록한 곳 (레지스트리 키 또는 rc 파일 경로)
    """
    if sys.platform == "win32":
        import winreg
        import ctypes
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, name, 0, winreg.REG_SZ, value)
        # 새로 여는 터미널·탐색기가 바뀐 값을 읽도록 알린다 (HWND_BROADCAST, WM_SETTINGCHANGE)
        ctypes.windll.user32.SendMessageTimeoutW(0xFFFF, 0x001A, 0, "Environment", 0x0002, 5000, None)
        return r"HKCU\Environment"

    rc_path = os.path.expanduser(rc_file)
    line = f"export {name}={shlex.quote(value)}\n"
    lines = []
    if os.path.exists(rc_path):
        with open(rc_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    pattern = re.compile(rf"^\s*export\s+{re.escape(name)}=")
    hits = [i for i, l in enumerate(lines) if pattern.match(l)]
    if hits:
        lines[hits[0]] = line
        lines = [l for i, l in enumerate(lines) if i not in hits[1:]]
    else:
        if lines and not lines[-1].endswith("\n"):
            lines[-1] += "\n"
        lines.append(line)
    with open(rc_path, "w", encoding="utf-8") as f:
        f.writelines(lines)
    return rc_path


def set_clova_credentials(invoke_url, secret, persist=False, rc_file="~/.bashrc"):
    """ Clova Speech 접속 정보를 등록한다.

        현재 파이썬 프로세스의 os.environ 에는 항상 넣으므로, 같은 세션 안의
        Clova_STT / Clova_confidence 는 인자 없이 바로 쓸 수 있다.
        persist=True 면 사용자 환경변수로도 영구 등록한다 (OS 별 방식은
        _persist_user_env 참고). 한 번만 실행하면 된다.

            >>> from Speech.Preprocessing import Audio
            >>> Audio.set_clova_credentials("<URL>", "<KEY>", persist=True)

        Args:
            invoke_url (str): https://clovaspeech-gw.ncloud.com/external/v1/... 형태의 호출 URL
            secret (str): X-CLOVASPEECH-API-KEY 값
            persist (bool): 사용자 환경변수로 영구 등록 여부 (default: False)
            rc_file (str): Linux 에서 쓸 셸 설정 파일 (default: ~/.bashrc)
    """
    values = {"CLOVA_INVOKE_URL": invoke_url.rstrip("/"), "CLOVA_SECRET": secret}
    for name, value in values.items():
        os.environ[name] = value
    if persist:
        where = [_persist_user_env(name, value, rc_file=rc_file) for name, value in values.items()][0]
        print(f"CLOVA_INVOKE_URL, CLOVA_SECRET 를 {where} 에 등록했습니다. "
              "다른 터미널·에디터는 새로 열어야 반영됩니다.")


def _clova_credentials(invoke_url=None, secret=None):
    """ Clova Speech 접속 정보를 정한다.

        우선순위: 인자로 받은 값 → 환경변수 (CLOVA_INVOKE_URL, CLOVA_SECRET).
        코드에 키를 적어 두지 않기 위한 것이다. 환경변수에 한 번 등록해 두면
        이후로는 아무것도 넘길 필요가 없고, 등록 없이 그때그때 쓰려면
        Clova_STT(..., invoke_url=, secret=) 로 넘긴다.

            CLOVA_INVOKE_URL : https://clovaspeech-gw.ncloud.com/external/v1/... 형태의 호출 URL
            CLOVA_SECRET     : X-CLOVASPEECH-API-KEY 값

        등록하는 법 (OS 무관, 한 번만 실행):
            Audio.set_clova_credentials("<URL>", "<KEY>", persist=True)
            → Windows 는 사용자 환경변수, Linux/WSL 은 ~/.bashrc 에 export 줄.

        직접 등록해도 된다.
            Windows (PowerShell):
                [Environment]::SetEnvironmentVariable('CLOVA_INVOKE_URL','<URL>','User')
                [Environment]::SetEnvironmentVariable('CLOVA_SECRET','<KEY>','User')
            Linux (~/.bashrc 등):
                export CLOVA_INVOKE_URL='<URL>'
                export CLOVA_SECRET='<KEY>'
            WSL 에서 Windows 값을 그대로 쓰려면 Windows 사용자 환경변수 WSLENV 에
            'CLOVA_INVOKE_URL/u:CLOVA_SECRET/u' 를 추가한다.

        Args:
            invoke_url (str, optional): 호출 URL. None 이면 환경변수
            secret (str, optional): API 키. None 이면 환경변수

        Returns:
            (invoke_url, secret) 튜플
    """

    invoke_url = invoke_url or os.environ.get("CLOVA_INVOKE_URL")
    secret = secret or os.environ.get("CLOVA_SECRET")

    missing = [name for name, value in
               [("CLOVA_INVOKE_URL", invoke_url), ("CLOVA_SECRET", secret)]
               if not value]
    if missing:
        raise RuntimeError(
            "Clova 접속 정보가 없습니다: " + ", ".join(missing) + "\n"
            "인자(invoke_url=, secret=)로 넘기거나, "
            "Audio.set_clova_credentials(url, secret, persist=True) 로 한 번 등록하세요.\n"
            "이미 등록했다면 VS Code나 터미널을 껐다 켜야 (Linux 는 source ~/.bashrc) "
            "새 환경변수가 반영됩니다."
        )

    return invoke_url.rstrip("/"), secret


# STT
def Clova_STT(file_path, lang="ko-KR", output="", save_STT=False, save_confidence=False, save_csv=False, save_speaker=False, showresults=False,
              invoke_url=None, secret=None):
    """ 오디오 파일의 받아쓰기 결과(_STT.txt) & 단어 정렬 결과(_FA.txt) 저장

        Args:
            file_path (str): 오디오 파일 경로
            lang (str): 받아쓸 언어 (default: ko-KR)
            output (str): STT, FA결과 저장할 경로 (default: 오디오 파일 위치)
            save_STT: STT결과 저장 여부 (default: False)
            save_csv: FA결과 csv파일로 저장 여부 (default: False, txt파일로 저장)
            save_confidence: confidence 저장 여부 (default: False)
            showresults: 결과 출력 여부 (default: False)
            invoke_url, secret: Clova 접속 정보 (default: None → 환경변수, _clova_credentials 참고)
    """

    invoke_url, secret = _clova_credentials(invoke_url, secret)
    request_body = {
        'language': lang,
        'completion': 'sync',
        'callback': None,
        'userdata': None,
        'wordAlignment': True,
        'fullText': True,
        'forbiddens': None,
        'boostings': None,
        'diarization': None,
    }
    headers = {
        'Accept': 'application/json;UTF-8',
        'X-CLOVASPEECH-API-KEY': secret
    }
    files = {
        'media': open(file_path, 'rb'),
        'params': (None, json.dumps(request_body, ensure_ascii=False).encode('UTF-8'), 'application/json')
    }
    response = requests.post(headers=headers, url=invoke_url + '/recognizer/upload', files=files)
    # 클로바 요청
    results = response.text

    #  STT와 FA결과
    results = json.loads(results)
    sentences = results['segments']
    
    if save_confidence:
        scores = []
        for line in sentences:
            scores.append(line['confidence'])
            
        
    full_text = results['text']
    if save_speaker:
        FA = sentences[0]['words']
        speaker_label = sentences[0]['speaker']['label']
        for n in range(len(FA)):
            FA[n] = [speaker_label] + FA[n]
        for i in range(1,len(sentences)):
            word_list = sentences[i]['words']
            speaker_label = sentences[i]['speaker']['label']
            for n in range(len(word_list)):
                word_list[n] = [speaker_label] + word_list[n] 
            FA = FA + word_list
    else:
        FA = sentences[0]['words']
        for i in range(1,len(sentences)):
            FA = FA + sentences[i]['words']
    # 결과 저장하기
    if len(output) == 0:
        if save_STT:
            f_stt = open(file_path.split(".")[0]+"_STT.txt", 'w', encoding="utf-8")
            f_stt.write(full_text)
            f_stt.close()
        if save_csv:
            f_csv = open(file_path.split(".")[0]+"_FA.csv", 'w', encoding="utf-8-sig")
            f_csv.write("start_time,end_time,word\n")
            for i in range(len(FA)):
                f_csv.write('{0},{1},{2}\n'.format(str(FA[i][0]), str(FA[i][1]), str(FA[i][2])))
            f_csv.close()
        if save_speaker:
            f_FA = open(file_path.split(".")[0]+"_FA.txt", 'w', encoding="utf-8")
            for i in range(len(FA)):
                f_FA.write('{0:<8}{1:<8}{2:<8}{3}\n'.format(FA[i][0], str(FA[i][1]), str(FA[i][2]), str(FA[i][3])))
            f_FA.close()
        else:
            f_FA = open(file_path.split(".")[0]+"_FA.txt", 'w', encoding="utf-8")
            for i in range(len(FA)):
                f_FA.write('{0:<8}{1:<8}{2}\n'.format(FA[i][0], str(FA[i][1]), str(FA[i][2])))
            f_FA.close()
        if save_confidence:
            f_confidence = open(file_path.split(".")[0]+"_confidence.txt", 'w', encoding="utf-8")
            for score in scores:
                f_confidence.write(str(score)+"\n")
            f_confidence.close()
    else:
        try:
            filename = os.path.basename(file_path).split(".")[0]
            if save_STT:
                f_stt = open(os.path.join(file_path, filename+"_STT.txt"), 'w', encoding="utf-8")
                f_stt.write(full_text)
                f_stt.close()
            if save_csv:
                f_csv = open(file_path.split(".")[0]+"_FA.csv", 'w', encoding="utf-8-sig")
                f_csv.write("start_time,end_time,word\n")
                for i in range(len(FA)):
                    f_csv.write('{0},{1},{2}\n'.format(str(FA[i][0]), str(FA[i][1]), str(FA[i][2])))
                f_csv.close()
            if save_speaker:
                f_FA = open(file_path.split(".")[0]+"_FA.txt", 'w', encoding="utf-8")
                for i in range(len(FA)):
                    f_FA.write('{0:<8}{1:<8}{2:<8}{3}\n'.format(FA[i][0], str(FA[i][1]), str(FA[i][2]), str(FA[i][3])))
                f_FA.close()
            else:
                f_FA = open(os.path.join(file_path, filename+"_FA.txt"), 'w', encoding="utf-8")
                for i in range(len(FA)):
                    f_FA.write('{0:<8}{1:<8}{2}\n'.format(FA[i][0], str(FA[i][1]), str(FA[i][2])))
                f_FA.close()
            if save_confidence:
                f_confidence = open(os.path.join(file_path, filename+"_confidence.txt"), 'w', encoding="utf-8")
                for score in scores:
                    f_confidence.write(str(score)+"\n")
                f_confidence.close()
        except:
            warnings.warn(f'Path "{output}" does not exist. Save at audio path "{os.path.dirname(file_path)}"')
            if save_STT:
                f_stt = open(file_path.split(".")[0]+"_STT.txt", 'w', encoding="utf-8")
                f_stt.write(full_text)
                f_stt.close()
            if save_csv:
                f_csv = open(file_path.split(".")[0]+"_FA.csv", 'w', encoding="utf-8-sig")
                f_csv.write("start_time,end_time,word\n")
                for i in range(len(FA)):
                    f_csv.write('{0},{1},{2}\n'.format(str(FA[i][0]), str(FA[i][1]), str(FA[i][2])))
                f_csv.close()
            else:
                f_FA = open(file_path.split(".")[0]+"_FA.txt", 'w', encoding="utf-8")
                for i in range(len(FA)):
                    f_FA.write('{0:<8}{1:<8}{2}\n'.format(FA[i][0], str(FA[i][1]), str(FA[i][2])))
                f_FA.close()          
            if save_confidence:
                f_confidence = open(file_path.split(".")[0]+"_confidence.txt", 'w', encoding="utf-8")
                for score in scores:
                    f_confidence.write(str(score)+"\n")
                f_confidence.close()  
    if showresults: return(results)

# second processing
def apply_FA(file_path):
    """ _FA_new.txt파일을 통해 _STT_new.txt를 생성
    
        Args: 
            file_path (str): _FA_new.txt 파일 경로
    """
    STT_new = []
    try: f_FA_new = open(file_path, 'r', encoding="utf-8")
    except: f_FA_new = open(file_path.replace(".wav", "_audio.wav"), 'r', encoding="utf-8")
    FA_new_lines = f_FA_new.readlines()
    for line in FA_new_lines:
        try:
            word = " ".join(line.split()[2:])
            STT_new.append(word)
        except:
            pass

    STT_new = " ".join(STT_new).split(". ")
    f_stt_new = open(file_path[:-11]+"_STT_new.txt", 'w', encoding="utf-8")
    for i in range(len(STT_new)):
        if i == len(STT_new)-1:
            f_stt_new.write(STT_new[i])
        else:
            f_stt_new.write(STT_new[i]+".\n")
    f_stt_new.close()


# audiostamp
def audiostamp(input, output_folder="./"):
    """ FA_new.txt를 통해 문장의 종결 지점 & topic boundary를 추가해야 할 더미 파일 저장

    Args:
        input (str): *_FA_new.txt
        output_folder (str, optional): 결과 파일 위치. Defaults to "./".
    """
    os.makedirs(output_folder, exist_ok=True)
    with open(input, 'r', encoding="utf-8") as f:
        text = f.readlines()
    # speech time
    timestamp = []
    for line in text:
        line = line.split()
        timestamp.append(line[:2])
    timestamp = np.array(timestamp, dtype=int)
    # sentence
    sentence = []
    for line in text:
        if line.strip()[-1] == "." or line.strip()[-1] == "?":
            sentence.append(line.split()[1])
    # save
    # sentence
    with open(os.path.join(output_folder, filename+"_sentence.txt"), 'w', encoding="utf-8") as f:
        for time in sentence:
            f.write(time)
            if not time == sentence[-1]: f.write("\n")
    # save
    # dummy: topic
    with open(os.path.join(output_folder, filename+"_event.txt"), 'w', encoding="utf-8") as f:
        f.write("[1]\n\n[2]\n")
        
        

def Clova_confidence(file_path, lang="ko-KR", invoke_url=None, secret=None):
    """ Clova STT의 confidence를 출력
        Args:
            file_path (str): 오디오 파일 경로
            invoke_url, secret: Clova 접속 정보 (default: None → 환경변수, _clova_credentials 참고)
    """

    invoke_url, secret = _clova_credentials(invoke_url, secret)
    request_body = {
        'language': lang,
        'completion': 'sync',
        'callback': None,
        'userdata': None,
        'wordAlignment': True,
        'fullText': True,
        'forbiddens': None,
        'boostings': None,
        'diarization': None,
    }
    headers = {
        'Accept': 'application/json;UTF-8',
        'X-CLOVASPEECH-API-KEY': secret
    }
    files = {
        'media': open(file_path, 'rb'),
        'params': (None, json.dumps(request_body, ensure_ascii=False).encode('UTF-8'), 'application/json')
    }
    response = requests.post(headers=headers, url=invoke_url + '/recognizer/upload', files=files)
    # 클로바 요청
    results = response.text
        
    #  STT와 FA결과
    results = json.loads(results)
    results = results["segments"]
    scores = []
    for line in results:
        scores.append(line['confidence'])
    
    return(np.array(scores))
