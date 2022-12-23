function [ img_grappa, mask, mask_acs ] = caipi_2d( kspace_sampled, kspace_acs, Rtot, Rz, c_del, acs_size, kernel_size, lambda_tik, subs )
%GRAPPA_1D Summarz of this function goes here
%   Detailed explanation goes here

if nargin < 7
    kernel_size = [3,3];
end

if nargin < 8
    lambda_tik = eps;
end

if nargin < 9
    subs = 1;
end

[N(1), N(2), num_chan] = size(kspace_sampled);


% sampling masks
Ry = Rtot/Rz;

Npad = ceil(N / Rtot) * Rtot;

mcaipi = zeros(Npad);
mcaipi(1:Ry:end,1:Rz:end) = 1; 


caipi_delz = zeros(Npad(1),1);

for cnt = 1:Npad/Rtot
    idx = 0;
    for kz = 1:Ry:Rtot
        mcaipi( kz + (cnt-1) * Rtot, : ) = circshift( mcaipi( kz + (cnt-1) * Rtot, : ), [0,c_del*idx] );

        caipi_delz( kz + (cnt-1) * Rtot ) = c_del * idx;  
        
        idx = idx + 1;        
    end    
end

mcaipi = mcaipi(1:N(1),1:N(2));

caipi_delz = caipi_delz(1:N(1));




num_acsX = acs_size(1);                % acs size
num_acsY = acs_size(2);                % acs size
 

% acs masks
mask_acs = zeros(N);
mask_acs(1+end/2-num_acsX/2:end/2+num_acsX/2 + 1, 1+end/2-num_acsY/2:end/2+num_acsY/2 + 1) = 1;


Apad = ceil(acs_size / Rtot) * Rtot;

acaipi = zeros(Apad);
acaipi(1:Ry:end,1:Rz:end) = 1; 


acs_delz = zeros(Apad(1),1);

for cnt = 1:Apad/Rtot
    idx = 0;
    for kz = 1:Ry:Rtot
        acaipi( kz + (cnt-1) * Rtot, : ) = circshift( acaipi( kz + (cnt-1) * Rtot, : ), [0,c_del*idx] );

        acs_delz( kz + (cnt-1) * Rtot ) = c_del * idx;  
        
        idx = idx + 1;        
    end    
end

acaipi = acaipi(1:acs_size(1)+1,1:acs_size(2)+1);

acs_delz = acs_delz(1:acs_size(1)+1);








kernel_hsize = (kernel_size-1)/2;

pad_size = kernel_hsize .* [Ry,Rz];


% make sure zero padding size is multiple of total accl factor to preserve
% caipi pattern in recon:

scl = 1;

while 1
    if Rtot > max(pad_size)
        pad_size = [Rtot, Rtot] * scl;
        scl = scl + 1;
    else
        break
    end
end

pad_size

N_pad = N + 2*pad_size;


% k-space limits for training:
kz_begin = 1 + pad_size(2);       % first kernel center point that fits acs region 
kz_end = num_acsY - pad_size(2) + 1;   % last kernel center point that fits acs region 
% kz_end = kz_end - max(caipi_delz);

ky_begin = 1 + pad_size(1);            % first kernel center point that fits acs region 
ky_end = num_acsX - pad_size(1) + 1;           % last kernel center point that fits acs region 
 

% k-space limits for recon:
Kz_begin = 1 + pad_size(2);       % first kernel center point that fits acs region 
Kz_end = N_pad(2) - pad_size(2);      % last kernel center point that fits acs region 

Ky_begin = 1 + pad_size(1);            % first kernel center point that fits acs region 
Ky_end = N_pad(1) - pad_size(1);           % last kernel center point that fits acs region 



% count the no of kernels that fit in acs 
ind = 1;

for kz = kz_begin :Rtot: kz_end
    for ky = ky_begin :Rtot: ky_end
        ind = ind + 1;        
    end
end

num_ind = ind;
     

