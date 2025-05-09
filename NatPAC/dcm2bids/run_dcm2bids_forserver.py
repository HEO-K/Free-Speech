import os
import json
import zipfile
import glob
import numpy as np
import subprocess as sp


def load_info(ses, custom_path=None):
    if custom_path==None:
        with open(os.path.join(os.path.dirname(__file__), "project_info.json")) as f:
            info = json.load(f)
    else:
        with open(os.path.join(custom_path)) as f:
            info = json.load(f)
    ses = str(ses)
    try: ses_info = info[ses]
    except:
        while not ses[-1].isdigit():
            ses = ses[:-1]
        ses_info = info["ses-"+ses]
    return ses_info



def check_dcm(sub, ses, raw_path="/sas2/PECON/7T/NatPAC/sourcedata"):

    
    # IMA path
    target_folder = f'NATPAC_SUB-{sub}_SES-{ses.upper()}'
    target_path = os.path.join(raw_path, target_folder)
    try:      
        print("\n---------------------------------------------------------------------------")
        print("Try unzip data")
        sp.call(" ".join(["unzip -qq", target_path+".zip", "-d", raw_path]),shell=True)
        os.remove(target_path+".zip")
        print("---------------------------------------------------------------------------")
    except:  
        print("\n---------------------------------------------------------------------------")
        print("Find sourcedata")

    target_list = glob.glob(os.path.join(target_path,"*"))   
    if len(target_list)>1:
        scan_date = []
        for foldername in target_list:
            try:
                foldername = os.path.basename(foldername)
                dates = foldername.split("_")[-3:]
                scan_date.append(int(dates[0])*(10**12)+ 
                                int(dates[1])*(10**6)+
                                int(dates[2]))
            except:
                scan_date.append(0)
        target_path = target_list[np.argmax(scan_date)]
    elif len(target_list) == 1:
        target_path = target_list[0]
    else:
        raise FileNotFoundError("File "+target_path+" do not exist")
    
    print("---------------------------------------------------------------------------")
    ses_info = load_info(ses)

    target_runs = []
    target_runs_data = dict()
    for run in ses_info:
        run_type = run["type"]
        if run_type == "func":
            for run_num in range(int(run["runs"])):
                run_name = "task-"+run["name"]+"_run-"+str(run_num+1)
                target_runs.append(run["type"]+"_"+run_name)
                target_runs_data[run["type"]+"_"+run_name]={
                    "dataType": run_type,
                    "modalityLabel": run["modality"],
                    "customLabels": run_name
                }
        elif run_type == "fmap":
            run_name = run["name"]
            if "GRE" in run_name:
                target_runs.append(run["type"]+"_"+run_name+"_"+run["modality"])
                target_runs_data[run["type"]+"_"+run_name+"_"+run["modality"]]={
                    "dataType": run_type,
                    "modalityLabel": run["modality"],
                    "customLabels": run_name
                }                         
            else:
                target_runs.append(run["type"]+"_"+run_name)
                target_runs_data[run["type"]+"_"+run_name]={
                    "dataType": run_type,
                    "modalityLabel": run["modality"],
                    "customLabels": run_name
                }           
        elif run_type == "dwi":
            run_name = run["name"]
            target_runs.append(run["type"]+"_"+run_name)
            target_runs_data[run["type"]+"_"+run_name]={
                "dataType": run_type,
                "modalityLabel": run["modality"],
                "customLabels": run_name
            }
        elif run_type == "anat":
            if run["modality"] == "MP2RAGE":
                target_runs.append("anat_MP2RAGE_"+run["name"].replace("-",""))
                target_runs_data["anat_MP2RAGE_"+run["name"].replace("-","")]={
                    "dataType": run_type,
                    "modalityLabel": run["modality"],
                    "customLabels": run["name"]                    
                }
            elif run["modality"] == "UNIT1":
                target_runs.append("anat_MP2RAGE_UNI")
                target_runs_data["anat_MP2RAGE_UNI"]={
                    "dataType": run_type,
                    "modalityLabel": run["modality"],
                    "customLabels": run["name"]                    
                }
            else:
                if "name" in run.keys():
                    target_runs.append(run["type"]+"_"+run["modality"]+"_"+run["name"])
                    target_runs_data[run["type"]+"_"+run["modality"]+"_"+run["name"]]={
                        "dataType": run_type,
                        "modalityLabel": run["modality"],
                        "customLabels": run["name"]
                    }
                else:
                    target_runs.append(run["type"]+"_"+run["modality"])
                    target_runs_data[run["type"]+"_"+run["modality"]]={
                        "dataType": run_type,
                        "modalityLabel": run["modality"]
                    }                    

 
    rundata = glob.glob(os.path.join(target_path,"*"))
    run_folders = []
    for run in rundata:
        run_folders.append(os.path.basename(run))
  
    order = []
    for run in run_folders:
        order.append(run.split("_")[-1])
    order = np.argsort(order)
    run_folders_raw = np.array(run_folders)[order]
    run_folders = []
    for name in run_folders_raw:
    	if not "_SPLIT_" in name:
            run_folders.append(name)
    run_folders = np.array(run_folders)
    
    # check results
    check_results = dict()
    for runname in target_runs:
        runname_upper = runname.upper()
        # GRE
        if "FMAP_ACQ-GRE" in runname_upper:   
               
            if "magnitude" in runname:  
                check_results[runname] = []
                check_results[runname.replace("magnitude", 'phase')] = []

                checked_run = []       
                for folder_name in run_folders:
                    if "_".join(runname_upper.split("_")[:-1]) in folder_name:
                        if folder_name.split("_")[-1] not in checked_run:
                            check_results[runname].append(folder_name)
                            check_results[runname.replace("magnitude", 'phase')].\
                                append(folder_name[:-4]+\
                                str(int(folder_name.split("_")[-1])+1).zfill(4))
                            checked_run.append(folder_name.split("_")[-1])
                            checked_run.append(str(int(folder_name.split("_")[-1])+1).zfill(4))                        
        # MP2RAGE
        elif "ANAT_MP2RAGE" in runname_upper:
            check_results[runname] = []
            mp2rage_type = runname_upper.split("_")[-1]
            for folder_name in run_folders:
                if "ANAT_MP2RAGE" in folder_name:
                    if mp2rage_type in folder_name:
                        check_results[runname].append(folder_name)
        # Chimap
        elif "ANAT_CHIMAP" in runname_upper:
            check_results[runname] = []
            for folder_name in run_folders:
                if "SWI_IMAGES" in folder_name:
                    check_results[runname].append(folder_name)                       
        else:
            check_results[runname] = []
            for folder_name in run_folders:
                if runname_upper in folder_name:
                    check_results[runname].append(folder_name)
                    
           
    for run in check_results.keys():
        if len(check_results[run]) > 1:
            check_results[run] = [check_results[run][-1]] 

 
    missed_run = []
    for run in target_runs:
        if check_results[run] == []: missed_run.append(run)
    if missed_run: 
        msg = "Run "
        for run in missed_run: msg = msg + '"' + run + '" ' 
        print("\n---------------------------------------------------------------------------")
        msg = msg+"is missed. \nNevertheless, do you want to continue? (y or n)\n"
        ans = input(msg)
        if ans == "n": 
            raise FileNotFoundError("Check '"+target_path+"' run_folder name")
        print("---------------------------------------------------------------------------")
        
        
    print("\n---------------------------------------------------------------------------")
    print("              TASK&RUN              -->              Raw_folder")
    print("---------------------------------------------------------------------------")
    for run in check_results.keys():
        try:
            print("%34s  -->  %s" % (run, check_results[run][0]))
        except:
            print("%34s  -->  %s" % (run, check_results[run]))
    return([check_results, target_runs_data, target_path])
    



