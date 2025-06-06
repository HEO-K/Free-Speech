# %%
import numpy as np
import os
import glob
import json
import pandas as pd
import subprocess as sp
from Speech.load_project_info import get_full_info,get_brain_path
import zipfile
import re
from Speech.tools import isWSL



########################## dcm2bids용 #################################
# raw 파일 확인하기
def check_dcm(Project, input_path, ses = None):

    """ bids로 변경할 Raw 파일을 확인, 빠진 run이 있는지와 run 변경 방식 출력

    Args:
        Project (str): 프로젝트 이름.
        input_path (str): Raw 데이터 위치.
        ses (str, optional): 세션이 존재할 경우 입력. Defaults to None.
        
    Returns:
        dict: run이름(NAME1): [폴더 정보]
        dict: run이름(NAME1): [run 정보]
        str: IMA 파일 위치
        
    """

    # 정보 불러오기.
    info = get_full_info(Project)
    
    
    # 세션 정보 불러오기
    if ses == None:
        ses_info = info['info']
    else:
        ses_info = info["ses-"+ses]   
        
    
    # baseline이 되는 run정보 만들기
    target_runs = []
    target_runs_data = dict()
    for run in ses_info:
        runname = run["name"]
        # func
        if run["type"] == "func":
            try:
                runs = run["runs"]
                for i in range(runs):
                    target_runs.append(runname+str(i+1))
                    target_runs_data[runname+str(i+1)] = run
            except:
                target_runs.append(runname)
                target_runs_data[runname] = run
        # anat
        elif run["type"] == "anat":
            if run["modality"] == "T1w": 
                target_runs.append(runname+"_MPRAGE")
                target_runs_data[runname+"_MPRAGE"] = run
            elif run["modality"] == "MP2RAGE": 
                target_runs.append("MP2RAGE_"+runname)
                target_runs_data["MP2RAGE_"+runname] = run
            elif run["modality"] == "UNIT1": 
                target_runs.append("MP2RAGE_UNI")
                target_runs_data["MP2RAGE_UNI"] = run
        # fmap
        elif run["type"] == "fmap":
            if runname == "acq-GRE": 
                target_runs.append("GRE_"+run["modality"])
                target_runs_data["GRE_"+run["modality"]] = run
            elif runname == "dir-AP": 
                target_runs.append("REF_AP")
                target_runs_data["REF_AP"] = run
        
        
    # Input의 중복 run제거하기
    target_path = os.path.abspath(os.path.join(input_path, "."))
    raw_path = os.path.dirname(target_path)
    try:      # 압축 풀기 시도 (zip파일이 존재하면 시도한다.)
        with zipfile.ZipFile(target_path+".zip", "r") as zip_ref:
            print("\n-----------------------------------------------------")
            print("Unzip data")
            zip_ref.extractall(raw_path)
        os.remove(target_path+".zip")
    except:   # 되어 있다면 그냥 넘어감
        pass
    # 한 스캔 정보로 여러번 스캔하면 폴더가 여러개 생성됨
    target_list = glob.glob(os.path.join(target_path,"*"))   
    if len(target_list)>1: # 그래서 가장 최근 것만 사용
        scan_date = []
        for foldername in target_list:
            foldername = os.path.basename(foldername)
            dates = foldername.split("_")[-3:]
            scan_date.append(int(dates[0])*(10**12)+
                             int(dates[1])*(10**6)+
                             int(dates[2]))
        target_path = target_list[np.argmax(scan_date)]
    elif len(target_list) == 1:
        target_path = target_list[0]
    else:
        raise FileNotFoundError("File "+target_path+" do not exist")   
    

    # Input IMA의 폴더 정보 불러오기
    rundata = glob.glob(os.path.join(target_path,"*"))
    run_folders = []
    for run in rundata:
        run_folders.append(os.path.basename(run))
    # 순서대로 정렬
    order = []
    for run in run_folders:
        order.append(run.split("_")[-1])
    order = np.argsort(order)
    run_folders = np.array(run_folders)[order]
    run_folders = [folder_name for folder_name in run_folders if not "_SPLIT_" in folder_name]        
            
    # check results
    check_results = dict()
    for runname in target_runs:
        runname_upper = runname.upper()
        # GRE
        if "GRE" in runname_upper:      
            if "magnitude" in runname:  # magnitude로만 완성
                check_results[runname] = []
                check_results[runname.replace("magnitude", 'phase')] = []
                run_exp = re.compile("GRE")  # gre_run이름
                checked_run = []
                for folder_name in run_folders:
                    if len(run_exp.findall(folder_name))>0:
                        if folder_name.split("_")[-1] not in checked_run:
                            check_results[runname].append(folder_name)
                            check_results[runname.replace("magnitude", 'phase')].\
                                append(folder_name[:-4]+\
                                    str(int(folder_name.split("_")[-1])+1).zfill(4))
                        checked_run.append(folder_name.split("_")[-1])
                        checked_run.append(str(int(folder_name.split("_")[-1])+1).zfill(4))
        # MP2RAGE
        elif "MP2RAGE" in runname_upper:
            check_results[runname] = []
            ref = runname_upper.split("_")[-1]
            if "-" in ref: ref = ref.replace("-","")
            for folder_name in run_folders:
                if ref in folder_name:
                    check_results[runname].append(folder_name)

        else:
            check_results[runname] = []
            for folder_name in run_folders:
                if runname_upper in folder_name:
                    check_results[runname].append(folder_name)
    # 모든 동일한 run 중 가장 마지막 run만 사용            
    for run in check_results.keys():
        if len(check_results[run]) > 1:
            check_results[run] = [check_results[run][-1]] 

    
    
    # print results
    missed_run = []
    for run in target_runs:
        if check_results[run] == []: missed_run.append(run)
    if missed_run: 
        msg = "Run "
        for run in missed_run: msg = msg + '"' + run + '" ' 
        msg = msg+"is missed. Nevertheless, do you want to continue? (y or n)\n"
        ans = input(msg)
        if ans == "n": return
    
    print("\n-------------------------------------------------------")
    print("        TASK&RUN        -->        Raw_folder")
    print("-------------------------------------------------------")
    for run in check_results.keys():
        try:
            print("%22s  -->  %s" % (run, check_results[run][0]))
        except:
            print("%22s  -->  %s" % (run, check_results[run]))
    print("\n\n")
    return(check_results, target_runs_data, target_path)
    
    
