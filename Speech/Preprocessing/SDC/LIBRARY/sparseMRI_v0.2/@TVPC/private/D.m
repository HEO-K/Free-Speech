function res = D(kspace)

%
% res = D(image)
%
% image = a 2D image
%
% This function computes the finite difference transform of the image
%
% Related functions:
%       adjD , invD 
%
%
% (c) Michael Lustig 2005

image = ifft2c2(kspace);


Dx = image([2:end,end],:,:,:) - image;
Dy = image(:,[2:end,end],:,:) - image;


res = cat(5, Dx, Dy);


