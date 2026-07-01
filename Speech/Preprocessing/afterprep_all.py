# %%
import argparse
from Speech.Preprocessing import EPI
from Speech import load_project_info

parser = argparse.ArgumentParser(description='Preprocessing, after fMRIprep')
parser.add_argument('project', help='project name')
parser.add_argument('sub', help='bids subject name')
parser.add_argument('--ses', help='session number', action="store") 
parser.add_argument('--threshold', help='FD movement threshold', action="store")
parser.add_argument("--tsnr", help='Save tSNR', action="store")
parser.add_argument('--rm', help='Delete intermediate files', action="store")
parser.add_argument('--gs', help='Denoise global signal', action="store")
parser.add_argument('--epi_space', help='EPI space', action="store")


args = parser.parse_args()
Project = str(args.project)
sub = args.sub
try:
    if len(str(args.ses).strip()) > 0: 
        ses = str(args.ses)
        if ses == "None": ses=None
    else:
        ses = None
except:
    ses = None


try:
    if float(args.threshold) > 0: 
        threshold = float(args.threshold)
    else:
        threshold = 0.05
except:
    threshold = 0.05

try:
    if len(str(args.tsnr)) > 0: 
        text = str(args.tsnr)
        if text == "True": tsnr = True
        elif text == "true": tsnr = True
        elif text == "False": tsnr = False
        elif text == "false": tsnr = False
        else: tsnr = False
    else:
        tsnr = False
except:
    tsnr = False
    
try:
    if len(str(args.rm)) > 0: 
        text = str(args.rm)
        if text == "True": rm = True
        elif text == "true": rm = True
        elif text == "False": rm = False
        elif text == "false": rm = False
        else: rm = True
    else:
        rm = True
except:
    rm = True

try:
    if len(str(args.gs)) > 0: 
        text = str(args.gs)
        if text == "True": gs = True
        elif text == "true": gs = True
        elif text == "False": gs = False
        elif text == "false": gs = False
        else: gs = True
    else:
        gs = True
except:
    gs = True
    
try:
    if len(str(args.epi_space)) > 0: 
        text = str(args.epi_space)
        if text == "MNI": epi_space = "MNI152NLin2009cAsym"
        elif text == "mni": epi_space = "MNI152NLin2009cAsym"
        elif text == "MNI152NLin2009cAsym": epi_space = "MNI152NLin2009cAsym"
        elif text == "T1": epi_space = "T1w"
        elif text == "t1": epi_space = "T1w"
        elif text == "T1w": epi_space = "T1w"
        else: epi_space = "MNI152NLin2009cAsym"
    else:
        epi_space = "MNI152NLin2009cAsym"
except:
    epi_space = "MNI152NLin2009cAsym"
    
    
    
# motion plot 저장
EPI.save_motion(Project, sub, ses, threshold=threshold)
if tsnr: EPI.save_tsnr(Project, sub, ses)

# 미리 run name들 불러오기
runs = load_project_info.get_run_names(Project, ses)
for name in runs:

    EPI.DN(Project, sub, name, ses, epi_space=epi_space, global_signal=gs)
    EPI.sc_dt_hp_sm(Project, sub, name, ses, epi_space=epi_space)
    if rm: EPI.delete_intermediate_files(Project, sub, name, ses, epi_space=epi_space)
    

# %%
