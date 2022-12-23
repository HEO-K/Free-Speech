function [ img_jgrappa, mask, mask_acs ] = joint_grappa_1d_vc( kspace_sampled, kspace_acs, Ry, acs_size, kernel_size, Lambda_tik, del_step )
%GRAPPA_1D Summary of this function goes here
%   Detailed explanation goes here

if nargin < 5
    kernel_size = [5,3];
end

if nargin < 6
    Lambda_tik = eps;
end

if nargin < 7
    del_step = 1;
end

% set to 0 to disable VC
vc = 1;


[N(1), N(2), num_vc, num_echo] = size(kspace_sampled);

num_chan = num_vc / 2;

num_acsX = acs_size(1);                % acs size
num_acsY = acs_size(2);                % acs size
 
 
mask = zeros([N, num_echo]);
mask_vc = zeros([N, num_echo]);


mask_acs = zeros(N);
mask_acs(1+end/2-num_acsX/2:end/2+num_acsX/2, 1+end/2-num_acsY/2:end/2+num_acsY/2 + 1) = 1;


% create sampling patterns

del = mod((0:num_echo-1) * del_step, Ry)        % offset from the first echo in the actual coil

del_vc = zeros(1,num_echo);                     % offset from the first echo in the virtual coil


for t = 1:num_echo
    mask(:,1+del(t):Ry:end,t) = 1;
    
    mask_vc(:,:,t) = ifft2c(conj(fft2c(mask(:,:,t))));
    mask_vc(:,:,t) = abs(mask_vc(:,:,t)) > 1e-12;    
    
    mask_shift = mask_vc(:,:,t);
    res = sum(sum(abs(mask_shift - mask(:,:,1))));
    
    for r = 1:Ry-1
        mask_shift = circshift(mask_vc(:,:,t), [0,-r]);
        res_now = sum(sum(abs(mask_shift - mask(:,:,1))));
        
        if res_now < res
            res = res_now;
            del_vc(t) = r;
        end
    end
end

del_vc 


kernel_hsize = (kernel_size-1)/2;

pad_size = kernel_hsize .* [1,Ry];
N_pad = N + 2 * pad_size; 


% k-space limits for training:
ky_begin = 1 + Ry * kernel_hsize(2);        % first kernel center point that fits acs region 
ky_end = num_acsY - Ry * kernel_hsize(2) + 1;   % last kernel center point that fits acs region 
ky_end = ky_end - max([del, del_vc]);                 % make sure other cycles remain within acs


kx_begin = 1 + kernel_hsize(1);             % first kernel center point that fits acs region 
kx_end = num_acsX - kernel_hsize(1);        % last kernel center point that fits acs region 


% k-space limits for recon:
Ky_begin = 1 + Ry * kernel_hsize(2);       % first kernel center point that fits acs region 
Ky_end = N_pad(2) - Ry * kernel_hsize(2);      % last kernel center point that fits acs region 
Ky_end = Ky_end - max([del, del_vc]);                     % make sure data from other images remain in matrix size


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
 


% train kernel
kspace_acs_crop = kspace_acs(1+end/2-num_acsX/2:end/2+num_acsX/2, 1+end/2-num_acsY/2:end/2+num_acsY/2 + 1, :, :);




Rhs = zeros([num_ind, num_chan * (1+vc), Ry-1, num_echo]);
Acs = zeros([num_ind, prod(kernel_size) * num_chan * num_echo * (1+vc)]);

disp(size(Acs))
 

ind = 1;

