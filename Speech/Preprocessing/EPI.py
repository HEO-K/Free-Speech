# %%
import numpy as np
import os
import glob
import json
import pandas as pd
import subprocess as sp
from Speech.load_project_info import get_full_info

###################### 스크립트서 자주 쓰일 함수 ########################
# 리눅스인지 확인 
def isWSL():
    if os.getcwd()[0] == "/": return True
    else: return False



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
    for run in ses_info:
        runname = run["name"]
        try:
            runs = run["runs"]
            for i in range(runs):
                target_runs.append(runname+str(i+1))
        except:
            target_runs.append(runname)
    
        
    # Input의 중복 run제거하기
    target_path = os.path.join(input_path, '*')
    while len(glob.glob(target_path)) == 1: target_path = os.path.join(target_path, "*")
    # Run data
    rundata = glob.glob(target_path)
    runs = []
    for run in rundata:
        runs.append(list(os.path.split(run))[-1])
    # Run order
    order = []
    for run in runs:
        order.append(run.split("_")[-1])
    order = np.argsort(order)
    # sorted runs
    runs = np.array(runs)[order]
    
    
    # check results
    check_results = dict()
    for runname in target_runs:
        try:
            name = runname.split('_')[0]
            runs = runname.split('_')[1]
            runname_upper = name.upper()+"_"+runs
        except:
            runname_upper = runname.upper()
        check_results[runname] = []
        for run in runs:
            if runname_upper == run.split("_")[0]:  # name_index의 형태이므로, 만약 아예 겹치는 이름이 없다면 아래가 나음
            # if runname in run:
                check_results[runname].append(run)
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
    
    print("\n-------------------------------------\n    TASK&RUN    -->    Raw_folder\n-------------------------------------")
    for run in check_results.keys():
        try:
            print("%14s  -->  %s" % (run, check_results[run][0]))
        except:
            print("%14s  -->  %s" % (run, check_results[run]))
    print("\n\n")
    return(check_results)
    
    
