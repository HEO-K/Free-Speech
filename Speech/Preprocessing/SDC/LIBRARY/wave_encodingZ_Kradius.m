function [PhasePerCm_Wave_resampledZ,  G0_Z, K_WaveZ, K_radius, amount_delta_k] = wave_encodingZ_Kradius(Ncol,ADC_duration,NcyclesGz,gZmax,sZmax,delay,FOV)

% Kawin Setsompop
% Oct 28 2010

% create the phase variation (per cm) that the Gz wave causes 
if nargin == 5
    delay = 0;
end

wavepoints = floor(ADC_duration/10);
T_wavepoints = 10^-5;
TimePerSineZ = (wavepoints)*T_wavepoints/NcyclesGz; 
wZ = 2*pi/TimePerSineZ;
if sZmax >= wZ*gZmax
    G0_Z = gZmax;
    % gradient limited: 
    % slew_used = wZ * gZmax    
    % gradient_used = gZmax
else
    G0_Z = sZmax/wZ;
    % slew limited:
    % slew_used = sZmax
    % gradient_used = sZmax/wZ
end

GradTimePoints = [1:wavepoints]*T_wavepoints;
GwaveZ = G0_Z*sin(wZ*(GradTimePoints-T_wavepoints));
%GwaveZ = G0_Z*cos(wZ*(GradTimePoints-T_wavepoints));
GwaveZ = [0 GwaveZ]; GradTimePoints = [0 GradTimePoints]; % have a zero point for interpolation
GwaveZforPhase = ([0 GwaveZ] + [GwaveZ 0])/2; GwaveZforPhase = GwaveZforPhase(1:end-1);
PhasePerCm_WaveZ = 2*pi*cumsum(GwaveZforPhase)*4257.56*T_wavepoints;

K_WaveZ = PhasePerCm_WaveZ / 2 / pi;
K_radius = (max( K_WaveZ ) - min( K_WaveZ )) / 2;


delta_k = 1 / FOV;
amount_delta_k = K_radius / delta_k;




PrePhaseZ = -(G0_Z/wZ)*2*pi*4257.56;
PhasePerCm_WaveZ = PhasePerCm_WaveZ + PrePhaseZ; % due to blip

% resampling to get on Kx sampling rate
T_KxSampling = (ADC_duration*10^-6)/Ncol;
KxTimePoints = [1+delay:Ncol+delay]*T_KxSampling; % 0.5 shifting to account for K being avg value, also start at second point (as first point is at 0 and not at -0.5)
PhasePerCm_Wave_resampledZ = interp1(GradTimePoints,PhasePerCm_WaveZ,KxTimePoints,'spline');


