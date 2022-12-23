function res = fft3c(x)
fctr = size(x,1)*size(x,2)*size(x,3);

res = zeros(size(x));

for n=1:size(x,4)
    res(:,:,:,n) = 1/sqrt(fctr)*fftshift(fftn(ifftshift(x(:,:,:,n))));
end


