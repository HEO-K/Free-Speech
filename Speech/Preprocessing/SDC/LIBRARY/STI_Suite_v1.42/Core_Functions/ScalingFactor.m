function SF=ScalingFactor_v1(B0,TE_ms)
% Wei Li, PhD
% Chunlei Liu, PHD
% Brain Imaging And Analysis Center, Duke Uiversity.

gamma = 42.575*2*pi; % gamma/1e6
TE = TE_ms*1.0e-3; % ms -> s
SF.X = 1/(gamma*B0*TE);
SF.Freq=1/TE/2/pi;
