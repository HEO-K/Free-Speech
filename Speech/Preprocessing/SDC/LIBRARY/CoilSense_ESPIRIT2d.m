function sens = CoilSense_ESPIRIT2d(img_3d, c, num_acs, data_path)
% this function is for multi-slice data, and loops over slices to estimate
% sensitivities in 2d


if nargin < 2
    c = 0.5;
end

if nargin < 3
    num_acs = 16;
end

if nargin < 4
    data_path = pwd;
end

% img_3d: x,y,slice,chan
% data_path : path you want to write data
% sens : final coil sens output including all slices

ImSize = size(img_3d);
% code only work if matrix is even in size so mod matrix if it is odd

if rem(ImSize(1),2) == 1 
    img_3d = cat(1,img_3d,zeros(1,ImSize(2),ImSize(3),ImSize(4)));
end

if rem(ImSize(2),2) == 1
    ImSizeCurrent = size(img_3d);
    img_3d = cat(2,img_3d,zeros(ImSizeCurrent(1),1,ImSizeCurrent(3),ImSizeCurrent(4)));
end


sens = zeros(size(img_3d));

addpath(genpath('/autofs/space/spinlock_001/users/kawin/berkin/Matlab_Code/LIBRARY/'))
% addpath(genpath('/autofs/cluster/kawin/Congyu/CODE/MRF/code_managed/nufft/tools/'))

add_bart2     % function to add bart to path
tic
for s = 1:size(img_3d,3)

    slice = img_3d(:,:,s,:);
  
    writecfl([data_path, 'img'], single(slice))

    system(['fft 3 ', data_path, 'img ', data_path, 'kspace'])

    system(['ecalib -c ', num2str(c), ' -r ', num2str(num_acs), ' ', data_path, 'kspace ', data_path, 'calib'])

    system(['slice 4 0 ', data_path, 'calib ', data_path, 'sens_slice'])
    
    sens_slice = single(readcfl([data_path, 'sens_slice']));
    
    sens(:,:,s,:) = sens_slice;
    
end
toc


system(['rm ', data_path, 'img.cfl'])
system(['rm ', data_path, 'img.hdr'])

system(['rm ', data_path, 'kspace.cfl'])
system(['rm ', data_path, 'kspace.hdr'])

system(['rm ', data_path, 'calib.cfl'])
system(['rm ', data_path, 'calib.hdr'])


if rem(ImSize(1),2) == 1
    sens = sens(1:end-1,:,:,:);
end

if rem(ImSize(2),2) == 1
    sens = sens(:,1:end-1,:,:);
end



end

