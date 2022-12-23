function x = fnlCg_nlinv(x0,params)
%-----------------------------------------------------------------------
%
% res = fnlCg(x0,params)
%
% implementation of a L1 penalized non linear conjugate gradient reconstruction
%
% The function solves the following problem:
%
% given k-space measurments y, and a fourier operator F the function 
% finds the image x that minimizes:
%
% Phi(x) = ||F* W' *x - y||^2 + lambda1*|x|_1 + lambda2*TV(W'*x) 
%
%
% the optimization method used is non linear conjugate gradient with fast&cheap backtracking
% line-search.
% 
% (c) Michael Lustig 2007
%-------------------------------------------------------------------------
x = x0;


% line search parameters
maxlsiter = params.lineSearchItnlim;
gradToll = params.gradToll;
alpha = params.lineSearchAlpha;     
beta = params.lineSearchBeta;
t0 = params.lineSearchT0;
k = 0;


% compute g0  = grad(Phi(x))
g0 = wGradient(x,params);

dx = -g0;


% iterations
while(1)

% backtracking line-search

	% pre-calculate values, such that it would be cheap to compute the objective
	% many times for efficient line-search
	[FTXFMtx, FTXFMtdx, DXFMtx, DXFMtdx] = preobjective(x, dx, params);
	f0 = objective(FTXFMtx, FTXFMtdx, DXFMtx, DXFMtdx,x,dx, 0, params);
	t = t0;
        f1  =  objective(FTXFMtx, FTXFMtdx, DXFMtx, DXFMtdx,x,dx, t, params);
	
	lsiter = 0;

	while (f1 > f0 - alpha*t*abs(g0(:)'*dx(:)))^2 & (lsiter<maxlsiter)
		lsiter = lsiter + 1;
		t = t * beta;
		f1  =  objective(FTXFMtx, FTXFMtdx, DXFMtx, DXFMtdx,x,dx, t, params);
	end

	if lsiter == maxlsiter
		disp('Reached max line search,.... not so good... might have a bug in operators. exiting... ');
		return;
	end

	% control the number of line searches by adapting the initial step search
	if lsiter > 2
		t0 = t0 * beta;
	end 
	
	if lsiter<1
		t0 = t0 / beta;
	end

	x = (x + t*dx);

	%--------- uncomment for debug purposes ------------------------	
	disp(sprintf('%d   , obj: %f,  L-S: %d', k, f1, lsiter));
	%---------------------------------------------------------------
	
    %conjugate gradient calculation
    
	g1 = wGradient(x,params);
	bk = g1(:)'*g1(:)/(g0(:)'*g0(:)+eps);
	g0 = g1;
	dx =  - g1 + bk* dx;
	k = k + 1;
	
	%TODO: need to "think" of a "better" stopping criteria ;-)
	if (k > params.Itnlim) | (norm(dx(:)) < gradToll) 
		break;
	end

end


end




%--------------------------------------------------------------------------
function [FTXFMtx, FTXFMtdx, DXFMtx, DXFMtdx] = preobjective(x, dx, params)
% precalculates transforms to make line search cheap

rho = repmat(permute(x(:,:,1:params.e), [1,2,4,3]), [1,1,params.c,1]);
c = joint_apweights(params.W, x(:,:,1+params.e:end));


d_rho = repmat(permute(dx(:,:,1:params.e), [1,2,4,3]), [1,1,params.c,1]);
d_c = joint_apweights(params.W, dx(:,:,1+params.e:end));


% params.cRep_n = repmat(params.c_n, [1,1,1,params.e]);
% params.rhoRep_n = repmat(permute(params.rho_n, [1,2,4,3]), [1,1,params.c,1]);


FTXFMtx = params.P .* joint_myfft( params.cRep_n .* rho + repmat(c, [1,1,1,params.e]) .* params.rhoRep_n );
    

FTXFMtdx = params.P .* joint_myfft( params.cRep_n .* d_rho + repmat(d_c, [1,1,1,params.e]) .* params.rhoRep_n );
    
    
if params.TVWeight
%     DXFMtx = params.TV * (x(:,:,1:params.e) + params.rho_n);
    DXFMtx = params.TV * x(:,:,1:params.e);
    DXFMtdx = params.TV * dx(:,:,1:params.e);
