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

# motion plot 저장
EPI.save_motion(Project, sub, ses, threshold=threshold)
if tsnr: EPI.save_tsnr(Project, sub, ses)

# 미리 run name들 불러오기
runs = load_project_info.get_run_names(Project, ses)
for name in runs:

    EPI.DN(Project, sub, name, ses)
    EPI.sc_dt_hp_sm(Project, sub, name, ses)


# %%