# dcm2bids config file 저장
def save_config(check_results, target_runs_data, Project, sub, ses=None):
    """ bids folder의 tmp_dcm2bids 안에 임시 config file 생성.

    Args:
        check_results (dict): check_dcm의 결과.
        target_runs_data (dict): check_dcm의 결과.
        Project (str): 프로젝트 이름.
        sub (str): bids의 sub 번호.
        ses (str, optional): session. Defaults to None.
    """
    
    # 저장되는 파일 이름
    if ses == None: filename = "sub-"+sub+"_tmp.json"
    else: filename = "sub-"+sub+"_ses-"+ses+"_tmp.json"
    
    # 프로젝트 정보 불러오기.
    info = get_full_info(Project)
        
    # json 데이터 생성
    json_data = dict()
    json_data["descriptions"] = []
    
    # fmap이 가리키는 run들
    intendrange = []
    run_number = 0
    for bids_run in check_results.keys():
        if check_results[bids_run] != []:
            if target_runs_data[bids_run]["type"] == "func":
                intendrange.append(run_number)
            if "GRE" in target_runs_data[bids_run]["name"]:
                run_number += 2
            else: run_number += 1
    
    for bids_run in check_results.keys():
        if check_results[bids_run] == []:
            pass
        else:
            target_run = target_runs_data[bids_run]
            run_type = target_run["type"]
            if run_type == "anat":
                if target_run["modality"] == "T1w":
                    run_dict = {
                    "dataType": run_type,
                    "modalityLabel": target_run["modality"],
                    "criteria": {"SeriesNumber": int(check_results[bids_run][0][-4:])}
                    }   
                else:  
                    run_dict = {
                    "dataType": run_type,
                    "modalityLabel": target_run["modality"],
                    "customLabels": target_run["name"],
                    "criteria": {"SeriesNumber": int(check_results[bids_run][0][-4:])}
                    }          
            elif run_type == "func":
                run_number = re.sub(r'[^0-9]', '', bids_run)
                if len(run_number)>0:
                    func_label = "task-"+target_run['name']+"_run-"+run_number
                else:
                    func_label ="task-"+target_run['name']
                run_dict = {
                   "dataType": run_type,
                   "modalityLabel": target_run["modality"],
                   "customLabels": func_label,
                   "criteria": {"SeriesNumber": int(check_results[bids_run][0][-4:])},
                   "sidecarChanges": {"TaskName": target_run['name']}
                   }
            elif run_type == "fmap":
                if "GRE" in target_run["name"]:
                    if target_run["modality"] == "magnitude":
                        run_dict = {
                        "dataType": run_type,
                        "modalityLabel": target_run["modality"]+"1",
                        "customLabels": target_run["name"],
                        "criteria": {"SeriesNumber": int(check_results[bids_run][0][-4:]),
                                    "SidecarFilename": "*e1*"},
                        "intendedFor": intendrange
                        }  
                        json_data["descriptions"].append(run_dict)
                        run_dict = {
                        "dataType": run_type,
                        "modalityLabel": target_run["modality"]+"2",
                        "customLabels": target_run["name"],
                        "criteria": {"SeriesNumber": int(check_results[bids_run][0][-4:]),
                                    "SidecarFilename": "*e2*"},
                        "intendedFor": intendrange
                        }    
                    elif target_run["modality"] == "phase": 
                        run_dict = {
                        "dataType": run_type,
                        "modalityLabel": target_run["modality"]+"1",
                        "customLabels": target_run["name"],
                        "criteria": {"SeriesNumber": int(check_results[bids_run][0][-4:]),
                                    "SidecarFilename": "*e1_ph*"},
                        "intendedFor": intendrange
                        }  
                        json_data["descriptions"].append(run_dict)
                        run_dict = {
                        "dataType": run_type,
                        "modalityLabel": target_run["modality"]+"2",
                        "customLabels": target_run["name"],
                        "criteria": {"SeriesNumber": int(check_results[bids_run][0][-4:]),
                                    "SidecarFilename": "*e2_ph*"},
                        "intendedFor": intendrange
                        }                                       
                else:
                    run_dict = {
                    "dataType": run_type,
                    "modalityLabel": target_run["modality"],
                    "customLabels": target_run["name"],
                    "criteria": {"SeriesNumber": int(check_results[bids_run][0][-4:])},
                    "intendedFor": intendrange
                    }                
            json_data["descriptions"].append(run_dict)
            

    bids_path = info['bids_path']
    os.makedirs(os.path.join(bids_path, "tmp_dcm2bids"), exist_ok=True)

    json_path = os.path.join(bids_path, "tmp_dcm2bids", filename)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=4)

    return 



