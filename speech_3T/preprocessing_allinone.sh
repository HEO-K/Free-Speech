################# dcm2bids #######################
# 변수
input=/mnt/c/Users/Kwon/Downloads/HK_SPEECH_20221004KHY
project=speech_3T
sub=001
script_path=Speech/Preprocessing

# 실행
python ${script_path}/dcm2bids_all.py ${project} ${input} ${sub}



################# fMRIprep #######################
# 변수
subs="001"
bids_path=speech_3T/_DATA_fMRI

# 실행
for sub in $subs
do
fmriprep-docker ${bids_path} ${bids_path}/derivatives participant --participant-label ${sub}  --n_cpus 20 --fs-license-file ~/freesurfer/license.txt --skip_bids_validation
done



################# preprocess #####################
# 변수
subs="001"
project=speech_3T
script_path=Speech/Preprocessing

# 실행
for sub in $subs
do
python ${script_path}/afterprep_all.py ${project} ${sub}
done