def save_config(check_results, target_runs_data, sub, ses):

    filename = "sub-"+sub+"_ses-"+ses+"_config.json"
    

    bids_path = load_info("bids_path")
        

    json_data = dict()
    json_data["descriptions"] = []
    
        

    intendrange = []
    run_number = 0
    for bids_run in check_results.keys():
        if check_results[bids_run] != []:
            if target_runs_data[bids_run]["dataType"] == "func":
                intendrange.append(run_number)
            if "GRE" in bids_run:
                run_number += 2
            else: run_number += 1
    

    for bids_run in check_results.keys():
        if check_results[bids_run] == []:
            pass
        else:
            target_run = target_runs_data[bids_run]
            run_type = target_run["dataType"]
            criteria = {"SeriesNumber": int(check_results[bids_run][0][-4:])}
            if run_type == "anat":
                if "Chimap" in target_run["modalityLabel"]:
                    run_dict = {
                    "dataType": run_type,
                    "modalityLabel": target_run["modalityLabel"],
                    "customLabels": "echo-1",
                    "criteria": {"SeriesNumber": int(check_results[bids_run][0][-4:]),
                                "SidecarFilename": "*e1*"}
                    }
                    json_data["descriptions"].append(run_dict)
                    run_dict = {
                    "dataType": run_type,
                    "modalityLabel": target_run["modalityLabel"],
                    "customLabels": "echo-2",
                    "criteria": {"SeriesNumber": int(check_results[bids_run][0][-4:]),
                                "SidecarFilename": "*e2*"}
                    }
                    json_data["descriptions"].append(run_dict)  
                    run_dict = {
                    "dataType": run_type,
                    "modalityLabel": target_run["modalityLabel"],
                    "customLabels": "echo-3",
                    "criteria": {"SeriesNumber": int(check_results[bids_run][0][-4:]),
                                "SidecarFilename": "*e3*"}
                    }
                    json_data["descriptions"].append(run_dict)  
                    run_dict = {
                    "dataType": run_type,
                    "modalityLabel": target_run["modalityLabel"],
                    "customLabels": "echo-4",
                    "criteria": {"SeriesNumber": int(check_results[bids_run][0][-4:]),
                                "SidecarFilename": "*e4*"}
                    }                   
                else:
                    run_dict = target_run
                    run_dict["criteria"] = criteria
            elif run_type == "func":
                run_dict = target_run
                run_dict["sidecarChanges"] = {"TaskName": target_run['customLabels']}
                run_dict["criteria"] = criteria
            elif run_type == "fmap":
                if "GRE" in target_run["customLabels"]:
                    if target_run["modalityLabel"] == "magnitude":
                        run_dict = {
                        "dataType": run_type,
                        "modalityLabel": target_run["modalityLabel"]+"1",
                        "customLabels": target_run["customLabels"],
                        "criteria": {"SeriesNumber": int(check_results[bids_run][0][-4:]),
                                    "SidecarFilename": "*e1*"},
                        "intendedFor": intendrange
                        }  
                        json_data["descriptions"].append(run_dict)
                        run_dict = {
                        "dataType": run_type,
                        "modalityLabel": target_run["modalityLabel"]+"2",
                        "customLabels": target_run["customLabels"],
                        "criteria": {"SeriesNumber": int(check_results[bids_run][0][-4:]),
                                    "SidecarFilename": "*e2*"},
                        "intendedFor": intendrange
                        }    
                    elif target_run["modalityLabel"] == "phase": 
                        run_dict = {
                        "dataType": run_type,
                        "modalityLabel": target_run["modalityLabel"]+"1",
                        "customLabels": target_run["customLabels"],
                        "criteria": {"SeriesNumber": int(check_results[bids_run][0][-4:]),
                                    "SidecarFilename": "*e1_ph*"},
                        "intendedFor": intendrange
                        }  
                        json_data["descriptions"].append(run_dict)
                        run_dict = {
                        "dataType": run_type,
                        "modalityLabel": target_run["modalityLabel"]+"2",
                        "customLabels": target_run["customLabels"],
                        "criteria": {"SeriesNumber": int(check_results[bids_run][0][-4:]),
                                    "SidecarFilename": "*e2_ph*"},
                        "intendedFor": intendrange
                        }                                       
                else:
                    run_dict = target_run
                    run_dict["criteria"] = criteria
                    run_dict["intendedFor"] = intendrange
            json_data["descriptions"].append(run_dict)

    os.makedirs(os.path.join(bids_path, "tmp_dcm2bids"), exist_ok=True)


    json_path = os.path.join(bids_path, "tmp_dcm2bids", filename)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=4)  
    print("\n---------------------------------------------------------------------------")
    print("Save config file: "+ os.path.join(bids_path, "tmp_dcm2bids", filename))
    print("---------------------------------------------------------------------------")
    return 


