function [X_tensor]=STI_Parfor(Thetai,HVector,parallel_Flag)
% Wei Li, PhD
% Chunlei Liu, PHD
% Brain Imaging And Analysis Center, Duke Uiversity.
poolnum=1;
switch parallel_Flag
    case 'on'
        matlabpool local 3
        poolnum=3;
end

tic
xres=size(Thetai,1);
yres=size(Thetai,2);
zres=size(Thetai,3);
Thetai=padarray(Thetai,[0 xres-yres xres-zres 0]/2);

SZ1=xres^3;
N_direction=size(Thetai,4);
thetai0=zeros(SZ1,N_direction);
for i=1:N_direction
    Xk0=fftnc(Thetai(:,:,:,i));
    thetai0(:,i)=Xk0(:);
end
disp('data FFT_ed')
clear Xk0
H=HVector./repmat(sqrt(sum(HVector.^2,2)),[1,3]);
A1 =[H(:,1).^2  2*H(:,1).*H(:,2)  2*H(:,1).*H(:,3) H(:,2).^2 2*H(:,2).*H(:,3) H(:,3).^2]/3;
SS=[xres xres xres];
[ry,rx,rz] = meshgrid(-SS(2)/2:SS(2)/2-1,-SS(1)/2:SS(1)/2-1,-SS(3)/2:SS(3)/2-1);
ki=[rx(:) ry(:) rz(:)];
clear rx ry rz
disp('ki constructed')
%% Variable distributing
SamplingVector1=(round((SZ1/poolnum)*(1:poolnum)))';
SamplingVector0=[1; SamplingVector1(1:end-1)+1];

for i=1:poolnum
kipar{i}=ki(SamplingVector0(i):SamplingVector1(i),:);
thetai0par{i}=thetai0(SamplingVector0(i):SamplingVector1(i),:);
end

clear ki thetai0
disp('Parallel variables created')

%% Parfor loop
parfor loopvar = 1:poolnum
    warning off all
    xkipar{loopvar}=myparforfun(kipar{loopvar},A1,H,thetai0par{loopvar},loopvar);
end
clear kipar

xki=[];
for i=1:poolnum
    xki=[xki; xkipar{i}];
end
size(xki)
%% Organize
xki=reshape(xki,[xres,xres,xres,6]);

xki(isnan(xki))=0;
for i=1:6
    X_tensor(:,:,:,i)=ifftnc(xki(:,:,:,i));
end
disp('reconstruction done')

switch parallel_Flag
    case 'on'
     matlabpool close
end
function xki=myparforfun(ki,A1,H,thetai0,loopvar)
SZ1=size(ki,1);
tic
xki=zeros(SZ1,6);
for i=1:SZ1
    k=ki(i,:);
    A2 =[k(1)*H(:,1) k(1)*H(:,2)+k(2)*H(:,1) k(1)*H(:,3)+k(3)*H(:,1) k(2)*H(:,2) k(2)*H(:,3)+k(3)*H(:,2) k(3)*H(:,3)];
    A=A1-repmat(H*k',[1,6]).*A2/sum(k.^2);
    thetai= thetai0(i,:)';
    
    A(isinf(A)) = 0;
    A(isnan(A)) = 0;
%     [U,S,V] = svd(A,'econ');
%     Stik = S ./ (S.^2 + 1e-3);
%     xki(i,:) = (V * Stik * U' * thetai)';
    
    xki(i,:)=(A\thetai)';
    if ~mod(i,round(SZ1/20))
        disp([ num2str(loopvar) ': ' num2str(round(i/SZ1*100)) '% finished;   Remaining: ' num2str(round((1-i/SZ1)/(i/SZ1)*toc)) ' sec' ])
    end
end




