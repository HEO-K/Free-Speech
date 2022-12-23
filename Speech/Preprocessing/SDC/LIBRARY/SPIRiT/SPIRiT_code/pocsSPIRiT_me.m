function x = pocsSPIRiT_me(data, GOP, nIter, x0, wavWeight, show, wavType, wavSize, wavScale)
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

if nargin < 6
    show = 0;
end


if nargin < 7
    wavType = 'Daubechies';
end

    
if nargin < 8
    wavSize = 4;
end


if nargin < 9
    wavScale = 'Daubechies';
end

        

num_echo = size(data,4);


% if no l1 penalty then skip wavelet thresholding.
if wavWeight==0

	mask = (data==0);

	x = x0;

	for n = 1:nIter
        
        if ~mod(n, 10)
            disp(['Iter: ', num2str(n), ' / ', num2str(nIter)])
        end
        
        for e = 1:num_echo
            tmpx = (x(:,:,:,e) + GOP{e}*x(:,:,:,e)) .* mask(:,:,:,e);         % Apply (G-I)x + x
            
            x(:,:,:,e) = tmpx + data(:,:,:,e);                    % fix the data
        end        
        
	end

else
    
    % find the closest diadic size for the images
	[sx,sy,nc,ne] = size(data);
	
    ssx = 2^ceil(log2(sx)); 
    ssy = 2^ceil(log2(sy));
	ss = max(ssx, ssy);
	
    W = Wavelet(wavType, wavSize, wavScale);

    

	mask = (data==0);
	x = x0;

    for n=1:nIter
        
           
        if ~mod(n, 10)
            disp(['Iter: ', num2str(n), ' / ', num2str(nIter)])
        end
    
        
% 		x = (x + GOP*x ).*(mask) + data;    % Apply (G-I)*x + x
        
        
        for e = 1:ne
            x(:,:,:,e) = (x(:,:,:,e) + GOP{e}*x(:,:,:,e)) .* mask(:,:,:,e) + data(:,:,:,e);         % Apply (G-I)x + x
            
            % apply wavelet thresholding
            X = ifft2c(x(:,:,:,e)); % goto image domain
		
            X = zpad(X,ss,ss,nc);   % zpad to the closest diadic 
    		X = W*(X); % apply wavelet
	
            X = softThresh(X,wavWeight); % threshold ( joint sparsity)
            X = W'*(X); % get back the image
            X = crop(X,sx,sy,nc); % return to the original size
            
            xx = fft2c(X); % go back to k-space
            x(:,:,:,e) = xx .* mask(:,:,:,e) + data(:,:,:,e); % fix the data
	
        end 
        
        
        % apply wavelet thresholding
%         X = ifft2c(x); % goto image domain
% 		X= zpad(X,ss,ss,nc); % zpad to the closest diadic 
% 		X = W*(X); % apply wavelet
% 		X = softThresh(X,wavWeight); % threshold ( joint sparsity)
% 		X = W'*(X); % get back the image
% 		X = crop(X,sx,sy,nc); % return to the original size
% 		xx = fft2c(X); % go back to k-space
% 		x = xx.*mask + data; % fix the data
		
	
        
	end

end

function x = softThresh(y,t)
% apply joint sparsity soft-thresholding 
absy = sqrt(sum(abs(y).^2,3));
unity = y./(repmat(absy,[1,1,size(y,3)])+eps);

res = absy-t;
res = (res + abs(res))/2;
x = unity.*repmat(res,[1,1,size(y,3)]);




