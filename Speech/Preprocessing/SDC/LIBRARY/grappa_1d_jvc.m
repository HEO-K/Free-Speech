function [ img_grappa, mask, mask_acs ] = grappa_1d_jvc( kspace_sampled, kspace_acs, Ry, acs_size, kernel_size, lambda_tik, subs, del )
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


[N(1), N(2), num_chan] = size(kspace_sampled);

if nargin < 8
    % k-space sampling offset of each coil
    del = zeros([1,num_chan]);
end

num_acsX = acs_size(1);                % acs size
num_acsY = acs_size(2);                % acs size
 

% sampling and acs masks
mask_acs = zeros([N, num_chan]);
mask_acs(1+end/2-num_acsX/2:end/2+num_acsX/2, 1+end/2-num_acsY/2:end/2+num_acsY/2 + 1, :) = 1;

mask = zeros([N, num_chan]);
for c = 1:num_chan
    mask(:,del(c)+1:Ry:end,c) = 1;
end


kernel_hsize = (kernel_size-1)/2;

pad_size = kernel_hsize .* [1,Ry];
N_pad = N + 2*pad_size;


% k-space limits for training:
ky_begin = 1 + Ry * kernel_hsize(2);       % first kernel center point that fits acs region 
ky_end = num_acsY - Ry * kernel_hsize(2) + 1;   % last kernel center point that fits acs region 
ky_end = ky_end - max(del);

kx_begin = 1 + kernel_hsize(1);            % first kernel center point that fits acs region 
kx_end = num_acsX - kernel_hsize(1);           % last kernel center point that fits acs region 
 

% k-space limits for recon:
Ky_begin = 1 + Ry * kernel_hsize(2);       % first kernel center point that fits acs region 
Ky_end = N_pad(2) - Ry * kernel_hsize(2);      % last kernel center point that fits acs region 
Ky_end = Ky_end - max(del);

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


Rhs = zeros([num_ind, num_chan, Ry-1]);
acs = zeros([kernel_size, num_chan]);
Acs = zeros([num_ind, prod(kernel_size) * num_chan]);

disp(['ACS mtx size: ', num2str(size(Acs))])


ind = 1;

for ky = ky_begin : ky_end
    for kx = kx_begin : kx_end

        for c = 1:num_chan
            acs(:,:,c) = kspace_acs_crop(kx-kernel_hsize(1):kx+kernel_hsize(1), del(c)+ky-kernel_hsize(2)*Ry : Ry : del(c)+ky+kernel_hsize(2)*Ry, c);
        end
        
        Acs(ind,:) = acs(:);

        for ry = 1:Ry-1
            for c = 1:num_chan
                Rhs(ind,c,ry) = kspace_acs_crop(kx, del(c)+ky-ry, c);
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

weights = zeros([prod(kernel_size) * num_chan, num_chan, Ry-1]);

for r = 1:Ry-1
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
data = zeros([kernel_size, num_chan]);


for ky = Ky_begin : Ry : Ky_end
    for kx = Kx_begin : Kx_end

        for c = 1:num_chan
            data(:,:,c) = kspace_recon(kx-kernel_hsize(1):kx+kernel_hsize(1), del(c)+ky-kernel_hsize(2)*Ry : Ry : del(c)+ky+kernel_hsize(2)*Ry, c);         
        end
        
        for ry = 1:Ry-1
            Wdata = Weights(:,:,ry) * data(:);
            
            for c = 1:num_chan
                kspace_recon(kx, del(c)+ky-ry, c) = Wdata(c);
            end
        end
        
    end
end

kspace_recon = kspace_recon(1+pad_size(1):end-pad_size(1), 1+pad_size(2):end-pad_size(2), :);

if subs
    % subsititute sampled & acs data
    kspace_recon = kspace_recon .* (~mask & ~mask_acs) + kspace_sampled .* (~mask_acs) + kspace_acs;
end

img_grappa = ifft2c(kspace_recon);
 

end

