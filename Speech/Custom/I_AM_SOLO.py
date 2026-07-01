# %%
# custom functions for speech_3T project
import numpy as np
import pandas as pd
import os
from Speech.load_project_info import get_brain_path, get_audio_path

def get_voxel_size_from_epi(epi):
    if epi.shape[0]<70: return "3.0"
    else: return "1.5"
    



def load_run_sequence(p1, p2):
    runnames = ["INTRO_run-1", "INTRO_run-2"]
    if p1[1] == "1":
        man = p1[0]
        woman = p2[0]
    elif p1[1] == "2":
        man = p2[0]
        woman = p1[0]  
    mapping = {'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4, 'F': 5}
    basepath = get_brain_path("I_AM_SOLO", derivatives=False)
    basepath = os.path.join(os.path.dirname(basepath), "Project_info")
    samediff = np.array(pd.read_excel(os.path.join(basepath, "SameDiff_order.xlsx")))
    samediff = (samediff[:,1:]).astype(int)
    samediff_order = samediff[mapping[man],mapping[woman]]
    if samediff_order == 1:
        runnames += ["SAME_run-1", "DIFF_run-1"]
    elif samediff_order == 2:
        runnames += ["DIFF_run-1", "SAME_run-1"]

    whois = np.array(pd.read_excel(os.path.join(basepath, "WhoIs_order.xlsx")))
    whois = (whois[:,1:]).astype(int)
    whois_order = whois[mapping[man],mapping[woman]]
    if whois_order == 1:
        runnames += ["HE_run-1", "SHE_run-1"]
    elif whois_order == 2:
        runnames += ["SHE_run-1", "HE_run-1"]
    return runnames


def get_likeability(sub, ses, run, counterpart=True):
    runlist = load_run_sequence(sub, ses)
    idx = runlist.index(run)+2
    basepath = get_audio_path("I_AM_SOLO", derivatives=False)
    filepath = os.path.join(basepath, f"sub-{sub}", f"ses-{ses}",
                            f"sub-{sub}_ses-{ses}_task-RATING_run-{idx}_impression.csv")
    ratings = pd.read_csv(filepath, index_col=0)
    likeability = np.array(ratings)[-2:,:]
    if counterpart: label = "OTHERTOSELF"
    else: label = "SELFTOOTHER"
    
    if label in likeability[0]: return int(likeability[0,-2])
    else: return int(likeability[1,-2])



def load_roi_info(name):
    roi_list={
        "PCN": ["Schaefer2018_400Parcels_17Networks", [1144,1145,1146,1147,1148,2151,2152,2153,2154,2155,2156,2157]],
        "rIPS": ["Schaefer2018_400Parcels_17Networks", [2125,2126,2127,2128,2104]],
        "PMC-core": ["Schaefer2018_400Parcels_17Networks", list(np.arange(1154,1161))+
                     list(np.arange(2163,2168))],
        "PCun": ["Schaefer2018_400Parcels_17Networks", list(np.arange(1154,1161))+list(np.arange(2163,2168))],
        "A1": ["Schaefer2018_400Parcels_17Networks", [1044,1045,2044,2045]],
        "AG": ["Schaefer2018_400Parcels_17Networks", [1149,1150,2159,2160]],
        "IPS": ["Schaefer2018_400Parcels_17Networks", [1122,1123,1124,1125,1126,2125,2126,2127,2128]],
        "Mot": ["Schaefer2018_400Parcels_17Networks", [1055,1056,1057,1058,1059,2056,2057,2058]],
        
    }
    
    return(roi_list[name])
    
    
def load_individual_roi_mask(sub, roi_name, vox):
    import nibabel as nib
    atlas_name, roi_ids = load_roi_info(roi_name)
    roi_path = os.path.join(get_brain_path("I_AM_SOLO"), f"sub-{sub}", "Atlas")
    roi_name = f"sub-{sub}_desc-{atlas_name}_{float(vox):.1f}mm.nii.gz"
    atlas = np.array(nib.load(os.path.join(roi_path, roi_name)).get_fdata(),int)
    mask = np.zeros_like(atlas)
    for i in roi_ids: mask = np.logical_or(mask, atlas==i)
    return(mask.astype(bool))
    

def load_individual_atlas(sub ,vox, atlas_name="Schaefer2018_400Parcels_17Networks"):
    import nibabel as nib
    roi_path = os.path.join(get_brain_path("I_AM_SOLO"), f"sub-{sub}", "Atlas")
    roi_name = f"sub-{sub}_desc-{atlas_name}_{float(vox):.1f}mm.nii.gz"
    atlas = np.array(nib.load(os.path.join(roi_path, roi_name)).get_fdata(),int)
    return(atlas)

def load_colors(name, scale=1, alpha=None):
    color_list={
        "PCN": [159,176,208],
        "IPS": [233,168,31],
        "rIPS": [233,168,31],
        "rIPL": [233,168,31],
        "PCun": [252,243,50],
        "PMC-core": [252,243,50],
        "HPC": [171,0,237],
        "ev1": [255,65,74],
        "ev": [255,65,74],
        "topic": [255,65,74]
        
    }
    
    color = color_list[name]

    if alpha:
        color.append(alpha)
        
    color = np.array(color)
    color = color*(scale/255)

    if scale==255: color = color.astype(int)

    return color
    
    
    
def set_matplotlib():
    import matplotlib as mpl
    import matplotlib.font_manager as fm

    from Speech.tools import isWSL
    if isWSL():
        fname = '/mnt/c//Users/Kwon/AppData/Local/Microsoft/Windows/Fonts/Helvetica.ttf'
    else:
        fname = 'C:/Users/Kwon/AppData/Local/Microsoft/Windows/Fonts/Helvetica.ttf'

    fe = fm.FontEntry(
        fname=fname,
        name="Helvetica")
    fm.fontManager.ttflist.insert(0, fe) # or append is fine
    mpl.rcParams['font.family'] = fe.name
    mpl.rc('font', family = 'Helvetica', size = 10)
    mpl.rc('savefig', transparent = True)
    spines = {"top": False, "right": False}
    mpl.rc('axes.spines', **spines)


def load_topic_transition(sub, ses, runname):
    basepath = get_audio_path("I_AM_SOLO", derivatives=False)
    basepath = os.path.join(basepath, "concat_timestamp", "Topic_transition")
    if sub[-1] == "1": group = f"{sub}{ses}"
    else: group = f"{ses}{sub}"
    filepath = os.path.join(basepath, f"{group}_task-{runname}.txt")

    topics = []
    with open(filepath, 'r') as f:
        while True:
            line = f.readline()
            if line.strip() == '':  break
            topics.append(line.split("\t"))
    return np.array(topics)



def load_final_likeability(sub, partner=None):
    final_partners = {
        "A1": "B2",
        "B1": "F2",
        "C1": "C2",
        "D1": "D2",
        "E1": "C2",
        "F1": "A2",
        "A2": "F1",
        "B2": "A1",
        "C2": "C1",
        "D2": "D1",
        "E2": "C1",
        "F2": "B1",   
    }

    ses = final_partners[sub]
    basepath = get_audio_path("I_AM_SOLO", derivatives=False)
    file = os.path.join(basepath, f"sub-{sub}", f"ses-{ses}", 
                        f"sub-{sub}_ses-{ses}_task-RANKING_run-1_impression.csv")
    data = pd.read_csv(file)
    rating = np.array([data["Char1"], data["Rating"]])
    rating = rating[:,rating[0,:]!=7]
    rating = rating[1,rating[0,:].argsort()]
    
    if partner:
        label = np.array(["A", "B", "C", "D", "E", "F"])
        return(rating[label==partner[0]][0])
    else: return rating
    
# %%
