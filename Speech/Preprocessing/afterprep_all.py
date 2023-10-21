# %%
import argparse
from Speech.Preprocessing import EPI
from Speech import load_project_info

parser = argparse.ArgumentParser(description='Preprocessing, after fMRIprep')
parser.add_argument('project', help='project name')
parser.add_argument('sub', help='bids subject name')
parser.add_argument('--ses', help='session number', action="store") 
parser.add_argument('--threshold', help='FD movement threshold', action="store")


args = parser.parse_args()
Project = str(args.project)
sub = args.sub
try:
    if int(args.ses) > 0: 
        ses = str(args.ses)
    else:
        ses = None
except:
    ses = None

try:
    if int(args.threshold) > 0: 
        threshold = float(args.threshold)
    else:
        threshold = 0.05
except:
    threshold = 0.05

# motion plot 저장
EPI.save_motion(Project, sub, ses, threshold=threshold)
EPI.save_tsnr(Project, sub, ses)

# 미리 run name들 불러오기
runs = load_project_info.get_run_names(Project, ses)
for name in runs:
    try:
        EPI.DN(Project, sub, name, ses)
        EPI.sc_dt_hp_sm(Project, sub, name, ses)
    except:
        print(name+" isn't exist")

# %%
