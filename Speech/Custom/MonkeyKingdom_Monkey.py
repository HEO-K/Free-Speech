# %%
# custom functions for speech_3T project
import numpy as np
import os
import nibabel as nib

def load_average_epi(sub, clip):
    from Speech.load_project_info import get_brain_path
    basepath = get_brain_path("MonkeyKingdom_Monkey")
    sub_epi = os.path.join(basepath, f"sub-{sub}", "func", f"sub-{sub}_task-clip{clip}_sm_mean.npy")
    return(np.load(sub_epi))

def load_epi(sub, clip, run, smooth=True, dtype="float16"):
    from Speech.load_project_info import get_brain_path, cache_file_path
    from scipy.stats import zscore
    basepath = get_brain_path("MonkeyKingdom_Monkey")
    func = os.path.join(basepath, f"sub-{sub}", "func")
    stem = f"sub-{sub}_task-clip{clip}_run-{run}_sc_dt_hp" + ("_sm" if smooth else "")
    epipath = os.path.join(func, stem + ".nii.gz")
    # zscore 한 float16 캐시는 paths.cache 아래 (derivatives/cache/sub-*/func/)
    npypath = cache_file_path("MonkeyKingdom_Monkey", func, basepath, stem + ".npy")
    
    try:
        epi = np.load(npypath)
    except:
        epi = nib.load(epipath).get_fdata()
        # shape info
        fov = list(epi.shape[:-1])
        tr = epi.shape[-1]
        epi = epi.reshape(-1,tr)
        # zscore

        epi = zscore(epi, axis=1)
        epi = epi.astype(dtype)
        np.save(npypath, epi.reshape(fov+[tr]))
    
    return(epi)





# %%
