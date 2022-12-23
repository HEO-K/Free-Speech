function x = fnlCg_joint(x0,params)
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
maxlsiter = params.lineSearchItnlim ;
gradToll = params.gradToll ;
alpha = params.lineSearchAlpha; ,    beta = params.lineSearchBeta;
t0 = params.lineSearchT0;
k = 0;
t = 1;

% copmute g0  = grad(Phi(x))

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
        [f1, ERRobj, RMSerr]  =  objective(FTXFMtx, FTXFMtdx, DXFMtx, DXFMtdx,x,dx, t, params);
	
	lsiter = 0;

	while (f1 > f0 - alpha*t*abs(g0(:)'*dx(:)))^2 & (lsiter<maxlsiter)
		lsiter = lsiter + 1;
		t = t * beta;
		[f1, ERRobj, RMSerr]  =  objective(FTXFMtx, FTXFMtdx, DXFMtx, DXFMtdx,x,dx, t, params);
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
% 	disp(sprintf('%d   , obj: %f, RMS: %f, L-S: %d', k,f1,RMSerr,lsiter));

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


return;


function [FTXFMtx, FTXFMtdx, DXFMtx, DXFMtdx] = preobjective(x, dx, params)
% precalculates transforms to make line search cheap

FTXFMtx = zeros(size(x));
FTXFMtdx = zeros(size(x));

for k = 1:params.L
    
    FTXFMtx(:,:,k) = params.FT{k} * x(:,:,k);
    FTXFMtdx(:,:,k) = params.FT{k} * dx(:,:,k);
    
end


DXFMtx = zeros([size(x,1), size(x,2), 2, params.L]);
DXFMtdx = zeros([size(x,1), size(x,2), 2, params.L]);

if params.TVWeight
    
    for k = 1:params.L
        
        DXFMtx(:,:,:,k) = params.TV * x(:,:,k);
        DXFMtdx(:,:,:,k) = params.TV * dx(:,:,k);
        
    end
    
else
    DXFMtx = 0;
    DXFMtdx = 0;
end





function [res, obj, RMS] = objective(FTXFMtx, FTXFMtdx, DXFMtx, DXFMtdx, x,dx,t, params);
%calculated the objective function


RMS = 0;

obj = 0;

for k = 1:params.L

    ob = FTXFMtx(:,:,k) + t*FTXFMtdx(:,:,k) - params.data(:,:,k);

    
    obj = obj + ob(:)'*ob(:);

end




TV = 0;

if params.TVWeight
    
    for k = 1:params.L
        
        w = DXFMtx(:,:,:,k) + t*DXFMtdx(:,:,:,k);
        
        TV = TV + abs(w).^2;   
        
    end
    
end

TV = sum(sqrt(TV(:))) * params.TVWeight;

res = obj + TV;




function grad = wGradient(x,params)

gradTV = 0;

gradObj = gOBJ(x,params);


if params.TVWeight
    gradTV = gTV(x,params);
end


grad = (gradObj + params.TVWeight.*gradTV);



function gradObj = gOBJ(x, params)
% computes the gradient of the data consistency

gradObj = zeros(size(x));

for k = 1:params.L
    
	gradObj(:,:,k) = params.FT{k}' * (params.FT{k} * x(:,:,k) - params.data(:,:,k));

end
    
gradObj = 2*gradObj ;



function grad = gTV(x,params)
% compute gradient of TV operator

Dx = zeros(size(x,1), size(x,2), 2, params.L);

for k = 1:params.L
        
    Dx(:,:,:,k) = params.TV * x(:,:,k);
    
end
    
Dx_L2 = sqrt( sum(abs(Dx).^2, 4) );


G = Dx ./ (eps + repmat(Dx_L2, [1,1,1,params.L]));


grad = zeros(size(x));

for k = 1:params.L

    grad(:,:,k) = params.TV' * G(:,:,:,k);

end








