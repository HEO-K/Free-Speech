function [nares] = psfgen_zyind_3Depi(x, param, findxY, Yloc, findxZ, Zloc, receive_pad, Wave_R, cey_pos, zi_pos)

ncol = param.psf_len;
num_chan = param.num_chan;
Ry = param.Ry;
Rz = param.Rz;
lsqr_tol = param.lsqr_tol;
lsqr_iter = param.lsqr_iter;
y_skip = param.y_skip;
z_skip = param.z_skip;
shift_amount = param.shift_amount;
Phs = param.Phs;

if nargin < 9
    cey_pos = floor(y_skip/2);
end

if nargin < 10
    zi_pos = [1 floor(z_skip/2) z_skip];
end


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


ares = [];
xres = [];

acnt = 0;

% for zi = [1 floor(z_skip/2) z_skip]        
for z = 1:length(zi_pos)        
    zi = zi_pos(z); 
    
    zi_ind = zi : z_skip : zi + (Rz-1) * z_skip;
    
    psf_use = repmat(PsfYZ_fit(:,:,zi_ind), [1,1,1,num_chan]);
    receive_use = receive_pad(:,:,zi_ind,:);
    
    for nz = 1:length(zi_ind)
        receive_use(:,:,nz,:) = circshift(receive_use(:,:,nz,:), [0,shift_amount(nz),0,0]);
        psf_use(:,:,nz,:) = circshift(psf_use(:,:,nz,:), [0,shift_amount(nz),0,0]);
    end    
    
%     for cey = floor(y_skip / 2)        
    for ce = 1:length(cey_pos)   
        cey = cey_pos(ce);
        
        cey_ind = cey : y_skip : cey + (Ry-1) * y_skip;                
        
        psfs = psf_use(:,cey_ind,:,:);        
        rcv = receive_use(:,cey_ind,:,:);
                        
        rhs = squeeze( Wave_R(:,cey,zi,:) );
            
        param.psfs = psfs;        
        param.rcv = rcv;
        param.phs = Phs(:,cey_ind,:);
        
        [res, ~] = lsqr(@apply_wave_3Depi, rhs(:), lsqr_tol, lsqr_iter, [], [], [], param);
        
        Ax = apply_wave_3Depi(res(:), param, 'ntransp');
                
        ares = [ares; double((Ax(:) - rhs(:)) / norm(rhs(:)))];
        xres = [xres; double(res)];
        acnt = acnt + 1;
    end
end

nares = norm(ares) / acnt;

end