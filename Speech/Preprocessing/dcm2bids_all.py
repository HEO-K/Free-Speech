# %%
import argparse
import os
import glob
import shutil
from Speech.Preprocessing import EPI
from Speech.load_project_info import get_brain_path


parser = argparse.ArgumentParser(description='dcm2bids all-in-one')
parser.add_argument('project', help='project name')
parser.add_argument("input_path", help="input(dcm) path")
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


[check_results, target_runs_data, target_path] = EPI.check_dcm(Project, input_path, ses)
EPI.save_config(check_results, target_runs_data, Project, sub, ses)
EPI.run_dcm2bids(Project, sub, target_path, ses)


#### MRIting
# remove 7T anat & replace 3T anat
if Project == "MRIting":
   
    if ses == "2":
        anat_path = os.path.join(get_brain_path("MRIting", derivatives=False), "sub-"+sub)
        ses2_anats = glob.glob(os.path.join(anat_path, "ses-2", "anat","*"))
        ses1_anats = glob.glob(os.path.join(anat_path, "ses-1", "anat","*"))
        
        if len(ses2_anats)<len(ses1_anats):
            for file in ses1_anats:
                try:
                    os.remove(file)
                except:
                    os.rmdir(file)
            for file in ses2_anats:
                shutil.move(file, file.replace("ses-2", "ses-1"))
            shutil.rmtree(os.path.join(anat_path, "ses-2", "anat"), ignore_errors=True)
        else:
            shutil.rmtree(os.path.join(anat_path, "ses-2", "anat"), ignore_errors=True)
            
        
# %%
