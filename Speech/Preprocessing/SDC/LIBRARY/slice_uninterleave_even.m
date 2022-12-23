function [ img ] = slice_uninterleave_even( img_int )
%SLICE_UNINTERLEAVE_ODD Summary of this function goes here
%   Detailed explanation goes here


img = zeros(size(img_int));

img(:,:,2:2:end,:) = img_int(:,:,1:end/2,:);
img(:,:,1:2:end,:) = img_int(:,:,1+end/2:end,:);
 


end

