function [x, sens] = pocsSPIRiT_rank(data, GOP, nIter, x0, low_rank)
%
%
% res = pocsSPIRIT(y, GOP, nIter, x0, wavWeight, show)
%
% Implementation of the Cartesian, POCS l1-SPIRiT reconstruction
%
% Input:
%		y - Undersampled k-space data. Make sure that empty entries are zero
%			or else they will not be filled.
%		GOP -	the SPIRiT kernel operator obtained by calibration
%		nIter -	Maximum number of iterations
%		x0 - initial guess
%		wavWeight - wavlet threshodling parameter
% 		show - >1 to display progress (slower)
%
% Outputs:
%		res - Full k-space matrix
%
% (c) Michael Lustig 2007
%

if nargin < 5
    low_rank = 1;
end


[sx,sy,nc,ne] = size(data);


mask = (data==0);
x = x0;

X = zeros([sx,sy,nc,ne]);
sens = zeros([nc,sx,sy]);


for n = 1:nIter


    if ~mod(n, 5)
        disp(['Iter: ', num2str(n), ' / ', num2str(nIter)])
    end


    for e = 1:ne
        x(:,:,:,e) = (x(:,:,:,e) + GOP{e}*x(:,:,:,e)) .* mask(:,:,:,e) + data(:,:,:,e);         % Apply (G-I)x + x

        X(:,:,:,e) = ifft2c(x(:,:,:,e));    % goto image domain
    end



    % svd truncation
    temp = permute(X, [3,4,1,2]);
    img1 = zeros([nc, ne, sx, sy]); 

    for cey = 1:sy    
        for ay = 1:sx

            mtx = temp(:,:,ay,cey);

            [u,s,v] = svd(mtx);

            % low rank approximation:
            mtx1 = u(:,1:low_rank) * s(1:low_rank,1:low_rank) * v(:,1:low_rank)';

            img1(:,:,ay,cey) = mtx1;
            
            
            if n == nIter
                sens(:,ay,cey) = u(:,1);
            end

        end
    end

    X = permute(img1, [3,4,1,2]);

    for e = 1:ne
        xx = fft2c(X(:,:,:,e));          % go back to k-space

        x(:,:,:,e) = xx .* mask(:,:,:,e) + data(:,:,:,e); % fix the data
    end


end

sens = permute(sens, [2,3,1]);

 
end
