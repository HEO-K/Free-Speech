# %%
import argparse
from Speech.Preprocessing import EPI
from Speech import load_project_info

parser = argparse.ArgumentParser(description='Preprocessing, after fMRIprep')
parser.add_argument('project', help='project name')
parser.add_argument('sub', help='bids subject name')
parser.add_argument('--ses', help='session number', action="store") 


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



# motion plot 저장
EPI.save_motion(Project, sub, ses)

# 미리 run name들 불러오기
runs = load_project_info.get_run_names(Project, ses)
for name in runs:
    try:
        EPI.DN(Project, sub, name, ses)
        EPI.sc_dt_hp_sm(Project, sub, name, ses)
    except:
        print(name+" isn't exist")

# %%
