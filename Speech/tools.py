import os
import sys
import numpy as np
import subprocess


def isWSL():
    """ POSIX(WSL·Linux) 환경인지 확인

        이름은 WSL이지만 실제로 구분하는 것은 "Windows가 아닌가"이다.
        호출부는 모두 이 의미로 쓴다 — bids_path와 bids_path_window 중 고르기,
        경로 구분자, pycortex import 여부, 서버 전용 명령 차단 등.

    Returns:
        bool: Windows면 False, 그 외(WSL·Linux·macOS)면 True
    """

    return sys.platform != "win32"


def isRealWSL():
    """ 순수 Linux가 아니라 진짜 WSL 위인지 확인

        isWSL()은 Windows인지만 가른다. WSL과 네이티브 Linux를
        구별해야 할 때만 이 함수를 쓴다.

    Returns:
        bool
    """

    if sys.platform != "linux":
        return False
    if os.environ.get("WSL_DISTRO_NAME"):
        return True
    try:
        with open("/proc/version", "r") as f:
            return "microsoft" in f.read().lower()
    except OSError:
        return False
    

def get_path_from_bashrc():
    try:
        result = subprocess.run(
            ['bash', '--login', '-c', 'echo $PATH'], 
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except Exception as e:
        print(f"Fail to load PATH: {e}")
        return None

def apply_bashrc():
    """ WSL환경에서 bashrc를 적용하여 PATH를 설정

    Returns: 
    """
    
    bashrc_path = get_path_from_bashrc()
    if bashrc_path:
        os.environ['PATH'] = bashrc_path
        print(f"Updated, ex) {os.environ['PATH'][:100]}...")
    else:
        print("Failed to load PATH from bashrc.")


def to_rgb_01(color_input):
    """
    다양한 색상 입력을 0~1 범위의 RGB 튜플로 변환.

    Args:
        color_input (str, tuple, list): 
            - 16진수 코드 (예: "#FF0000", "#f00")
            - 0-255 범위 RGB (예: (255, 0, 0))
            - 0-1 범위 RGB (예: (1.0, 0, 0))

    Returns:
        tuple: 0~1 범위의 RGB 튜플 (예: (1.0, 0.0, 0.0))
    """
    
    # 1. 입력이 16진수 문자열(str)인 경우
    if isinstance(color_input, str):
        hex_code = color_input.lstrip('#')
        
        # 3자리 hex 코드(#f00)를 6자리(#ff0000)로 변환
        if len(hex_code) == 3:
            hex_code = "".join([c*2 for c in hex_code])
            
        if len(hex_code) != 6:
            raise ValueError(f"'{color_input}'는 유효한 16진수 색상 코드가 아닙니다.")
            
        # 16진수를 10진수(0-255)로 변환
        r = int(hex_code[0:2], 16)
        g = int(hex_code[2:4], 16)
        b = int(hex_code[4:6], 16)
        
        # 0-255 범위를 0-1 범위로 변환하여 반환
        return (r / 255.0, g / 255.0, b / 255.0)

    # 2. 입력이 튜플(tuple) 또는 리스트(list)인 경우
    elif isinstance(color_input, (tuple, list)):
        if len(color_input) != 3:
            raise ValueError("RGB 튜플/리스트는 3개의 요소를 가져야 합니다.")
            
        # 2a. 0-255 범위인지 확인 (요소 중 1보다 큰 값이 있으면)
        if any(c > 1 for c in color_input):
            # 0-255 범위를 0-1 범위로 변환
            return (color_input[0] / 255.0, 
                    color_input[1] / 255.0, 
                    color_input[2] / 255.0)
        
        # 2b. 0-1 범위인 경우 (모든 요소가 1 이하)
        else:
            # 튜플로 변환하여 그대로 반환
            return tuple(color_input)
            
    # 3. 지원하지 않는 타입인 경우
    else:
        raise TypeError(f"지원하지 않는 입력 타입입니다: {type(color_input)}")
    
    