# dcm2bids
def run_dcm2bids(Project, sub, input_path, ses=None):
    """tmp폴더의 json 정보를 통해 dcm2bids 실행.

    Args:
        Project (str): 프로젝트 이름.
        sub (str): bids의 sub 번호
        input_path (str): dcm 파일 위치
        ses (str, optional): session. Defaults to None.
    """

    if isWSL() == False: return "WSL, base환경에서 실행!!"

    # 정보 불러오기.
    info = get_full_info(Project)
    
    bids_path = info['bids_path']
    
    if ses == None: 
        filename = "sub-"+sub+"_tmp.json"
        command = ["dcm2bids",
                "-d", input_path,
                "-p", sub,
                "-c", os.path.join(bids_path, "tmp_dcm2bids", filename),
                "-o", bids_path,
                "--forceDcm2niix --clobber"]
    else: 
        filename = "sub-"+sub+"_ses-"+ses+"_tmp.json"
        command = ["dcm2bids",
            "-d", input_path,
            "-p", sub,
            "-s", ses,
            "-c", os.path.join(bids_path, "tmp_dcm2bids", filename),
            "-o", bids_path,
            "--forceDcm2niix --clobber"]

    command = " ".join(command)
    sp.call(command, shell=True)
    
    sp.call("rm -rf "+os.path.join(os.path.join(bids_path, "tmp_dcm2bids", "*")), shell=True)




################################ Prep 이후 denosing ###################################
# load (prep) confound
def load_confounds(Project, sub, runname, ses=None):
    bids_path = get_brain_path(Project)
    sub_path = os.path.join(bids_path,  "sub-"+sub)
    
    
    sub = "sub-"+sub
    task = "_task-"+runname
    
    if ses == None: ses = ""
    else: 
        sub_path = os.path.join(sub_path, "ses-"+ses)
        ses = "_ses-" + ses
    sub_path = os.path.join(sub_path, "func")
    tsv_name = sub+ses+task+"_desc-confounds_*.tsv"
    
    confounds= os.path.join(sub_path, tsv_name)
    confounds = glob.glob(confounds)[0]
    
    
    df = pd.read_csv(confounds, sep='\t')
    return df



# polynomial regression
def make_poly_regressors(n_samples, order=2):
    from numpy.polynomial.legendre import Legendre
    # mean
    X = np.ones((n_samples, 1))
    for d in range(order):
        poly = Legendre.basis(d + 1)
        poly_trend = poly(np.linspace(-1, 1, n_samples))
        X = np.hstack((X, poly_trend[:, None]))
    return X



# denosing
def clean_data(data, confounds, custom_columns=None):
    import scipy.linalg as la

    # default로 설정된 noise들
    columns = [
        'global_signal',
        'framewise_displacement',
        'trans_x', 'trans_x_derivative1',
        'trans_y', 'trans_y_derivative1',
        'trans_z', 'trans_z_derivative1',
        'rot_x', 'rot_x_derivative1',
        'rot_y', 'rot_y_derivative1',
        'rot_z', 'rot_z_derivative1',
    ]
    
    if custom_columns != None:
        columns = custom_columns
    
    # a_compcor
    n_comp_cor = 6 # top 6
    columns += [f"a_comp_cor_{c:02d}" for c in range(n_comp_cor)]
    X = confounds[columns].values

    # remove nans
    X[np.isnan(X)] = 0.
    
    # add polynomial components
    n_samples = X.shape[0]
    X = np.hstack((X, make_poly_regressors(n_samples, order=2)))

    # time to clean up
    # center the data first and store the mean
    data_mean = data.mean(0)
    data = data - data_mean
    coef, _, _, _ = la.lstsq(X, data)
    # remove trends and add back mean of the data
    data_clean = data - X.dot(coef) + data_mean
    return data_clean


# load confound + clean data
def DN(Project, sub, runname, ses=None, custom_columns=None):
    # confound
    fmri_compounds = load_confounds(Project, sub, runname, ses)
    # epi
    import nibabel as nib
    info = get_full_info(Project)
    if isWSL():
        file_path = os.path.join(info['bids_path'], "derivatives", "sub-"+sub)
    else:
        return "Change to WSL"
    if ses == None:
        file_path = os.path.join(file_path, "func", "*"+runname+"_space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz")
    else:
        file_path = os.path.join(file_path, "ses-"+ses, "func", "*"+runname+"_space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz")
    file_path = glob.glob(file_path)[-1]
    fmri_data = nib.load(file_path)
    vox = fmri_data.header.get_zooms()[0]
    vox = "{:.1f}".format(vox)
    fmri_data = fmri_data.get_fdata()

    # mni
    mni_path = __file__
    mni_path = os.path.abspath(os.path.join(mni_path, "..", '..', '_data_Atlas', 'MNI'))
    mni_mask = nib.load(os.path.join(mni_path, "MNI_"+vox+"mm_mask.nii.gz")).get_fdata()
    mni_image = nib.load(os.path.join(mni_path, "MNI_"+vox+"mm.nii.gz"))
    # masking
    fmri_data = fmri_data[mni_mask==1,:].T

    # cleaning
    fmri_clean = clean_data(fmri_data, fmri_compounds, custom_columns=custom_columns)
    fmri_clean = fmri_clean.astype(np.float32)
    new_image = np.zeros(mni_mask.shape+(fmri_data.shape[0],), dtype=np.float32)
    new_image[mni_mask==1,:] = fmri_clean.T

    # save
    save_path = file_path.split("_space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz")[0]+".nii.gz"
    nib.save(nib.Nifti1Image(new_image, mni_image.affine),save_path)
    print("\n")
    print("---------------------------------------------------------------------")
    print(os.path.basename(file_path).split("_space")[0]+" denosing finished")
    print("---------------------------------------------------------------------")



