function [ img_grappa, mask, mask_acs ] = grappa_1d_virtual( kspace_sampled, kspace_acs, Ry, acs_size, kernel_size, lambda_tik, subs, virtual )
%GRAPPA_1D Summary of this function goes here
%   Detailed explanation goes here

if nargin < 5
    kernel_size = [5,3];
end

if nargin < 6
    lambda_tik = eps;
end

if nargin < 7
    subs = 1;
end

if nargin < 8
    virtual = 0;
end


[N(1), N(2), num_vc] = size(kspace_sampled);

num_chan = num_vc / (1+virtual);

% the amount of k-space voxel shift due to virtual coil:
shift_amount = mod(N(2), Ry) * virtual;

    
num_acsX = acs_size(1);                % acs size
num_acsY = acs_size(2);                % acs size
 

% sampling and acs masks
mask = zeros(N);
mask_acs = zeros(N);

mask(:,1:Ry:end) = 1;
mask_acs(1+end/2-num_acsX/2:end/2+num_acsX/2, 1+end/2-num_acsY/2:end/2+num_acsY/2 + 1) = 1;


kernel_hsize = (kernel_size-1)/2;

pad_size = kernel_hsize .* [1,Ry];
N_pad = N + 2*pad_size;


% k-space limits for training:
ky_begin = 1 + Ry * kernel_hsize(2);       % first kernel center point that fits acs region 
ky_end = num_acsY - Ry * kernel_hsize(2) + 1;   % last kernel center point that fits acs region 

if shift_amount > 0
    ky_end = ky_end - shift_amount;
else
    ky_begin = ky_begin - shift_amount;
end

kx_begin = 1 + kernel_hsize(1);            % first kernel center point that fits acs region 
kx_end = num_acsX - kernel_hsize(1);           % last kernel center point that fits acs region 
 

% k-space limits for recon:
Ky_begin = 1 + Ry * kernel_hsize(2);       % first kernel center point that fits acs region 
Ky_end = N_pad(2) - Ry * kernel_hsize(2);      % last kernel center point that fits acs region 

if shift_amount > 0
    Ky_end = Ky_end - shift_amount;
end


Kx_begin = 1 + kernel_hsize(1);            % first kernel center point that fits acs region 
Kx_end = N_pad(1) - kernel_hsize(1);           % last kernel center point that fits acs region 



% count the no of kernels that fit in acs 
ind = 1;

for ky = ky_begin : ky_end
    for kx = kx_begin : kx_end
        ind = ind + 1;        
    end
end

num_ind = ind;
     

kspace_acs_crop = kspace_acs(1+end/2-num_acsX/2:end/2+num_acsX/2, 1+end/2-num_acsY/2:end/2+num_acsY/2 + 1, :);


Rhs = zeros([num_ind, num_chan * (1+virtual), Ry-1]);
Acs = zeros([num_ind, prod(kernel_size) * num_chan * (1+virtual)]);

disp(['ACS mtx size: ', num2str(size(Acs))])


ind = 1;

for ky = ky_begin : ky_end
    for kx = kx_begin : kx_end

        acs = kspace_acs_crop(kx-kernel_hsize(1):kx+kernel_hsize(1), ky-kernel_hsize(2)*Ry:Ry:ky+kernel_hsize(2)*Ry, 1:num_chan);
        
        if virtual
            acs = cat(3, acs, kspace_acs_crop(kx-kernel_hsize(1):kx+kernel_hsize(1), shift_amount + ky-kernel_hsize(2)*Ry:Ry: shift_amount + ky+kernel_hsize(2)*Ry, 1+num_chan:end));
        end
        
        Acs(ind,:) = acs(:);

        for ry = 1:Ry-1
            Rhs(ind,1:num_chan,ry) = kspace_acs_crop(kx, ky-ry, 1:num_chan);
        
            if virtual
                Rhs(ind,1+num_chan:end,ry) = kspace_acs_crop(kx, shift_amount + ky-ry, 1+num_chan:end);
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

weights = zeros([prod(kernel_size) * num_chan * (1+virtual), num_chan * (1+virtual), Ry-1]);

for r = 1:Ry-1
    disp(['Kernel group : ', num2str(r)])

    for c = 1:num_chan * (1+virtual)

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


for ky = Ky_begin : Ry : Ky_end
    for kx = Kx_begin : Kx_end

        data = kspace_recon(kx-kernel_hsize(1):kx+kernel_hsize(1), ky-kernel_hsize(2)*Ry:Ry:ky+kernel_hsize(2)*Ry, 1:num_chan);                
        
        if virtual
            data = cat(3, data, kspace_recon(kx-kernel_hsize(1):kx+kernel_hsize(1), shift_amount + ky-kernel_hsize(2)*Ry:Ry: shift_amount + ky+kernel_hsize(2)*Ry, 1+num_chan:end));                
        end
        
        for ry = 1:Ry-1
             kspace_recon(kx, ky-ry, :) = Weights(:,:,ry) * data(:);
        end

    end
end

kspace_recon = kspace_recon(1+pad_size(1):end-pad_size(1), 1+pad_size(2):end-pad_size(2), :);


if subs
    % subsititute sampled & acs data
    kspace_recon = kspace_recon(:,:,1:num_chan) .* repmat((~mask & ~mask_acs), [1,1,num_chan]) + kspace_sampled .* repmat(~mask_acs, [1,1,num_chan]) + kspace_acs;
end

img_grappa = ifft2c(kspace_recon);
  

end