else
    DXFMtx = 0;
    DXFMtdx = 0;
end
 

end
%--------------------------------------------------------------------------




%--------------------------------------------------------------------------
function [res, obj] = objective(FTXFMtx, FTXFMtdx, DXFMtx, DXFMtdx, x, dx, t, params)
%calculates the objective function

% params.data = kspace - params.P .* joint_myfft( cRep_n .* rhoRep_n );

obj = FTXFMtx + t*FTXFMtdx - params.data;
obj = obj(:)'*obj(:);


if params.TVWeight
%     w = DXFMtx + t*DXFMtdx;
    w = DXFMtx + t*DXFMtdx + params.TVrho_n;
    
    if params.L == 21        
        % L21 joint penalty
        TV = sum(abs(w).^2, 3).^0.5;
        TV = sum(TV(:));
    else
        % L1 for each echo separately
        TV = sum(abs(w(:)));
    end
    
else
    TV = 0;
end
 

if params.xfmWeight    
    % L2 Tikhonov constraint
    Chat = x(:,:,1+params.e:end) + t*dx(:,:,1+params.e:end) + params.chat_n; 

    XFM = sum(abs(Chat(:)).^2);   

    if ~params.TVWeight
        % use L2 if TV is not used for image
        Rho = x(:,:,1:params.e) + t*dx(:,:,1:params.e) + params.rho_n; 
        
        XFM = sum(abs(Rho(:)).^2) + XFM;   
    end
else
    XFM = 0;
end


res = obj + TV * params.TVWeight + XFM * params.xfmWeight;

end
%--------------------------------------------------------------------------



%--------------------------------------------------------------------------
function grad = wGradient(x,params)

gradXFM = 0;
gradTV = 0;

gradObj = gOBJ(x,params);

if params.xfmWeight
    gradXFM = gXFM(x,params);
end

if params.TVWeight
    gradTV = gTV(x,params);
end


grad = gradObj + params.xfmWeight * gradXFM + params.TVWeight * gradTV;

end
%--------------------------------------------------------------------------



%--------------------------------------------------------------------------
function gradObj = gOBJ(x,params)
% computes the gradient of the data consistency

rho = repmat(permute(x(:,:,1:params.e), [1,2,4,3]), [1,1,params.c,1]);
c = joint_apweights(params.W, x(:,:,1+params.e:end));


FTXFMtx = params.P .* joint_myfft( params.cRep_n .* rho + repmat(c, [1,1,1,params.e]) .* params.rhoRep_n );


y = joint_myifft( params.P.* (FTXFMtx - params.data) );


gradRho = 2 * squeeze( sum(params.conj_cRep_n .* y, 3) );


gradChat = 2 * joint_apweightsH( params.W, sum(params.conj_rhoRep_n .* y, 4) );


gradObj = cat(3, gradRho, gradChat);


end
%--------------------------------------------------------------------------



%--------------------------------------------------------------------------
function grad = gXFM(x,params)
% computes gradient of the L2 Tikhonov operator

if ~params.TVWeight
    % use L2 if TV not used for image
    gRho = 2 * (x(:,:,1:params.e) + params.rho_n); 
else
    % use TV constraint instead of L2 for image
    gRho = zeros(size(x(:,:,1:params.e)));
end
    
gChat = 2 * (x(:,:,1+params.e:end) + params.chat_n); 

grad = cat(3, gRho, gChat);

end
%--------------------------------------------------------------------------



%--------------------------------------------------------------------------
function grad = gTV(x,params)
% computes gradient of TV operator

% Dx = params.TV * (x(:,:,1:params.e) + params.rho_n);
Dx = (params.TV * x(:,:,1:params.e)) + params.TVrho_n;


if params.L == 21
    % joint L21 penalty
    DxL2 = sum(abs(Dx).^2, 3).^0.5;
    G = Dx ./ (eps + repmat(DxL2, [1,1,params.e,1]));
else
    % L1 penalty for each echo separately
    G = sign(Dx);
end

grad = cat(3, params.TV' * G, zeros(size(x(:,:,1+params.e:end))));

end
%--------------------------------------------------------------------------

 