# save motion & FD checking
def save_motion(Project, sub, ses=None, threshold=0.05):
    import matplotlib.pyplot as plt
    from scipy.stats import sem

    # 정보 불러오기.
    info = get_full_info(Project) 
    # 피험자 위치
    if isWSL():
        sub_path = os.path.join(info['bids_path'], "derivatives", "sub-"+sub)
    else:
        sub_path = os.path.join(info['bids_path_window'], "derivatives", "sub-"+sub)
    fig_path = os.path.join(sub_path,'figures')
    # run 정보
    if ses == None:
        run_info = info['info']
        func_path = os.path.join(sub_path, "func")
    else:
        run_info = info["ses-"+ses]  
        func_path = os.path.join(sub_path, "ses-"+ses, "func")
    runnames = []
    for run in run_info:
        if 'runs' in run.keys():
            for i in range(1, run["runs"]+1):
                runnames.append(run["name"]+"_run-"+str(i))
        else: runnames.append(run["name"])

    # 존재하는 파일만 사용한다.
    files = []
    for name in runnames:
        file_path = glob.glob(os.path.join(func_path, "*"+name+"*confounds_*.tsv"))
        if len(file_path)>0: files.append(file_path[0])
        

    # plot
    plt.figure(figsize=(20,2.5*len(files)))
    plt.subplots_adjust(hspace=0.5)
    
    summary_stat = dict()
    
    for file, i in zip(files, range(len(files))):
        task = file.split("task-")[1].split("_desc")[0]
        print(task)
        motions = pd.read_csv(file, sep="\t")
        pars = np.array(motions[['trans_x', 'trans_y', 'trans_z', 
                                 'rot_x', 'rot_y', 'rot_z']])
        pars = np.nan_to_num(pars)
        fd = np.array(motions['framewise_displacement'])
        fd = np.nan_to_num(fd)

        # save outlier list
        motion_confound = fd > 0.5
        motion_confound = np.array(motion_confound, int)
        motion_confound = np.array(motion_confound, str)
        with open(file.split("-confounds")[0]+"-FDoutlier.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(motion_confound))

        # save subjects
        if np.mean(fd>0.5) < threshold: # FD>0.5인 구간이 5% 미만
            good_sub_path = __file__
            good_sub_path = os.path.abspath(os.path.join(good_sub_path, "..", ".."))
            good_sub_path = os.path.join(good_sub_path, "_data_Project", Project, "good_sub.json")
            if ses == None: ses_index = "info"
            else: ses_index = "ses-"+ses
            try:
                with open(good_sub_path) as f:
                    good_sub = json.load(f)

                if task in good_sub[ses_index].keys():
                    if sub not in good_sub[ses_index][task]: good_sub[ses_index][task].append(sub)
                else:
                    good_sub[ses_index][task] = [sub]
                f.close()
            except:
                good_sub = dict()
                good_sub[ses_index] = dict()
                good_sub[ses_index][task] = [sub]
            with open(good_sub_path, "w", encoding="utf-8") as f:
                json.dump(good_sub, f, indent=4)
            f.close()

        # save plot
        plt.subplot(len(files), 3, 1+3*i)
        plt.plot(pars[:,:3])
        plt.ylabel("Trans (mm)")
        plt.legend(['x','y','z'])
        plt.ylim([-2,2])
        plt.subplot(len(files), 3, 2+3*i)
        plt.plot(pars[:,3:])
        plt.title(task+" (outlier ratio: "+str(np.round(np.mean(fd>0.5),3))+")")
        plt.ylabel("Rot (radian)")
        plt.legend(['x','y','z'])
        plt.ylim([-0.05,0.05])
        plt.subplot(len(files), 3, 3+3*i)
        plt.plot(fd, color='k')
        if np.max(fd)>1.5:
            plt.text(np.argmax(fd), 1.53, str(np.round(np.max(fd),2)), 
                horizontalalignment='center')
        else:
            plt.text(np.argmax(fd), np.max(fd)+0.03, str(np.round(np.max(fd),2)), 
                horizontalalignment='center')
        plt.ylim([0,1.5])
        plt.axhline(y=0.5, color='r', linestyle = "--", linewidth=2)
        plt.ylabel("FD")
        
        summary_stat[task] = fd
    # save
    os.makedirs(fig_path, exist_ok=True)
    if ses == None:
        fig_path = os.path.join(fig_path, "sub-"+sub+"_motion.png")
    else:
        fig_path = os.path.join(fig_path, "sub-"+sub+"_ses-"+ses+"_motion.png")
    
    if os.path.isfile(fig_path): os.remove(fig_path)
    plt.savefig(fig_path, dpi=200)
    
    
    # save summary image
    fig_path = os.path.join(sub_path,'figures')
    plt.figure(figsize=(1.5*len(summary_stat),5))
    plt.xticks(np.arange(len(summary_stat.keys())), list(summary_stat.keys()), rotation=30)
    plt.ylim(0,0.5)
    plt.ylabel("FD")
    for i, task in enumerate(summary_stat.keys()):
        plt.bar(i, np.nanmean(summary_stat[task]), yerr=sem(summary_stat[task]), color='grey')
        outlier_ratio = str(np.round(np.mean(summary_stat[task]>0.5),3))
        plt.text(i, np.nanmean(summary_stat[task])+sem(summary_stat[task])+0.02, outlier_ratio,
                 horizontalalignment='center')
    if ses == None:
        fig_path = os.path.join(fig_path, "sub-"+sub+"_motion_summary.png")
    else:
        fig_path = os.path.join(fig_path, "sub-"+sub+"_ses-"+ses+"_motion_summary.png")
    
    if os.path.isfile(fig_path): os.remove(fig_path)
    plt.savefig(fig_path, dpi=200, bbox_inches = 'tight')   
    
    print("---------------------------------------------------------------------")
    print("sub-"+sub+" motion plot is saved")
    print("---------------------------------------------------------------------")


def save_tsnr(Project, sub, ses=None):
    import matplotlib.pyplot as plt
    import nibabel as nib
    from tqdm import tqdm
    from scipy.stats import sem
    
    # 정보 불러오기.
    info = get_full_info(Project) 
    # 피험자 위치
    if isWSL():
        sub_path = os.path.join(info['bids_path'], "derivatives", "sub-"+sub)
    else:
        sub_path = os.path.join(info['bids_path_window'], "derivatives", "sub-"+sub)
    fig_path = os.path.join(sub_path,'figures')
    # run 정보
    if ses == None:
        run_info = info['info']
        func_path = os.path.join(sub_path, "func")
    else:
        run_info = info["ses-"+ses]  
        func_path = os.path.join(sub_path, "ses-"+ses, "func")
    runnames = []
    for run in run_info:
        if 'runs' in run.keys():
            for i in range(1, run["runs"]+1):
                runnames.append(run["name"]+"_run-"+str(i))
        else: runnames.append(run["name"])

    # 존재하는 파일만 사용한다.
    files = []
    for name in runnames:
        file_path = glob.glob(os.path.join(func_path, 
                                           "*"+name+"*space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz"))
        if len(file_path)>0: files.append(file_path[0])
    
    # Yeo network에 들어오는 값만 사용한다.
    vox = str(nib.load(files[0]).header.get_zooms()[0])
    from Speech.tools_EPI import get_atlas
    atlas = get_atlas("Yeo2011_7Networks_tight", size=vox)[1]
    mask = atlas>0
    
    
    plt.figure(figsize=(1.5*len(files),5))
    tasknames = []
    tsnr_map = []
    for i, file in tqdm(enumerate(files), "Plotting summary tSNR"):
        tasknames.append(file.split("task-")[1].split("_space")[0])
        epi = nib.load(file).get_fdata()
        mean_d = np.mean(epi,axis=-1)
        std_d = np.std(epi,axis=-1)
        tsnr = mean_d/std_d
        tsnr_map.append(tsnr)
        tsnr_brain = tsnr[mask]
        tsnr_brain = tsnr_brain[~np.isnan(tsnr_brain)]
        plt.bar(i, np.mean(tsnr_brain), yerr=sem(tsnr_brain), color="grey")
    plt.xticks(np.arange(len(files)), tasknames, rotation=30)
    plt.ylabel("tSNR")
    
    # save summary
    if ses == None:
        fig_file = os.path.join(fig_path, "sub-"+sub+"_tsnr_summary.png")
    else:
        fig_file = os.path.join(fig_path, "sub-"+sub+"_ses-"+ses+"_tsnr_summary.png")
    
    if os.path.isfile(fig_file): os.remove(fig_file)
    plt.savefig(fig_file, dpi=200, bbox_inches = 'tight')       
    
    
    
    # plot network tsnr
    colors = [[120,18,134],
              [70,130,180],
              [0,118,14],
              [196,58,250],
              [220,248,164],
              [230,148,34],
              [205,62,78]]
    colors = np.array(colors)/255
    network = ["Visual", "SomMot", "DorsAttn", "VentAttn", "Limbic", "Control", "Default"]
    plt.figure(figsize=(10,2.5*len(files)))
    plt.subplots_adjust(hspace=0.5)
    
    for i, file in tqdm(enumerate(files), "Plotting network tSNR"):
        task = file.split("task-")[1].split("_space")[0]
        tsnr = tsnr_map[i]
        plt.subplot(len(files), 1, 1+i)
        plt.title(task)
        for n in range(7):
            tsnr_net = tsnr[atlas==n+1]
            tsnr_net = tsnr_net[~np.isnan(tsnr_net)]
            plt.bar(n, np.mean(tsnr_net), yerr=sem(tsnr_net), color=colors[n], ecolor=colors[n], alpha=0.3)
        plt.xticks(np.arange(7), network)
        plt.ylabel("tSNR")
        
    # save 
    if ses == None:
        fig_file = os.path.join(fig_path, "sub-"+sub+"_tsnr.png")
    else:
        fig_file = os.path.join(fig_path, "sub-"+sub+"_ses-"+ses+"_tsnr.png")
    
    if os.path.isfile(fig_file): os.remove(fig_file)
    plt.savefig(fig_file, dpi=200, bbox_inches = 'tight')               
        
    print("---------------------------------------------------------------------")
    print("sub-"+sub+" tSNR plot is saved")
    print("---------------------------------------------------------------------")       
        


def sc_dt_hp_sm(Project, sub, runname, ses=None):
    import nibabel as nib
    info = get_full_info(Project)
    if isWSL():
        file_path = os.path.join(info['bids_path'], "derivatives", "sub-"+sub)
    else:
        return "Change to WSL"
    if ses == None:
        file_path = os.path.join(file_path, "func")
    else:
        file_path = os.path.join(file_path, "ses-"+ses, "func")

    input_fname = glob.glob(os.path.join(file_path, "*"+runname+".nii.gz"))[0]
    mean_fname = input_fname.split(".nii.gz")[0] + '_mean.nii.gz'
    SC_fname = input_fname.split(".nii.gz")[0] + '_sc.nii.gz'
    DT_fname = input_fname.split(".nii.gz")[0] + '_sc_dt.nii.gz'
    HP_fname = input_fname.split(".nii.gz")[0] + '_sc_dt_hp.nii.gz'
    SM_HP_fname = input_fname.split(".nii.gz")[0] + '_sc_dt_hp_sm.nii.gz'
    final_fname = input_fname.split(".nii.gz")[0] + '_final.nii.gz'

    print_name = os.path.basename(input_fname).split("_nii.gz")[0]

    vox = nib.load(input_fname).header.get_zooms()[0]
    mni_path = __file__
    vox_str = "{:.1f}".format(vox)
    mask_fname = os.path.abspath(os.path.join(mni_path, "..", '..', '_data_Atlas', 'MNI', "MNI_"+vox_str+"mm_mask.nii.gz"))

    # Scaling
    sp.call(f'3dTstat -prefix {mean_fname} {input_fname}', shell=True)
    sp.call(f"3dcalc -a {input_fname} -b {mean_fname} -c {mask_fname} -expr 'c * min(200, a/b*100)*step(a)*step(b)' -prefix {SC_fname}",
            shell=True)
    print("---------------------------------------------------------------------")
    print(print_name+" scaling finished")
    print("---------------------------------------------------------------------")

    # detrending
    sp.call(f'3dDetrend -polort 1 -prefix {DT_fname} {SC_fname}', shell=True)
    print("---------------------------------------------------------------------")
    print(print_name+" detrending finished")
    print("---------------------------------------------------------------------")

    # high-pass filtering
    sp.call(f'3dBandpass -prefix {HP_fname} 0.01 99999 {DT_fname}', shell=True)
    print("---------------------------------------------------------------------")
    print(print_name+" filtering finished")
    print("---------------------------------------------------------------------")

    # Spatial Smoothing
    if vox == 1.5: FWHM = 2
    elif vox == 2: FWHM = 3
    elif vox == 2.5: FWHM = 4
    elif vox == 3: FWHM = 5
    else: FWHM = vox
    sp.call(f'3dmerge -quiet -1blur_fwhm {FWHM} -doall -prefix {SM_HP_fname} {HP_fname}', shell=True)
    sp.call(f"cp {SM_HP_fname} {final_fname}", shell=True)
    print("---------------------------------------------------------------------")
    print(print_name+" smoothing finished")
    print("---------------------------------------------------------------------")
    
    

# SS MP2RAGE
def MP2RAGE(Project, sub, output=None, ses=None, replace="03_UNI_SS.nii.gz"):
    from Speech.tools import isWSL
    if not isWSL(): return("Change WSL")
    info = get_full_info(Project)
    bids_path = info['bids_path']
    if output == None:
        if bids_path[-1] == "/": output_path = bids_path[:-1]+"_raw"
        else: output_path = bids_path+"_raw"
    else:
        output_path = output
    
    if ses == None:
        t1_path = os.path.join(bids_path, "sub-"+sub, 'anat')
        raw_path = os.path.join(output_path, "sub-"+sub, 'anat')
    else:
        t1_path = os.path.join(bids_path, "sub-"+sub, 'ses-'+ses, 'anat')
        raw_path = os.path.join(output_path, "sub-"+sub, 'ses-'+ses, 'anat')
        
    uni = glob.glob(os.path.join(raw_path, "*UNI.nii.gz"))[0]
    inv1 = glob.glob(os.path.join(raw_path, "*UNI.nii.gz"))[0]
    inv2 = glob.glob(os.path.join(raw_path, "*UNI.nii.gz"))[0]
    
    # bet
    inv2_bet = os.path.join(raw_path, "02_INV2_bet.nii.gz")
    sp.call(f"bet {inv2} {inv2_bet} -f 0.2 -m -R -v", shell=True)
    
    uni_ss = os.path.join(raw_path, "03_UNI_SS.nii.gz")
    inv2_bet_mask = os.path.join(raw_path, "02_INV2_bet_mask.nii.gz")
    sp.call(f"fslmaths {inv2_bet_mask} -mul {uni} {uni_ss}", shell=True)
    
    # remove dura
    uni_ss_ss = os.path.join(raw_path, "04_UNI_SS_SS.nii.gz")
    sp.call(f"3dSkullStrip -input {uni_ss} -prefix {uni_ss_ss} -orig_vol", shell=True)
    
    
    if replace != None:
        new_t1 = os.path.join(raw_path, "*"+replace)
        invs = os.path.join(t1_path, "*INV*")
        sp.call(f"rm -rf {invs}", shell=True)
        uni_json = os.path.join(t1_path, "sub-"+sub+'_ses-'+ses+"_UNI.json")
        t1w_json = os.path.join(t1_path, "sub-"+sub+'_ses-'+ses+"_T1w.json")
        sp.call(f"mv {uni_json} {t1w_json}", shell=True)
        t1w = os.path.join(t1_path, "sub-"+sub+'_ses-'+ses+"_T1w.nii.gz")
        sp.call(f"cp {new_t1} {t1w}", shell=True)
# %%