function [PhasePerCm_Wave_resampledY G0_Y] = wave_encodingY(Ncol,ADC_duration,NcyclesGy,gYmax,sYmax,delay)

% Kawin Setsompop
% Oct 28 2010

% create the phase variation (per cm) that the Gy wave causes 
if nargin == 5
    delay = 0;
end

wavepoints = floor(ADC_duration/10);
wavepoints_Y = floor(wavepoints*(NcyclesGy+0.5)/NcyclesGy);
shiftToStartADC = floor( (wavepoints_Y -wavepoints)/2 );
T_wavepoints = 10^-5;
TimePerSineY = (wavepoints)*T_wavepoints/NcyclesGy;
wY = 2*pi/TimePerSineY;
if sYmax >= wY*gYmax
    G0_Y = gYmax;
else
    G0_Y = sYmax/wY;
end

GradTimePoints = [1:wavepoints_Y]*T_wavepoints;
GwaveY = G0_Y*sin(wY*(GradTimePoints-T_wavepoints));
GwaveY = [0 GwaveY]; GradTimePoints = [0 GradTimePoints]; % have a zero point for interpolation
GwaveYforPhase = ([0 GwaveY] + [GwaveY 0])/2; GwaveYforPhase = GwaveYforPhase(1:end-1);
PhasePerCm_WaveY = 2*pi*cumsum(GwaveYforPhase)*4257.56*T_wavepoints;
PrePhaseY = -(G0_Y/wY)*2*pi*4257.56;
PhasePerCm_WaveY = PhasePerCm_WaveY + PrePhaseY; % due to blip

PhasePerCm_WaveY = PhasePerCm_WaveY(1+shiftToStartADC:end);
GradTimePoints = [0:(length(PhasePerCm_WaveY)-1)]*T_wavepoints;

% resampling to get on Kx sampling rate
T_KxSampling = (ADC_duration*10^-6)/Ncol;
KxTimePoints = [1+delay:Ncol+delay]*T_KxSampling;
PhasePerCm_Wave_resampledY = interp1(GradTimePoints,PhasePerCm_WaveY,KxTimePoints,'spline');
