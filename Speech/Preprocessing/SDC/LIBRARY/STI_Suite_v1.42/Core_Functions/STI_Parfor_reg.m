function [X_tensor]=STI_Parfor_reg(Thetai, HVector, parallel_Flag, reg_Flag, tik)
% Wei Li, PhD
% Chunlei Liu, PHD
% Brain Imaging And Analysis Center, Duke Uiversity.

poolnum=1;
switch parallel_Flag
    case 'on'
        matlabpool local 3
        poolnum=3;
end

if nargin < 4
    reg_Flag = 1;       % Tikhonov reg
%     reg_Flag = 2;       % L2-gradient reg
%     reg_Flag = 3;       % backslash solution
end

if nargin < 5
    % Tikhonov regularization parameter
    tik = 1e-6;
end

tic
xres = size(Thetai,1);
yres = size(Thetai,2);
zres = size(Thetai,3);

maxres = length(Thetai);

Thetai = padarray(Thetai,[maxres-xres maxres-yres maxres-zres 0]/2);

SZ1 = maxres^3;
N_direction = size(Thetai,4);
thetai0 = zeros(SZ1,N_direction);

for n = 1:N_direction
    Xk0 = fftnc(Thetai(:,:,:,n));
    thetai0(:,n) = Xk0(:);
end

disp('data FFT_ed')
clear Xk0

H = HVector ./ repmat(sqrt(sum(HVector.^2,2)),[1,3]);
A1 = [H(:,1).^2  2*H(:,1).*H(:,2)  2*H(:,1).*H(:,3) H(:,2).^2 2*H(:,2).*H(:,3) H(:,3).^2]/3;
SS = [maxres maxres maxres];

[ry,rx,rz] = meshgrid(-SS(2)/2:SS(2)/2-1,-SS(1)/2:SS(1)/2-1,-SS(3)/2:SS(3)/2-1);
ki = [rx(:) ry(:) rz(:)];
clear rx ry rz
disp('ki constructed')

% Variable distributing
SamplingVector1 = (round((SZ1/poolnum)*(1:poolnum)))';
SamplingVector0 = [1; SamplingVector1(1:end-1)+1];

for n = 1:poolnum
    kipar{n} = ki(SamplingVector0(n):SamplingVector1(n),:);
    thetai0par{n} = thetai0(SamplingVector0(n):SamplingVector1(n),:);
end

clear ki thetai0
disp('Parallel variables created')

% Parfor loop
parfor loopvar = 1:poolnum
    warning off all
    xkipar{loopvar}=myparforfun(kipar{loopvar}, A1, H, thetai0par{loopvar}, loopvar, tik, SS, reg_Flag);
end
clear kipar

xki = [];
for n = 1:poolnum
    xki = [xki; xkipar{n}];
end
size(xki)

% Organize
xki = reshape(xki, [SS,6]);

xki(isnan(xki)) = 0;
xki(isinf(xki)) = 0;

for n = 1:6
    X_tensor(:,:,:,n) = ifftnc(xki(:,:,:,n));
end
disp('reconstruction done')

switch parallel_Flag
    case 'on'
     matlabpool close
end

end


function xki = myparforfun(ki, A1, H, thetai0, loopvar, tik, SS, reg_Flag)
SZ1 = size(ki,1);
tic
xki = zeros(SZ1,6);

for n = 1:SZ1
    k = ki(n,:);
    
    A2 = [k(1)*H(:,1) k(1)*H(:,2)+k(2)*H(:,1) k(1)*H(:,3)+k(3)*H(:,1) k(2)*H(:,2) k(2)*H(:,3)+k(3)*H(:,2) k(3)*H(:,3)];
    A = A1 - repmat(H*k',[1,6]).*A2/sum(k.^2);
    thetai = thetai0(n,:)';
    
    A(isinf(A)) = 0;
    A(isnan(A)) = 0;
    
    if reg_Flag == 1
        % Tikhonov regularization
        [U,S,V] = svd(A,'econ');
        Stik = S ./ (S.^2 + tik);
        xki(n,:) = (V * Stik * U' * thetai)';
    end
    
    if reg_Flag == 2
        % L2 gradient regularization
        fdx = 1 - exp(-2*pi*1i*k(1)/SS(1));
        fdy = 1 - exp(-2*pi*1i*k(2)/SS(2));
        fdz = 1 - exp(-2*pi*1i*k(3)/SS(3));

        Reg = tik * eye(6) * (abs(fdx).^2 + abs(fdy).^2 + abs(fdz).^2);

        xki(n,:) = ((A'*A + Reg + eps) \ (A'*thetai))';
    end
    
    if reg_Flag == 3
        % original recon
        xki(n,:) = (A\thetai)';
    end
    
    if ~mod(n,round(SZ1/20))
        disp([ num2str(loopvar) ': ' num2str(round(n/SZ1*100)) '% finished;   Remaining: ' num2str(round((1-n/SZ1)/(n/SZ1)*toc)) ' sec' ])
    end
end

end




