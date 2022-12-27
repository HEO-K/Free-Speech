# %%
from Speech.Preprocessing import Audio
import os
import shutil


audio_path = "speech_3T/_data_Audio"

tasks = ["speechFREE"] # 과제명
subs = "001"  # 피험자, 띄어쓰기 구분
subs = subs.split()

for sub in subs:
    outpath = os.path.join(audio_path, "derivatives", "sub-"+sub)
    try: os.mkdir(outpath)
    except: pass
    for task in tasks:
        filename = "sub-"+sub+"_task-"+task+".wav"
        audio = os.path.join(audio_path, "sub-"+sub, filename)
        Audio.Clova_STT(audio)
        
        input(filename[:-4]+"_FA.txt를 수정한 뒤, '_FA_new.txt' 라는 이름으로 저장한다. 끝났으면 엔터.")
        
        filename = "sub-"+sub+"_task-"+task+"_FA_new.txt"
        Audio.apply_FA(os.path.join(audio_path, "sub-"+sub, filename))
        
        Audio.audiostamp(os.path.join(audio_path, "sub-"+sub, filename), outpath)
        
        
        # copy
        shutil.copy(os.path.join(audio_path, "sub-"+sub, filename), 
                    os.path.join(outpath, filename))
        filename = "sub-"+sub+"_task-"+task+"_STT_new.txt"
        shutil.copy(os.path.join(audio_path, "sub-"+sub, filename), 
                    os.path.join(outpath, filename))


# %%
