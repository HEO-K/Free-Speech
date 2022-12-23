import argparse
from Speech.Preprocessing import EPI
from Speech import load_project_info


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


check_results = EPI.check_dcm(Project, input_path, ses)
EPI.save_config(check_results, Project, sub, ses)
EPI.run_dcm2bids(Project, sub, input_path, ses)