# dcm2bids config file 저장
def save_config(check_results, Project, sub, ses=None):
    """ bids folder의 tmp_dcm2bids 안에 임시 config file 생성.

    Args:
        check_results (dict): check_dcm의 결과.
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
    
    for bids_run in check_results.keys():
        if check_results[bids_run] == []:
            pass
        else:
            if bids_run == "T1":
                run_dict = {
                    "dataType": "anat",
                    "modalityLabel": "T1w",
                    "criteria": {"SeriesNumber": int(check_results[bids_run][0][-4:])}
                    }
            elif bids_run == "UNI":
                run_dict = {
                    "dataType": "anat",
                    "modalityLabel": "UNI",
                    "criteria": {"SeriesNumber": int(check_results[bids_run][0][-4:])}
                    }
            elif bids_run == "INV1":
                run_dict = {
                    "dataType": "anat",
                    "modalityLabel": "INV1",
                    "criteria": {"SeriesNumber": int(check_results[bids_run][0][-4:])}
                    }
            elif bids_run == "INV2":
                run_dict = {
                    "dataType": "anat",
                    "modalityLabel": "INV2",
                    "criteria": {"SeriesNumber": int(check_results[bids_run][0][-4:])}
                    }
            else:
                if bids_run[-1].isdigit():
                    customLabels = "task-"+bids_run[:-1]+"_run-"+bids_run[-1]
                    TaskName = bids_run[:-1]
                else:
                    customLabels = "task-"+bids_run
                    TaskName = bids_run
                run_dict = {
                    "dataType": "func",
                    "modalityLabel": "bold",
                    "customLabels": customLabels,
                    "criteria": {"SeriesNumber": int(check_results[bids_run][0][-4:])},
                    "sidecarChanges": {"TaskName": TaskName}
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
    return 




################################ Prep 이후 denosing ###################################
# load (prep) confound
def load_confounds(Project, sub, runname, ses=None):
    info = get_full_info(Project)
    bids_path = info['bids_path']
    sub = "sub-"+sub
    task = "_task-"+runname
    sub_path = os.path.join(bids_path, "derivatives", sub)
    if ses == None: ses = ""
    else: 
        sub_path = os.path.join(sub_path, "ses-"+ses)
        ses = "_ses-" + ses
    sub_path = os.path.join(sub_path, "func")
    tsv_name = sub+ses+task+"_desc-confounds_timeseries.tsv"
    
    confounds= os.path.join(sub_path, tsv_name)
    
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
def DN(Project, sub, runname, ses=None):
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
    file_path = glob.glob(file_path)[0]
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
    fmri_clean = clean_data(fmri_data, fmri_compounds)
    ffmri_clean = fmri_clean.astype(np.float32)
    new_image = np.zeros(mni_mask.shape+(fmri_data.shape[0],), dtype=np.float32)
    new_image[mni_mask==1,:] = fmri_clean.T

    # save
    save_path = file_path.split("_space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz")[0]+".nii.gz"
    nib.save(nib.Nifti1Image(new_image, mni_image.affine),save_path)
    print("\n")
    print("---------------------------------------------------------------------")
    print(os.path.basename(file_path).split("_space")[0]+" denosing finished")
    print("---------------------------------------------------------------------")

    return 

# save motion & FD checking
def save_motion(Project, sub, ses=None):
    import matplotlib.pyplot as plt

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
        file_path = glob.glob(os.path.join(func_path, "*"+name+"*confounds_timeseries.tsv"))
        if len(file_path)>0: files.append(file_path[0])
        

    # plot
    plt.figure(figsize=(20,2.5*len(files)))
    plt.subplots_adjust(hspace=0.5)
    for file, i in zip(files, range(len(files))):
        task = file.split("task-")[1].split("_desc")[0]
        print(task)
        motions = pd.read_csv(file, sep="\t")
        pars = np.array(motions[['trans_x', 'trans_y', 'trans_z', 'rot_x', 'rot_y', 'rot_z']])
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
        if np.mean(fd>0.5) < 0.05: # FD>0.5인 구간이 5% 미만
            good_sub_path = __file__
            good_sub_path = os.path.abspath(os.path.join(good_sub_path, "..", ".."))
            good_sub_path = os.path.join(good_sub_path, "_data_Project", Project, "good_sub.json")
            if ses == None: ses_index = 0
            else: ses_index = int(ses)-1

            try:
                with open(good_sub_path) as f:
                    good_sub = json.load(f)
                if ses == None: ses_index = 0
                else: ses_index = int(ses)-1
                if task in good_sub[ses_index].keys():
                    if sub not in good_sub[ses_index][task]: good_sub[ses_index][task].append(sub)
                else:
                    good_sub[ses_index][task] = [sub]
                f.close()
            except:
                good_sub = []
                for n in range(ses_index+1): good_sub.append({})
                good_sub[ses_index][task] = [sub]
            with open(good_sub_path, "w", encoding="utf-8") as f:
                json.dump(good_sub, f, indent=4)
            f.close()

        # save plot
        plt.subplot(len(files), 3, 1+3*i)
        plt.plot(pars[:,:3])
        plt.ylabel("Trans (mm)")
        plt.legend(['x','y','z'])
        plt.ylim([-1,1])
        plt.subplot(len(files), 3, 2+3*i)
        plt.plot(pars[:,3:])
        plt.title(task+" (outlier ratio: "+str(np.round(np.mean(fd>0.5),3))+")")
        plt.ylabel("Rot (radian)")
        plt.legend(['x','y','z'])
        plt.ylim([-0.04,0.04])
        plt.subplot(len(files), 3, 3+3*i)
        plt.plot(fd, color='k')
        plt.text(np.argmax(fd), np.max(fd+0.03), str(np.round(np.max(fd),2)), 
            horizontalalignment='center')
        plt.ylim([0,1])
        plt.axhline(y=0.5, color='r', linestyle = "--", linewidth=2)
        plt.ylabel("FD")
    # save
    if ses == None:
        fig_path = os.path.join(fig_path, "sub-"+sub+"_motion.png")
    else:
        fig_path = os.path.join(fig_path, "sub-"+sub+"_ses-"+ses+"_motion.png")
       
    plt.savefig(fig_path, dpi=200)
    print("---------------------------------------------------------------------")
    print("sub-"+sub+" motion plot is saved")
    print("---------------------------------------------------------------------")

    return()



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
    if vox == 2: FWHM = 3
    if vox == 2.5: FWHM = 4
    if vox == 3: FWHM = 5
    sp.call(f'3dmerge -quiet -1blur_fwhm {FWHM} -doall -prefix {SM_HP_fname} {HP_fname}', shell=True)
    sp.call(f"cp {SM_HP_fname} {final_fname}", shell=True)
    print("---------------------------------------------------------------------")
    print(print_name+" smoothing finished")
    print("---------------------------------------------------------------------")
    
    
    
##################################### 7T #####################################
def SDC(Project, ima_path, sub, ses=None, gre_name="*GRE*", replace=True):
    from Speech.tools import isWSL
    if not isWSL(): return("Change WSL")
    
    # 정보 경로
    json_path = os.path.dirname(__file__)
    json_path = os.path.join(json_path, 'SDC', Project+".json")
    with open(json_path) as f: project_info = json.load(f)
    
    # raw 데이터 저장 경로
    raw_path = project_info["raw_path"]
    if ses == None:
        raw_path = os.path.join(raw_path, "sub-"+sub, "func")
    else:
        raw_path = os.path.join(raw_path, "sub-"+sub, "ses-"+ses, "func")
    
    # bids format 저장 경로
    bids_path = project_info["bids_path"]
    if ses == None:
        bids_path = os.path.join(bids_path, "sub-"+sub, "func")
    else:
        bids_path = os.path.join(bids_path, "sub-"+sub, "ses-"+ses, "func")
    
    # 파일 가져오기    
    if not os.path.isdir(os.path.join(project_info["raw_path"], "sub-"+sub)):
        copy = os.path.join(project_info["bids_path"], "sub-"+sub) 
        target = os.path.join(project_info["raw_path"], "sub-"+sub)
        sp.call(f"cp -r {copy} {target}", shell=True)
        
    
      
    # e.nii, e_ph.nii 만들기 
    print("---------------------------------------------------------------------")
    print("Making e.nii, e_ph.nii")
    print("---------------------------------------------------------------------")
    while len(glob.glob(os.path.join(ima_path,gre_name))) != 2: 
        ima_path = os.path.join(ima_path, "*")

    for folder in glob.glob(os.path.join(ima_path,gre_name)):
        sp.call(f"dcm2niix {folder}", shell=True) 
        nii_files = glob.glob(os.path.join(folder, "*.nii"))
        for filename in nii_files:
            if "e1.nii" in filename:
                target_path = os.path.join(raw_path, "e1.nii")
                sp.call(f"mv {filename} {target_path}", shell=True)
            elif "e2.nii" in filename:
                target_path = os.path.join(raw_path, "e2.nii")
                sp.call(f"mv {filename} {target_path}", shell=True)
            elif "e1_ph.nii" in filename:
                target_path = os.path.join(raw_path, "e1_ph.nii")
                sp.call(f"mv {filename} {target_path}", shell=True)
            elif "e2_ph.nii" in filename:
                target_path = os.path.join(raw_path, "e2_ph.nii")
                sp.call(f"mv {filename} {target_path}", shell=True)
    
    
    # sdc 돌리기
    print("---------------------------------------------------------------------")
    print("SDC")
    print("---------------------------------------------------------------------")
    
    vox_size = project_info['vox_size']
    EPI_x = project_info['EPI_x']
    EPI_y = project_info['EPI_y']
    EPI_z = project_info['EPI_z']
    ref_x = project_info['ref_x']
    ref_y = project_info['ref_y']
    ref_z = project_info['ref_z']
    PAT = project_info['PAT']
    dwell = project_info['dwell']
    dTE = project_info['dTE']

    sdc_script = os.path.join(os.path.dirname(__file__), "SDC/SDC.m")
    os.chdir(raw_path)
    sp.call(f"cd {raw_path}", shell=True)
    sp.call(f"cp -r {sdc_script} ./", shell=True)
    sp.call(f'matlab -nodesktop -nodisplay -r "SDC({vox_size}, {EPI_x}, {EPI_y}, {EPI_z}, {ref_x}, {ref_y}, {ref_z}, {PAT}, {dwell}, {dTE}); quit"',
            shell=True)
    
    # 파일 대체 
    if replace:
        print("---------------------------------------------------------------------")
        print("Replace epi to SDC corrected")
        print("---------------------------------------------------------------------")
        sdc_files = glob.glob("./*_SDC.nii.gz")
        for sdc_path in sdc_files:
            sdc_name = os.path.basename(sdc_path)
            new_name = sdc_path.split("_SDC.nii.gz")[0]+"_bold.nii.gz"
            new_path = os.path.join(bids_path, new_name)
            sp.call(f'\cp {sdc_path} {new_path}', shell=True)
    return("SDC Finished")


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