# check sub & ima folder
sub=0501
ses1_input=/mnt/c/Users/Kwon/Downloads/20230314_MRITING_KSM_KSM
ses2_input=/mnt/c/Users/Kwon/Downloads/20230315_MRITING_KSM_KSM/


# other param
project=MRIting
script_path=Free-Speech/Speech/Preprocessing
bids_path=Free-Speech/MRIting/_DATA_fMRI


#### dcm2bids
# session 1
python ${script_path}/dcm2bids_all.py ${project} ${ses1_input} ${sub} --ses 1

# session 2
python ${script_path}/dcm2bids_all.py ${project} ${ses2_input} ${sub} --ses 2



#### fmriprep
subs="0501 0502"
for sub in $subs
do
fmriprep-docker ${bids_path} ${bids_path}/derivatives participant --participant-label ${sub} --fs-license-file ~/freesurfer/license.txt 
done