for ky = ky_begin : ky_end
    for kx = kx_begin : kx_end

        acs = zeros( prod(kernel_size) * num_chan * num_echo * (1+vc), 1 );

        for ry = 0 : num_echo - 1

            tmp = kspace_acs_crop(kx-kernel_hsize(1):kx+kernel_hsize(1), del(ry+1) + ky-kernel_hsize(2)*Ry : Ry : del(ry+1) + ky+kernel_hsize(2)*Ry, 1:num_chan, ry + 1);

            if vc
                tmp = cat(3, tmp, kspace_acs_crop(kx-kernel_hsize(1):kx+kernel_hsize(1), del_vc(ry+1) + ky-kernel_hsize(2)*Ry : Ry : del_vc(ry+1) + ky+kernel_hsize(2)*Ry, 1+num_chan:end, ry + 1));
            end
            
            acs( 1 + prod(kernel_size) * num_chan * ry * (1+vc) : prod(kernel_size) * num_chan * (ry + 1) * (1+vc) ) = tmp(:);

        end

        Acs(ind,:) = acs;

        for phs_cyc = 1:num_echo
            for ry = 1:Ry-1
            
                Rhs(ind,1:num_chan,ry,phs_cyc) = kspace_acs_crop(kx, del(phs_cyc) + ky-ry, 1:num_chan, phs_cyc);
                
                if vc
                    Rhs(ind,1+num_chan:end,ry,phs_cyc) = kspace_acs_crop(kx, del_vc(phs_cyc) + ky-ry, 1+num_chan:end, phs_cyc);
                end
                
            end
        end 

        ind = ind + 1;

    end
end



if Lambda_tik
    [u,s,v] = svd(Acs, 'econ');

    s_inv = diag(s); 
    s_inv = conj(s_inv) ./ (abs(s_inv).^2 + Lambda_tik);

    Acs_inv = v * diag(s_inv) * u';
end
    

% estimate kernel weights
weights = zeros([prod(kernel_size) * num_chan * num_echo * (1+vc), num_chan * (1+vc), Ry-1, num_echo]);

for phs_cyc = 1:num_echo
    disp(['Phase cycle: ', num2str(phs_cyc)])

    for r = 1:Ry-1
        for c = 1:num_chan*(1+vc)

            if ~Lambda_tik
                weights(:,c,r,phs_cyc) = Acs \ Rhs(:,c,r,phs_cyc);
            else
                weights(:,c,r,phs_cyc) = Acs_inv * Rhs(:,c,r,phs_cyc);
            end
        end
    end
end


% recon undersampled data
Weights = permute(weights, [2,1,3,4]);

kspace_recon = padarray(kspace_sampled, [pad_size, 0, 0]);


for ky = Ky_begin : Ry : Ky_end
    for kx = Kx_begin : Kx_end

        data = zeros( prod(kernel_size) * num_chan * num_echo * (1+vc), 1 );

        for ry = 0:num_echo-1

            dt = kspace_recon(kx-kernel_hsize(1):kx+kernel_hsize(1), del(ry+1) + ky-kernel_hsize(2)*Ry : Ry : del(ry+1) + ky+kernel_hsize(2)*Ry, 1:num_chan, ry + 1);

            if vc
                dt = cat(3, dt, kspace_recon(kx-kernel_hsize(1):kx+kernel_hsize(1), del_vc(ry+1) + ky-kernel_hsize(2)*Ry : Ry : del_vc(ry+1) + ky+kernel_hsize(2)*Ry, 1+num_chan:end, ry + 1));
            end
            
            data( 1 + prod(kernel_size) * num_chan * ry * (1+vc) : prod(kernel_size) * num_chan * (ry + 1) * (1+vc) ) = dt(:);

        end

        for phs_cyc = 1:num_echo
            for ry = 1:Ry-1
                kspace_recon(kx, del(phs_cyc) + ky-ry, 1:num_chan, phs_cyc) = Weights(1:num_chan,:,ry,phs_cyc) * data(:);                 
            end
        end

    end
end


kspace_recon = kspace_recon(1+pad_size(1):end-pad_size(1), 1+pad_size(2):end-pad_size(2), 1:num_chan, :);


img_jgrappa = zeros(size(kspace_recon));

for phs_cyc = 1:num_echo
    img_jgrappa(:,:,:,phs_cyc) = ifft2c( kspace_recon(:,:,:,phs_cyc) );
end
 
  

end

