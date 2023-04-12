### 변수, 여기만 수정
sub=008
ses=pre02         # XXR, XXa... 도 가능


### 서버에 파일 업로드
# 로컬 *.zip파일을 /sas2/PECON/7T/NatPAC/sourcedata로
# 로컬에서 실행
# download_path=/mnt/c/Users/Kwon/Downloads
# scp ${download_path}/NATPAC_SUB-${sub}_SES-${ses^^}.zip  wonmokshim@115.145.185.185:/sas2/PECON/7T/NatPAC/sourcedata/


### dcm2bids 실행
python3 /sas2/PECON/7T/NatPAC/code/HK_dcm2bids/run_dcm2bids.py ${sub} ${ses}