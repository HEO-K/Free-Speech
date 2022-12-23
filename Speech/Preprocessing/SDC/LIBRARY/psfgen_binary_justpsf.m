function [Psf_fitY, Psf_fitZ] = psfgen_binary_justpsf(x, ncol, findxY, Yloc, findxZ, Zloc)

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


%% make it herm
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

end

