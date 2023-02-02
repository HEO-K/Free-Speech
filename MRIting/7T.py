import argparse
from Speech.Preprocessing import EPI
from Speech import load_project_info


parser = argparse.ArgumentParser(description='SDC')
parser.add_argument('project', help='project name')
parser.add_argument("input_path", help="input(ima) path")
parser.add_argument('sub', help='bids subject name')
parser.add_argument('--ses', help='session number', action="store")


args = parser.parse_args()
Project = str(args.project)
sub = args.sub
input_path = args.input_path
try:
    if int(args.ses) > 0: 
        ses = str(args.ses)
    else:
        ses = None
except:
    ses = None


EPI.SDC(Project, input_path, sub, ses=ses, gre_name="*GRE*", replace=True)


# %% 
# MRIting 전용
# UNI 비우기
import os
import glob
import subprocess as sp
filepath = load_project_info.get_brain_path(Project, derivatives=False)
try:
    os.rmdir(os.path.join(filepath, "sub-"+sub, "ses-"+ses, "anat"))
except:
    print("No files")

# session 1에 T1이 있어야 한다.
if ses == "1":
    anat_7t = os.path.join(filepath, "sub-"+sub, "ses-"+ses, "anat")
    anat_3t = os.path.join(filepath, "sub-"+sub, "ses-2", "anat")
    sp.call(f"mv {anat_3t} {anat_7t}" ,shell=True)
    
    
# %%
