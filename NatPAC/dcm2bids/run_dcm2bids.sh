### 변수, 여기만 수정
sub=007
ses=01
download_path=/mnt/c/Users/Kwon/Downloads


### 서버에 파일 업로드
# 로컬 *.zip파일을 /sas2/PECON/7T/NatPAC/sourcedata로
# 로컬에서 실행
# scp ${download_path}/NATPAC_SUB-{sub}_SES-{ses}.zip  wonmokshim@115.145.185.185:/sas2/PECON/7T/NatPAC/sourcedata/


### dcm2bids 실행
script_path=/sas2/PECON/7T/NatPAC/code/dcm2bids
python ${script_path}/run_dcm2bids.py ${sub} ${ses}



### 만약, 직접 만든 config파일로 돌리고 싶다: '### dcm2bids 실행' 대신 아래를 실행
# config_path = /your/config/path
# script_path=/sas2/PECON/7T/NatPAC/code/dcm2bids
# python ${script_path}/run_dcm2bids.py ${sub} ${ses} --custom_config ${config_path}
