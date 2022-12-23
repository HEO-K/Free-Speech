function [AtA,A] = dat2AtA2(data, kSize)

% [AtA,A,kernel] = dat2AtA(data, kSize)
%
% Function computes the calibration matrix from calibration data. 
%
% (c) Michael Lustig 2013



[sx,sy,nc,ne] = size(data);

tmp = im2row2(data,kSize); 

[tsx,tsy,tsz] = size(tmp);

A = reshape(tmp,tsx,tsy*tsz);

AtA = A'*A;
