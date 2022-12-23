function [nares, ghost_odd, ghost_even] = ghostgen_zyind_3Depi(poly_coef, params, sens_shift, wave_odd, wave_even, psf_shift_odd, psf_shift_even)

% form ghost correction factor based on the input polynomial coeffs
N = params.N;
x_all = 1:N(1);

ghost_angle_fit = polyval(poly_coef, x_all);
ghost_odd = exp(0i * ghost_angle_fit(:));
ghost_even = exp(-1i * ghost_angle_fit(:)); 


lsqr_tol = 1e-3;
lsqr_iter = 100;

y_skip = params.y_skip;
z_skip = params.z_skip;
Ry = params.Ry;
Rz = params.Rz;
cey_pos = params.cey_pos;
zi_pos = params.zi_pos;
Phs = params.Phs;
num_svd = params.num_chan;

ares = [];
acnt = 0;


for zi = 1:length(zi_pos)        
    z = zi_pos(zi);    
    z_ind = z : z_skip : N(3);

    for cey = 1:length(cey_pos)
        y = cey_pos(cey);
        y_ind = y : y_skip : N(2);

        rcv = sens_shift(:,y_ind,z_ind,:);
        phs = repmat(Phs(y_ind), [N(1),1,Rz]);

        data_odd = squeeze(wave_odd(:,y,z,:));
        data_even = squeeze(wave_even(:,y,z,:));
        rhs = cat(1, data_odd(:), data_even(:));

        params.rcv = rcv;
        params.phs = phs;
        params.cphs = conj(phs);
        params.crcv = conj(rcv);

        params.ghost_odd = repmat(ghost_odd, [1,2*Ry,Rz]);
        params.ghost_even = repmat(ghost_even, [1,2*Ry,Rz]);    
        params.cghost_odd = conj(params.ghost_odd);
        params.cghost_even = conj(params.ghost_even);

        params.psf_odd = repmat(psf_shift_odd(:,y_ind,z_ind), [1,1,1,num_svd]);
        params.psf_even = repmat(psf_shift_even(:,y_ind,z_ind), [1,1,1,num_svd]);
        params.cpsf_odd = conj(params.psf_odd);
        params.cpsf_even = conj(params.psf_even);

        [res, ~] = lsqr(@apply_3Depi_wave_ghost, rhs(:), lsqr_tol, lsqr_iter, [], [], [], params);        
        
        Ax = apply_3Depi_wave_ghost(res(:), params, 'ntransp');
                
        ares = [ares; (Ax(:) - rhs(:)) / norm(rhs(:))];
        acnt = acnt + 1;
    end
end

nares = norm(ares) / acnt;

end
