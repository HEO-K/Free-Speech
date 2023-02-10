function SDC_su(vox_size, EPI_x, EPI_y, EPI_z, ref_x, ref_y, ref_z, PAT, dwell, dTE)

addpath(genpath("/mnt/d/Functions/Speech/Preprocessing/SDC/LIBRARY/"))
filename = dir('./*nii.gz');
setenv("PATH", [getenv("PATH") ':/root/fsl/share/fsl/bin/'])
%% Phase Normalize
t = load_untouch_nii('./e1.nii');
TE1_mag_comb = single(t.img);
t = load_untouch_nii('./e2.nii');
TE2_mag_comb = single(t.img);
t = load_untouch_nii('./e1_ph.nii');
TE1_ph_temp_comb = single(t.img);
t = load_untouch_nii('./e2_ph.nii');
TE2_ph_temp_comb = single(t.img);

TE1_ph_comb = (TE1_ph_temp_comb .* pi ./ 2048)-pi;
TE2_ph_comb = (TE2_ph_temp_comb .* pi ./ 2048)-pi;


%% Image Interpolation
voxel_multiplier_x = EPI_x/ref_x;
voxel_multiplier_y = EPI_y/ref_y;
voxel_multiplier_z = EPI_z/ref_z;

phase_diff = angle(exp(1i*(TE2_ph_comb-TE1_ph_comb)));

[nx,ny,nz] = size(phase_diff);
x = linspace(-1,1,nx);
y = linspace(-1,1,ny);
z = linspace(-1,1,nz);
[X,Y,Z] = meshgrid(x,y,z);

xi = linspace(-1,1,nx*voxel_multiplier_x);
yi = linspace(-1,1,ny*voxel_multiplier_y);
zi = linspace(-1,1,nz*voxel_multiplier_z);
[Xi,Yi,Zi] = meshgrid(xi,yi,zi);

phase_diff_new = interp3(X,Y,Z,phase_diff,Xi,Yi,Zi,'cubic');
TE1_mag = interp3(X,Y,Z,TE1_mag_comb,Xi,Yi,Zi,'cubic');

% for the error in prelude;
% ERROR: input phase image exceeds allowable phase range.
% Allowable range is 6.283 radians.  Image range is: 9.47644 radians.

for x = 1:size(phase_diff_new, 1)
    for y = 1:size(phase_diff_new, 2)
        for z = 1:size(phase_diff_new, 3)
            if phase_diff_new(x,y,z) > pi
                phase_diff_new(x,y,z) = phase_diff_new(x,y,z) - 2*pi;
            elseif phase_diff_new(x,y,z) < -pi
                phase_diff_new(x,y,z) = phase_diff_new(x,y,z) + 2*pi;
            end
        end
    end
end

genNii(phase_diff_new(size(phase_diff_new,1):-1:1,:,:),[vox_size vox_size vox_size], 'phase_diff_new.nii');
genNii(TE1_mag(size(TE1_mag,1):-1:1,:,:),[vox_size vox_size vox_size], 'TE1_mag.nii');

%% in shell
% system('prelude -a TE1_mag.nii -p phase_diff_new.nii -u phase_diff_unwrapped');
% system('bet TE1_mag.nii mask -f 0.3 -m');
% system('gunzip *mask*.gz');
% system('gunzip *phase*.gz');

system('prelude -a TE1_mag.nii -p phase_diff_new.nii -u phase_diff_unwrapped');
system('bet TE1_mag.nii mask -f 0.3 -m');
system('gunzip *mask*.gz');
system('gunzip *phase*.gz');


%% Calculate fieldmap
t = load_untouch_nii('phase_diff_unwrapped.nii');
phase_diff_unwrapped = single(t.img);

phase_diff_unwrapped_temp = phase_diff_unwrapped;

for ii=1:size(phase_diff_unwrapped,1)
    for jj=1:size(phase_diff_unwrapped,2)
        for kk=1:size(phase_diff_unwrapped,3)
            if phase_diff_unwrapped(ii,jj,kk) > pi && phase_diff_unwrapped(ii,jj,kk) <= 3*pi
                phase_diff_unwrapped(ii,jj,kk) = -(phase_diff_unwrapped(ii,jj,kk) - 2*pi);
            elseif phase_diff_unwrapped(ii,jj,kk) > 3*pi
                phase_diff_unwrapped(ii,jj,kk) = -(phase_diff_unwrapped(ii,jj,kk) - 4*pi);
            elseif phase_diff_unwrapped(ii,jj,kk) < -pi && phase_diff_unwrapped(ii,jj,kk) >= -3*pi
               phase_diff_unwrapped(ii,jj,kk) = -(phase_diff_unwrapped(ii,jj,kk) + 2*pi);
            elseif phase_diff_unwrapped(ii,jj,kk) < -3*pi
              phase_diff_unwrapped(ii,jj,kk) = -(phase_diff_unwrapped(ii,jj,kk) + 4*pi);
            else
            end
        end
    end
end
delB0_ref = phase_diff_unwrapped./(dTE*1e-3);

save delB0_ref delB0_ref

t = load_untouch_nii('mask_mask.nii');
mask = single(t.img);

genNii(delB0_ref.*mask./PAT,[vox_size vox_size vox_size], 'fieldmap_rads.nii');


%% in shell
% system('fugue --loadfmap=fieldmap_rads.nii -m --savefmap=fieldmap_rads_m')
system('fugue --loadfmap=fieldmap_rads.nii -m --savefmap=fieldmap_rads_m');

dwell = char(string(dwell));
for i = 1:numel(filename)
    name = filename(i).name;
    fname = split(name, '_bold');
    fname = char(fname(1));
    fname_sdc = strcat([fname, '_SDC.nii.gz']);
    system(strcat(['fugue -i ', name, ' --dwell=', dwell, ...
        ' --loadfmap=fieldmap_rads_m.nii', ' -u ', ...
        fname_sdc, ' --unwarpdir=y-']));

end
