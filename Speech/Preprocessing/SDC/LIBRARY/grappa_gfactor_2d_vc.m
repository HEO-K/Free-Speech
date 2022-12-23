function [ img_grappa, mask, mask_acs, image_weights, g_fnl ] = grappa_gfactor_2d_vc( kspace_sampled, kspace_acs, Rx, Ry, acs_size, kernel_size, lambda_tik )
%GRAPPA_1D Summary of this function goes here
%   Detailed explanation goes here

if nargin < 6
    kernel_size = [3,3];
end

if nargin < 7
    lambda_tik = eps;
end
 
image_weights = 1;
g_fnl = 1;

[N(1), N(2), num_vc] = size(kspace_sampled);

num_chan = num_vc / 2;


% the amount of k-space voxel shift due to virtual coil:
shiftX_amount = mod(N(1), Rx);
shiftY_amount = mod(N(2), Ry);


num_acsX = acs_size(1);                % acs size
num_acsY = acs_size(2);                % acs size
 

% sampling and acs masks
mask = zeros(N);
mask_acs = zeros(N);

mask(1:Rx:end,1:Ry:end) = 1;
mask_acs(1+end/2-num_acsX/2:end/2+num_acsX/2 + 1, 1+end/2-num_acsY/2:end/2+num_acsY/2 + 1) = 1;


kernel_hsize = (kernel_size-1)/2;

pad_size = kernel_hsize .* [Rx,Ry];
N_pad = N + 2*pad_size;


% k-space limits for training:
ky_begin = 1 + Ry * kernel_hsize(2);       % first kernel center point that fits acs region 
ky_end = num_acsY - Ry * kernel_hsize(2) + 1;   % last kernel center point that fits acs region 

ky_end = ky_end - shiftY_amount;


kx_begin = 1 + Rx * kernel_hsize(1);            % first kernel center point that fits acs region 
kx_end = num_acsX - Rx * kernel_hsize(1) + 1;           % last kernel center point that fits acs region 

kx_end = kx_end - shiftX_amount;
 

% k-space limits for recon:
Ky_begin = 1 + Ry * kernel_hsize(2);       % first kernel center point that fits acs region 
Ky_end = N_pad(2) - Ry * kernel_hsize(2);      % last kernel center point that fits acs region 

Ky_end = Ky_end - shiftY_amount;


Kx_begin = 1 + Rx * kernel_hsize(1);            % first kernel center point that fits acs region 
Kx_end = N_pad(1) - Rx * kernel_hsize(1);           % last kernel center point that fits acs region 

Kx_end = Kx_end - shiftX_amount;



% count the no of kernels that fit in acs 
ind = 1;

for ky = ky_begin : ky_end
    for kx = kx_begin : kx_end
        ind = ind + 1;        
    end
end

num_ind = ind;
     

kspace_acs_crop = kspace_acs(1+end/2-num_acsX/2:end/2+num_acsX/2 + 1, 1+end/2-num_acsY/2:end/2+num_acsY/2 + 1, :);


Rhs = zeros([num_ind, num_chan * 1, Rx*Ry-1]);


Acs = zeros([num_ind, prod(kernel_size) * num_chan * 2]);

disp(['ACS mtx size: ', num2str(size(Acs))])


ind = 1;

for ky = ky_begin : ky_end
    for kx = kx_begin : kx_end
          
        acs = kspace_acs_crop(kx-kernel_hsize(1)*Rx:Rx:kx+kernel_hsize(1)*Rx, ky-kernel_hsize(2)*Ry:Ry:ky+kernel_hsize(2)*Ry, 1:num_chan);

        acs = cat(3, acs, kspace_acs_crop(shiftX_amount + kx-kernel_hsize(1)*Rx:Rx: shiftX_amount + kx+kernel_hsize(1)*Rx, ...
            shiftY_amount + ky-kernel_hsize(2)*Ry:Ry: shiftY_amount + ky+kernel_hsize(2)*Ry, 1+num_chan:end));

        Acs(ind,:) = acs(:);

        idx = 1;
        for ry = 1:Ry-1
            Rhs(ind,:,idx) = kspace_acs_crop(kx, ky-ry, 1:num_chan);
            
            idx = idx + 1;
        end    

        for rx = 1:Rx-1
            for ry = 0:Ry-1
                Rhs(ind,:,idx) = kspace_acs_crop(kx-rx, ky-ry, 1:num_chan);
                                
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

weights = zeros([prod(kernel_size) * num_chan * 2, num_chan, Rx*Ry-1]);

