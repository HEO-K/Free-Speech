################# 3T dcm2bids #######################
mri=3T
project=MRIting
input=압축_푼_ima폴더
sub=0302
ses=2
script_path=/Free-Speech/Speech/Preprocessing
python ${script_path}/dcm2bids_all.py ${project} ${input} ${sub} --ses ${ses}




################# 7T dcm2bids #######################
# /usr/local/MATLAB/R2021b/bin/activate_matlab.sh
mri=7T
project=MRIting
input=압축_푼_ima폴더
sub=0302
ses=1
script_path=/Free-Speech/Speech/Preprocessing
python ${script_path}/dcm2bids_all.py ${project} ${input} ${sub} --ses ${ses}
if [ $mri = 7T ]
then
    python /Free-Speech/MRIting/7T.py ${project} ${input} ${sub} --ses ${ses}
fi


################# fMRIprep #######################
subs="0302"
bids_path=/Free-Speech/MRIting/_DATA_fMRI

for sub in $subs
do
fmriprep-docker ${bids_path} ${bids_path}/derivatives participant --participant-label ${sub}  --fs-license-file ~/freesurfer/license.txt --skip_bids_validation --ignore slicetiming
done



################# after prep ######################
subs="0302"
project=MRIting
script_path=/Free-Speech/Speech/Preprocessing
ses=1
for sub in $subs
do
python ${script_path}/afterprep_all.py ${project} ${sub} --ses ${ses}
done

ses=2
for sub in $subs
do
python ${script_path}/afterprep_all.py ${project} ${sub} --ses ${ses}
done

