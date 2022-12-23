%% Thanks for your interest in our STI SUITE software package!
% This file contains templates to use the STI SUITE functions.

% Author: Wei Li, PhD, and Chunlei, PhD
% Duke University

%% [1] HARPERELLA: Integrated phase unwrapping and background phase removal
% Inputs:
% rawphase: raw phase
% SpatialRes: Spatial resolution, e.g. SpatialRes=[1 1 1];
% padsize: size for padarray to increase numerical accuracy, 
%          e.g. padsize= [0 0 20];
% BrainMask: Binary Brain Mask
% nIter: Number of Iterations, e.g. nIter= 40;
% Radius: Radius, e.g Radius= 10;
[TissuePhase,NewMask]=HARPERELLA(rawphase,SpatialRes,padsize,BrainMask,nIter,Radius);

%% [2] The Laplacian-based phase unwrapping
% Inputs:
% rawphase: raw phase
% SpatialRes: Spatial resolution
% padsize: size for padarray to increase numerical accuracy

Unwrapped_Phase=LaplacianPhaseUnwrap(rawphase,SpatialRes,padsize);

%% [3] V-SHARP: background phase removal
% Inputs:
% Unwrapped_Phase: unwrapped phase
% SpatialRes: Spatial resolution
% padsize: size for padarray to increase numerical accuracy
% SMV_Radius: Spherical Mean Value Radius, typical values =25
% BrainMask: Binary Brain Mask

% Option 1: Large SMV_Radius with no deconvolution
[TissuePhase,NewMask]=V_SHARP(Unwrapped_Phase,BrainMask,SMV_Radius,padsize,SpatialRes);

% Option 2: Medium to Large SMV_Radius with deconvolution
[~,NewMask,PhaseDeconv]=V_SHARP(Unwrapped_Phase,BrainMask,SMV_Radius,padsize,SpatialRes);
% Note: the deconvolution step is skipped in this implementation. 

%% [4] LSQR: Quantative Susceptibility Mapping
% Inputs:
% TissuePhase: tissue phase
% SpatialRes: Spatial resolution
% padsize: size for padarray to increase numerical accuracy
% H: the field direction, e.g. H=[0 0 1];
% ninter: number of iterations. e.g. niter=50.

X = QSM_LSQR(TissuePhase,NewMask,H,SpatialRes,padsize,niter);

%% [5] Scalling to obtain Frequency and Susceptibility
% Inputs: 
% B0: B0, e.g. B0=3;
% TE_ms: TE in the unit of ms, e.g TE=30.

ScalingFactor=ScalingFactor(B0,TE_ms);

% then frequency shift and susceptibility can be obtained by
FrequencyShift=TissuePhase*ScalingFactor.Freq;
Susceptibility=X*ScalingFactor.X;

%% [6] Susceptibility Tensor Imaging
% Inputs: 
% Phase4D: 4D dataset the 4th dimention is orientation. e.g. 
%          size(Phase4D)=[128,128,128,n];                   % n directions
% H_Matrix: the H matrix
%          e.g. H= [  0.0072   -0.8902   -0.4556            % direction 1
%                     0.1121   -0.2320   -0.9662            % direction 2
%                     ........
%                    -0.1384    0.7923    0.5942];          % direction n
% parallel_Flag: parallel computing flag. recommend 'off'.

[X_tensor]=STI_Parfor(Phase4D,H_Matrix,parallel_Flag);

% don't forget scalling the tensors:
SusceptibilityTensor=X_tensor*ScalingFactor.X;




