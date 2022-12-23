function x = fnlCg_mgn(x0,params)
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
	disp(sprintf('%d   , obj: %f, RMS: %f, L-S: %d', k,f1,RMSerr,lsiter));
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


%% ________________________________________________________________________
function [FTXFMtx, FTXFMtdx, DXFMtx, DXFMtdx] = preobjective(x, dx, params)
% precalculates transforms to make line search cheap

FTXFMtx = params.FT * (params.P .* x);
FTXFMtdx = params.FT * (params.P .* dx);

if params.TVWeight
    DXFMtx = params.TV*x;
    DXFMtdx = params.TV*dx;
else
    DXFMtx = 0;
    DXFMtdx = 0;
end
end
%% ________________________________________________________________________


%% ________________________________________________________________________
function [res, obj, RMS] = objective(FTXFMtx, FTXFMtdx, DXFMtx, DXFMtdx, x, dx, t, params)
% calculates the objective function

p = params.pNorm;

obj = FTXFMtx + t*FTXFMtdx - params.data;
obj = obj(:)'*obj(:);

if params.TVWeight
    w = DXFMtx(:) + t*DXFMtdx(:);
    TV = (w.*conj(w)+params.l1Smooth).^(p/2); 
else
    TV = 0;
end

TV = sum(TV.*params.TVWeight(:));
RMS = sqrt(obj/sum(abs(params.data(:))>0));

res = obj + TV;
end
%% ________________________________________________________________________


%% ________________________________________________________________________
function grad = wGradient(x,params)

gradTV = 0;

gradObj = gOBJ(x,params);

if params.TVWeight
    gradTV = gTV(x,params);
end

grad = gradObj + params.TVWeight.*gradTV;
end
%% ________________________________________________________________________


%% ________________________________________________________________________
function gradObj = gOBJ(x,params)
% computes the gradient of the data consistency

% 	gradObj = params.XFM*(params.FT'*(params.FT*(params.XFM'*x) - params.data));

% gradObj = 2*gradObj ;

gradObj = params.Pt .* (params.FT' * (params.FT * (params.P .* x) - params.data));

gradObj = 2 * real(gradObj);

end
%% ________________________________________________________________________


%% ________________________________________________________________________
function grad = gTV(x,params)
% computes gradient of TV operator
p = params.pNorm;

Dx = params.TV*x;

G = p*Dx.*(Dx.*conj(Dx) + params.l1Smooth).^(p/2-1);
grad = params.TV'*G;
end
%% ________________________________________________________________________



