function [raw_stab, delta_phi] = mrir_artifact_phase_stabilization(raw, phasestab, refphasestab, TE, TS, TR)
%MRIR_ARTIFACT_PHASE_STABILIZATION
%
% raw_stab = mrir_artifact_phase_stabilization(raw, phasestab, refphasestab, TE, TS)

% jonathan polimeni <jonp@padkeemao.nmr.mgh.harvard.edu>, 2007/aug/15
% $Id: mrir_artifact_phase_stabilization.m,v 1.2 2007/08/21 19:25:26 jonp Exp $
%**************************************************************************%

  VERSION = '$Revision: 1.2 $';
  if ( nargin == 0 ), help(mfilename); return; end;

  PLOT = 1;
  
  
  %==--------------------------------------------------------------------==%

  dims_raw          = size(raw);           dims_raw(end+1:16)          = 1;
  dims_phasestab    = size(phasestab);     dims_phasestab(end+1:16)    = 1;
  dims_refphasestab = size(refphasestab);  dims_refphasestab(end+1:16) = 1;

  % compute average phase difference for each readout line (i.e., sum along
  % COL dimension)
  delta_phi = angle(sum( ...
      phasestab .* conj(repmat(refphasestab, [dims_phasestab ./ dims_refphasestab])), ...
                        1));

  % thus every image readout line gets a unique *scalar* phase rotation. for
  % this reason, the image data alone can be Fourier transformed along the
  % readout direction before applying the phase rotation.

  % assuming a linear evolution of phase, the phase difference at TS is
  % converted to the appropriate correction at TE by multiplying by TE/TS
  % ratio
  phase_rotation = exp( i * delta_phi * (-TE/TS) );

  dims_rotation = size(phase_rotation); dims_rotation(end+1:16) = 1;

  % apply rotation
  raw_stab = raw .* repmat(phase_rotation, [dims_raw ./ dims_rotation]);


  %==--------------------------------------------------------------------==%

  if ( PLOT ),

    t  = 0 : TR : ( TR*(dims_raw(2)-1) );

    iCha = 1;
    iSlc = 1;
    ts = ( TS*iSlc + t ) / 1000;  % sec
    

    figure; axis; hold on;
    plot(ts, delta_phi(1,:,iCha,1,1,1,1,1,1,iSlc), 'b.-');

    iSlc = dims_raw(10);
    ts = ( TS*iSlc + t ) / 1000;  % sec
    plot(ts, delta_phi(1,:,iCha,1,1,1,1,1,1,iSlc), 'g.-');
    
    set(gca, 'XLim', [ts(1), ts(end)]);
    set(gca, 'YLim', [-pi, +pi], 'YGrid', 'on');
    box on;
    xlabel('acquisition time (sec)');
    ylabel('phase difference, {\Delta}{\phi} (radians)');
    title('phase signal, \Delta\phi(t)');

    lh = legend('slice 1', sprintf('slice %d', iSlc));
    
    
    % compute N-point DFT with 16x fewer points to smooth out spectrum
    N = length(delta_phi) / 16;
    
    Phi = fftshift(fft(delta_phi(1,:,iCha,1,1,1,1,1,1,iSlc), N));
    Phi(end+1) = Phi(1);  % wrap
    
    delta_t = TR / 1000;  % sec
    f_max = 1/delta_t;    % Hz
    
    w = linspace(-pi, +pi, N+1);
    f = w / 2 / pi * f_max;
    

    figure('name', mfilename); axis; hold on;

    % average respiration freq = 0.3 hz
    rh = rectangle('Position', [0.2, 0, 0.2, +1000]);

    set(rh, 'FaceColor', [1 1 1] * 0.9, 'LineStyle', 'none')
    plot(f, abs(Phi), 'r.-');
    set(gca, 'XLim', [-1, +1] * f_max/2);
    set(gca, 'YLim', [0, +1.2] * max(abs(Phi)));
    box on;
    xlabel('frequency (Hz)');
    ylabel('amplitude spectrum (a.u.)');
    title('frequency content of phase signal, \Phi(\omega) = DFT\{\Delta\phi(t)\}');
    
  end;



  return;


  %************************************************************************%
  %%% $Source: /space/padkeemao/1/users/jonp/cvsjrp/PROJECTS/IMAGE_RECON/mrir_toolbox/mrir_artifact_phase_stabilization.m,v $
  %%% Local Variables:
  %%% mode: Matlab
  %%% fill-column: 76
  %%% comment-column: 0
  %%% End:
