## for replace proc00_dcm2bids.sh
sub=$2
ses=$3
maindir=$1


## dcm2bids 
script_path=/sas2/PECON/7T/NatPAC/code/dcm2bids
python3 ${script_path}/run_dcm2bids.py ${sub} ${ses}


## chmod
cd ${maindir}/sub-${sub}
chmod -R 777 ses-${ses}