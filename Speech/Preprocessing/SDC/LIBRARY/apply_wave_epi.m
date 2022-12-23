function [ res, tflag ] = apply_wave_epi( in, params, tflag )
%APPLY_COLLAPSE Summary of this function goes here
%   Detailed explanation goes here

if strcmp(tflag,'transp');
    
    im = reshape(in, [params.psf_len, 1, 1, params.num_chan]);
    Im = repmat(im, [1,params.Ry,params.Rz,1]);
    
    Temp = ifft(fft(Im, [], 1) .* conj(params.psfs), [], 1);

    temp = Temp(end/2+1-params.img_len/2:end/2+params.img_len/2,:,:,:) .* conj(params.rcv);
    
    Res = sum(temp,4);
    res = Res(:);

else

    im = reshape(in, [params.img_len, params.Ry, params.Rz]);
    img = repmat(im, [1,1,1,params.num_chan]) .* params.rcv;
    Img = padarray(img, [params.pad_size,0,0,0]);
    
    Img_conv = ifft(fft(Img, [], 1) .* params.psfs, [], 1);    
    
    Res = squeeze(sum(sum(Img_conv, 2), 3));
    res = Res(:);
end

end 