def run_dcm2bids(sub, ses, input_path, custom_config=False, del_tmp=False):

    
    bids_path = load_info("bids_path")
    if custom_config==False:
        filename = "sub-"+sub+"_ses-"+ses+"_config.json"
    else: filename = custom_config
    command = ["dcm2bids",
        "-d", input_path,
        "-p", sub,
        "-s", ses,
        "-c", os.path.join(bids_path, "tmp_dcm2bids", filename),
        "-o", bids_path]
        #"--forceDcm2niix --clobber"]
        
    command = " ".join(command)
    sp.call(command, shell=True)
    
    command = ["mv",
               os.path.join(bids_path, "tmp_dcm2bids", filename),
               os.path.join(bids_path, "sub-"+sub)]
    command = " ".join(command)
    sp.call(command, shell=True)
    
    if del_tmp:
        sp.call("rm -rf "+os.path.join(os.path.join(bids_path, "tmp_dcm2bids", "sub-"+sub+"_ses-"+ses+"*")), shell=True)
    return 




import argparse
parser = argparse.ArgumentParser(description='NatPAC dcm2bids')
parser.add_argument('sub', help='subject number')
parser.add_argument('ses', help='session number')
parser.add_argument("--input_path", help="path of ima zip file", action="store")
parser.add_argument("--custom_config", help="path of custom config file", action="store")


args = parser.parse_args()
sub = str(args.sub)
ses = str(args.ses)
try:
    if int(args.input_path) > 0: 
        input_path = str(args.input_path)
    else:
        input_path = None
except:
    input_path = None

try:
    if int(args.custom_config) > 0: 
        custom_config = str(args.custom_config)
    else:
        custom_config = None
except:
    custom_config = None


if input_path == None:
    [check_results, target_runs_data, target_path] = check_dcm(sub, ses)
else:
    [check_results, target_runs_data, target_path] = check_dcm(sub, ses, input_path)
if custom_config == None:
    save_config(check_results, target_runs_data, sub, ses)
    run_dcm2bids(sub, ses, target_path)
else:
    run_dcm2bids(sub, ses, target_path, custom_config=custom_config)