kspace_acs_crop = kspace_acs(1+end/2-num_acsX/2:end/2+num_acsX/2 + 1, 1+end/2-num_acsY/2:end/2+num_acsY/2 + 1, :);


Rhs = zeros([num_ind, num_chan, Ry*Rz-1]);
Acs = zeros([num_ind, prod(kernel_size) * num_chan]);

disp(['ACS mtx size: ', num2str(size(Acs))])


ind = 1;

for kz = kz_begin : Rtot: kz_end
    for ky = ky_begin :Rtot: ky_end

        acs = zeros([kernel_size, num_chan]);
        
        y_idx = 1;
        
        for y = ky-kernel_hsize(1)*Ry:Ry:ky+kernel_hsize(1)*Ry
        
            acs(y_idx,:,:) = kspace_acs_crop(y, acs_delz(y) + kz-kernel_hsize(2)*Rz : Rz : acs_delz(y) + kz+kernel_hsize(2)*Rz, :);
            y_idx = y_idx + 1;

        end

        Acs(ind,:) = acs(:);

        idx = 1;
        for rz = 1:Rz-1
            Rhs(ind,:,idx) = kspace_acs_crop(ky, acs_delz(ky) + kz-rz, :);
            idx = idx + 1;
        end    

        for ry = 1:Ry-1
            for rz = 0:Rz-1
                Rhs(ind,:,idx) = kspace_acs_crop(ky-ry, acs_delz(ky) + kz-rz, :);
                idx = idx + 1;
            end    
        end
        
        ind = ind + 1;
    end
end


if lambda_tik
    [u,s,v] = svd(Acs, 'econ');

    s_inv = diag(s); 
    
    disp(['condition number: ', num2str(max(abs(s_inv)) / min(abs(s_inv)))])
    
    s_inv = conj(s_inv) ./ (abs(s_inv).^2 + lambda_tik);

    Acs_inv = v * diag(s_inv) * u';
end


% estimate kernel weights

weights = zeros([prod(kernel_size) * num_chan, num_chan, Rz-1]);

for r = 1:Ry*Rz-1
    disp(['Kernel group : ', num2str(r)])

    for c = 1:num_chan

        if ~lambda_tik
            weights(:,c,r) = Acs \ Rhs(:,c,r);
        else
            weights(:,c,r) = Acs_inv * Rhs(:,c,r);
        end

    end
end



% recon undersampled data

Weights = permute(weights, [2,1,3]);

kspace_recon = padarray(kspace_sampled, [pad_size, 0]);

caipi_delz = padarray( caipi_delz, pad_size(1) );


for kz = Kz_begin : Rz : Kz_end
    for ky = Ky_begin : Ry : Ky_end

        
        data = zeros( [kernel_size, num_chan] );
        
        yidx = 1;
        
        for y = ky-kernel_hsize(1)*Ry : Ry : ky+kernel_hsize(1)*Ry
            
            data(yidx,:,:) = kspace_recon(y, kz-kernel_hsize(2)*Rz + caipi_delz(y) : Rz : kz+kernel_hsize(2)*Rz + caipi_delz(y), :);                
 
            yidx = yidx + 1;
            
        end        
        
        
        idx = 1;
        for rz = 1:Rz-1
            kspace_recon(ky, caipi_delz(ky) + kz-rz, :) = Weights(:, :, idx) * data(:);
            idx = idx + 1;
        end    

        for ry = 1:Ry-1
            for rz = 0:Rz-1
                kspace_recon(ky-ry, caipi_delz(ky) + kz-rz, :) = Weights(:, :, idx) * data(:);
                idx = idx + 1;
            end    
        end
        
    end
end

kspace_recon = kspace_recon(1+pad_size(1):end-pad_size(1), 1+pad_size(2):end-pad_size(2), :);

if subs
    % subsititute sampled & acs data
    kspace_recon = kspace_recon .* repmat((~mcaipi & ~mask_acs), [1,1,num_chan]) + kspace_sampled .* repmat(~mask_acs, [1,1,num_chan]) + kspace_acs;
end

img_grappa = ifft2c(kspace_recon);
 
  

end