for r = 1:Rx*Ry-1
    disp(['Kernel group : ', num2str(r)])

    for c = 1:num_chan * 1

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
    for kx = Kx_begin : Rx : Kx_end
        
        data = kspace_recon(kx-kernel_hsize(1)*Rx:Rx:kx+kernel_hsize(1)*Rx, ky-kernel_hsize(2)*Ry:Ry:ky+kernel_hsize(2)*Ry, 1:num_chan);                
        data = cat(3, data, kspace_recon( shiftX_amount + kx-kernel_hsize(1)*Rx:Rx: shiftX_amount + kx+kernel_hsize(1)*Rx, shiftY_amount + ky-kernel_hsize(2)*Ry:Ry: shiftY_amount + ky+kernel_hsize(2)*Ry, 1+num_chan:end));                

        
        idx = 1;
        for ry = 1:Ry-1
            kspace_recon(kx, ky-ry, 1:num_chan) = Weights(:, :, idx) * data(:);
            idx = idx + 1;
        end    

        for rx = 1:Rx-1
            for ry = 0:Ry-1
                kspace_recon(kx-rx, ky-ry, 1:num_chan) = Weights(:, :, idx) * data(:);
                idx = idx + 1;
            end    
        end
        

    end
end

kspace_recon = kspace_recon(1+pad_size(1):end-pad_size(1), 1+pad_size(2):end-pad_size(2), 1:num_chan);


img_grappa = ifft2c(kspace_recon);
 



% 
% 
% % image space grappa weights
% 
% image_weights = zeros([N, num_chan*2, num_chan*2]);
%  
%             
% for c = 1:num_chan * 2
% 
%     idx = 1; 
%     
%     image_weights(1+end/2, 1+end/2, c, c) = 1;
% 
%     for ry = 1:Ry-1
%         
%         w = weights(:, c, idx);
% 
%         W = reshape(w, [kernel_size, num_chan*2]);
% 
%         image_weights(1+end/2 - kernel_hsize(1)*Rx :Rx: 1+end/2 + kernel_hsize(1)*Rx, ry + 1+end/2 - kernel_hsize(2)*Ry :Ry: ry + 1+end/2 + kernel_hsize(2)*Ry, 1:num_chan, c) = W(:,:,1:num_chan);
% 
%         
%         image_weights( shiftX_amount + 1+end/2 - kernel_hsize(1)*Rx :Rx: shiftX_amount + 1+end/2 + kernel_hsize(1)*Rx, ...
%             shiftY_amount + ry + 1+end/2 - kernel_hsize(2)*Ry :Ry: shiftY_amount + ry + 1+end/2 + kernel_hsize(2)*Ry, 1+num_chan:end, c) = W(:,:,1+num_chan:2*num_chan);
%         
%          
%         idx = idx + 1;
%         
%     end    
% 
%     for rx = 1:Rx-1
%         for ry = 0:Ry-1
%     
%             w = weights(:, c, idx);
% 
%             W = reshape(w, [kernel_size, num_chan*2]);
% 
%             image_weights(rx + 1+end/2 - kernel_hsize(1)*Rx :Rx: rx + 1+end/2 + kernel_hsize(1)*Rx, ry + 1+end/2 - kernel_hsize(2)*Ry :Ry: ry + 1+end/2 + kernel_hsize(2)*Ry, 1:num_chan, c) = W(:,:,1:num_chan);
%              
%             image_weights( shiftX_amount + rx + 1+end/2 - kernel_hsize(1)*Rx :Rx: shiftX_amount + rx + 1+end/2 + kernel_hsize(1)*Rx, ...
%                 shiftY_amount + ry + 1+end/2 - kernel_hsize(2)*Ry :Ry: shiftY_amount + ry + 1+end/2 + kernel_hsize(2)*Ry, 1+num_chan:end, c) = W(:,:,1+num_chan:2*num_chan);
% 
%             idx = idx + 1;
% 
%         end    
%     end
%     
% end
% 
% 
%  
% 
% image_weights = flipdim( flipdim( ifft2c2( image_weights ), 1 ), 2 ) * sqrt(prod(N));
% 
% 
% image_weights = image_weights(:,:,:,1:num_chan);
% 
% 
% 
% % Tukey window on acs image to create rsos coil combination weights
% 
% tw1 = tukeywin(acs_size(1));
% tw2 = tukeywin(acs_size(2));
% 
% 
% tw = repmat( padarray(tw1 * tw2', (N-acs_size)/2), [1,1,num_chan]);
% 
% 
% img_acs = ifft2c( kspace_acs(:,:,1:num_chan) .* tw );
% 
% 
% weights_p = conj(img_acs) ./ (eps + repmat(rsos(img_acs, 3), [1,1,num_chan]));
% 
%  
% 
% % coil combined g-factor 
% 
% img_weights = image_weights / (Ry * Rx);
% 
% 
% g_cmb = zeros([N, num_chan]);
% 
% for c = 1:num_chan*2
%     
%     weights_coil = squeeze( img_weights(:,:,c,:) );
%      
%     g_cmb(:,:,c) = sum(weights_p .* weights_coil, 3);
%     
% end
% 
% g_comb = sqrt( sum(g_cmb .* conj( g_cmb ), 3) );
% 
% p_comb = sqrt( sum(weights_p .* conj( weights_p ), 3) );
% 
% g_fnl = g_comb ./ p_comb;
%   

end

