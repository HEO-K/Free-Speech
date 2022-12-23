function [nares] = psfgen_binary(x, findxY, Yloc, findxZ, Zloc, receive, Wave_R, param)

ncol = size(Wave_R, 1);         % num readout points


% take subsets
xY = x(1:end/2);
xZ = x(end/2+1:end);


% create the low-fre com
mfreq = length(findxY);

cft = zeros(ncol, 1);
cft(findxY) = xY(1:mfreq) + 1i * xY(mfreq+1:2*mfreq);


% make it herm
cft(mod(ncol - (findxY(1:mfreq) - 1), ncol) + 1) = conj(cft(findxY));

cft(1) = real(cft(1));

cimg = real(ifft(cft));


% create the linear and sin adjustment term
a1 = real(xY(2*mfreq+1));
b1 = real(xY(2*mfreq+2));
c1 = real(xY(2*mfreq+3));

sine_fit = a1 * sin( b1 * [1:ncol] + c1 );

% linear fit
lm = real(xY(2*mfreq+4));
lb = real(xY(2*mfreq+5));

line_fit = lm * [1:ncol] + lb;


% combine and form psf
psf_vals = [cimg.'; (sine_fit + line_fit)];

angle_fit = Yloc * psf_vals;

Psf_fitY = exp(1i.*(angle_fit.'));


% create the low-fre com
mfreq = length(findxZ);

cft = zeros(ncol, 1);

cft(findxZ) = xZ(1:mfreq) + 1i * xZ(mfreq+1:2*mfreq);


% make it herm
cft(mod(ncol - (findxZ(1:mfreq) - 1), ncol) + 1) = conj(cft(findxZ));

cft(1) = real(cft(1));

cimg = real(ifft(cft));


% create the linear and sin adjustment term
a1 = real(xZ(2*mfreq+1));
b1 = real(xZ(2*mfreq+2));
c1 = real(xZ(2*mfreq+3));

sine_fit = a1 * sin( b1 * [1:ncol] + c1 );


% linear fit
lm = real(xZ(2*mfreq+4));
lb = real(xZ(2*mfreq+5));

line_fit = lm * [1:ncol] + lb;


% combine and form psf
psf_vals = [cimg.'; (sine_fit + line_fit)];

angle_fit = Zloc * psf_vals;

Psf_fitZ = exp(1i.*(angle_fit.'));

PsfYZ_fit = repmat(Psf_fitY, [1,1,size(Psf_fitZ,2)]) .* repmat(permute(Psf_fitZ, [1,3,2]), [1,size(Psf_fitY,2),1]);



lsqr_tol = 1e-3;
lsqr_iter = 100;

ares = [];
xres = [];

acnt = 0;

for zi = param.zi_pos
    zi_ind = zi : param.z_skip : zi + (param.Rz-1) * param.z_skip;
    
    psf_use = repmat(PsfYZ_fit(:,:,zi_ind), [1,1,1,param.num_chan]);
    receive_use = receive(:,:,zi_ind,:);
    
    for nz = 1:length(zi_ind)
        receive_use(:,:,nz,:) = circshift(receive_use(:,:,nz,:), [0,param.shift_amount(nz),0,0]);
        psf_use(:,:,nz,:) = circshift(psf_use(:,:,nz,:), [0,param.shift_amount(nz),0,0]);
    end    
    
    for cey = param.cey_pos       
        cey_ind = cey : param.y_skip : cey + (param.Ry-1) * param.y_skip;                
        
        param.psfs = psf_use(:,cey_ind,:,:);        
        param.rcv = receive_use(:,cey_ind,:,:);
                        
        rhs = squeeze( Wave_R(:,cey,zi,:) );
                   
        [res, ~] = lsqr(@apply_wave_fft, rhs(:), lsqr_tol, lsqr_iter, [], [], [], param);
        
        Ax = apply_wave_fft(res(:), param, 'ntransp');
                
        ares = [ares; double((Ax(:) - rhs(:)) / norm(rhs(:)))];
        xres = [xres; double(res)];
        acnt = acnt + 1;
                
    end
end

nares = norm(ares) / acnt;

end


