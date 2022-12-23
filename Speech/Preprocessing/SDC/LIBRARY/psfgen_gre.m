function [nares, psf, psfY, psfZ] = psfgen_gre(x, params, sens_svd, Wave_deblur, Mask_roi)

xY = x(1:end/2);
xZ = x(1+end/2:end);

[psf, psfY, psfZ] = psf_from_coefs(xY, xZ, params.findY, params.findZ, params.Yloc, params.Zloc, params.psf_len);


lsqr_tol = 1e-3;
lsqr_iter = 100;

y_skip = params.y_skip;
z_skip = params.z_skip;
cey_pos = params.cey_pos;
zi_pos = params.zi_pos;
shift_amount = params.shift_amount;

ares = [];
acnt = 0;
    
for zi = zi_pos
    zi_ind = zi : z_skip : zi + (params.Rz-1) * z_skip;
    
    psf_use = repmat(psf(:,:,zi_ind), [1,1,1,size(Wave_deblur,4)]);
    receive_use = sens_svd(:,:,zi_ind,:);
    
    mask_use = zeros(size(receive_use(:,:,:,1)));
    for nz = 1:length(zi_ind)
        receive_use(:,:,nz,:) = circshift(receive_use(:,:,nz,:), [0,shift_amount(nz),0,0]);
        psf_use(:,:,nz,:) = circshift(psf_use(:,:,nz,:), [0,shift_amount(nz),0,0]);
        mask_use(:,:,nz) = circshift(Mask_roi(:,:,zi_ind(nz)), [0,shift_amount(nz),0]);
    end
    mask_use = sum(mask_use,3); 
         
    for cey = cey_pos
        cey_ind = cey : y_skip : cey + (params.Ry-1) * y_skip;
   
        if sum(sum(mask_use(:,cey_ind),1),2) > 0
            psfs = psf_use(:,cey_ind,:,:);
            rcv = receive_use(:,cey_ind,:,:);
            rhs = squeeze( Wave_deblur(:,cey,zi,:) );

            params.psfs = psfs;
            params.rcv = rcv;

            [res, ~] = lsqr(@apply_wave_fft, rhs(:), lsqr_tol, lsqr_iter, [], [], [], params);        
            Ax = apply_wave_fft(res(:), params, 'ntransp');
        
            ares = [ares; (Ax(:) - rhs(:)) / norm(rhs(:))];
            acnt = acnt + 1;
        end        
    end    
end

nares = norm(ares) / acnt;
 
end
