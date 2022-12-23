function [Psf_fitYZ, Psf_fitY, Psf_fitZ] = psf_from_coefs(xY, xZ, findY, findZ, Yloc, Zloc, ncol)

% create the low-fre com
mfreq = length(findY);

cft = zeros(ncol, 1);
cft(findY) = xY(1:mfreq) + 1i * xY(mfreq+1:2*mfreq);


% make it herm
cft(mod(ncol - (findY - 1), ncol) + 1) = conj(cft(findY));

cft(1) = real(cft(1));
cimg = real(ifft(cft));


sine_fit = zeros(1, ncol);
line_fit = zeros(1, ncol);


% combine and form psf
psf_vals = [cimg.'; (sine_fit + line_fit)];
angle_fit = Yloc * psf_vals;
Psf_fitY = exp(1i.*(angle_fit.'));


% create the low-fre com
mfreq = length(findZ);

cft = zeros(ncol, 1);

cft(findZ) = xZ(1:mfreq) + 1i * xZ(mfreq+1:2*mfreq);


% make it herm
cft(mod(ncol - (findZ - 1), ncol) + 1) = conj(cft(findZ));

cft(1) = real(cft(1));
cimg = real(ifft(cft));


% combine and form psf
psf_vals = [cimg.'; (sine_fit + line_fit)];
angle_fit = Zloc * psf_vals;
Psf_fitZ = exp(1i.*(angle_fit.'));

Psf_fitYZ = repmat(Psf_fitY, [1,1,size(Psf_fitZ,2)]) .* repmat(permute(Psf_fitZ, [1,3,2]), [1,size(Psf_fitY,2),1]);

end
