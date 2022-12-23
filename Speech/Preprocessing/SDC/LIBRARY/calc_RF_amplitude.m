function [ RF_Amp ] = calc_RF_amplitude( TR, T1, RF_volt, RF_factor )
%CALC_RF_AMPLITURE Summary of this function goes here
%   Detailed explanation goes here


% T1 : 
%      at 7  T, WM~1250 ms; GM~2000 ms     => take 1625 ms
%      at 3  T, WM~800 ms;  GM~1500 ms     => take 1150 ms
%      at 1.5T, WM~650 ms;  GM~1200 ms     => take 925 ms
%
% for Nadine's phantom at 7T: T1~200ms
%
% RF_volt : read from AFI middle of the brain
%           or from the protocol (~300)
%
% RF_factor : read from the RF pulse info text file (2.83 for 12 cm)
%                                                   (2.56 for 18 cm)


RF_Amp = acosd(exp(- TR / T1 )) * RF_volt * RF_factor / 90;


end



