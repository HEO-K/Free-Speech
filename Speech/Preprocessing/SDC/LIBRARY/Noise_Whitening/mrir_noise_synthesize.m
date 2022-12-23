function varargout = mrir_noise_synthesize(dims, noisecov, varargin)
%MRIR_NOISE_SYNTHESIZE
%
% noise_color = mrir_noise_synthesize(dims, noisecov);
% noise_color = mrir_noise_synthesize(dims, noisecov, autocorr_filter);
% noise_color = mrir_noise_synthesize(dims, noisecov, autocorr_filter, VERIFY);
%
%
% example:
%
%   noisecov = mrir_array_stats_matrix(noise, 'cov', 0);
%   autocorr_filter = mrir_noise_autocorr_calculate(noise);
%   synth = mrir_noise_synthesize(size(noise), noisecov, autocorr_filter);
%
%   mrir_noise_bandwidth(noise, 1)
%   mrir_noise_bandwidth(synth, 1)
%
%   synthcov = mrir_array_stats_matrix(noise, 'cov', 0);
%
%   figure('name', 'comparison of measured noise to synthesized noise');
%   subplot(1,3,1); imagesc(abs(noisecov)); axis image; colorbar; title('measured');
%   subplot(1,3,2); imagesc(abs(synthcov)); axis image; colorbar; title('synthetic');
%   subplot(1,3,3); imagesc(abs(noisecov-synthcov)); axis image; colorbar; title('difference');
%
% 
% See also MRIR_NOISE_AUTOCORR_CALCULATE, MRIR_NOISE_AUTOCORR_APPLY, MRIR_NOISE_BANDWIDTH.

% "mrir_array_stats_sim_data" performs a similar operation but on data
% passed as input.

% jonathan polimeni <jonp@nmr.mgh.harvard.edu>, 2008/nov/23
% $Id: mrir_noise_synthesize.m,v 1.3 2009/10/15 06:28:12 jonp Exp $
%**************************************************************************%

  VERSION = '$Revision: 1.3 $';
  if ( nargin == 0 ), help(mfilename); return; end;


  %==--------------------------------------------------------------------==%

  Ncha = dims(mrir_DIM_CHA);

  if ( (nargin < 2) || isempty(noisecov) ),
    noisecov = complex(rand(Ncha, Ncha), rand(Ncha, Ncha));
  end;

  if ( Ncha ~= size(noisecov, 1) ),
    error('channel number mismatch');
  end;

  FLAG__autocorr = 0;
  if ( nargin >= 3 ),
    autocorr_filter = varargin{1};
    
    if ( ~isempty(autocorr_filter) ),
      FLAG__autocorr = 1;
    end;
  end;  

  FLAG__VERIFY = 0;
  if ( nargin >= 4 ),
    FLAG__VERIFY = varargin{2};
  end;

  setstate = sum(100*clock);
  if ( nargin >= 5 ),
    setstate = varargin{3};
    disp(sprintf('==> [%s]: setting state of random number generator with value [ %f ]', mfilename, setstate));
  end;
  
  
  %==--------------------------------------------------------------------==%

  randn('state', setstate);

  noise_white = complex(randn(dims), randn(dims));

  % calculate projection from cholesky decomposition
  P = chol(noisecov/2);

  noise_color = mrir_array_transform(noise_white, P');


  if ( FLAG__autocorr ),
    noise_color = mrir_noise_autocorr_apply(noise_color, autocorr_filter);
  end;
    
  
  %==--------------------------------------------------------------------==%

  if ( FLAG__VERIFY ),

    noisecov_color = mrir_array_stats_matrix(noise_color, 'cov', 0);

    v0 = noisecov(      logical(triu(ones(size(noisecov)))));
    v1 = noisecov_color(logical(triu(ones(size(noisecov)))));

    v_mag_err_rel = ( (v0 - v1) ./ v1 );
    v_mag_err_rms = sqrt(mean(abs(v_mag_err_rel).^2));

    disp(sprintf('correlated data exhibits prescribed covariance with [[%2.1f%%]] accuracy', 100 * abs([1 - (1/v_mag_err_rms)])));

  end;

  
  %==--------------------------------------------------------------------==%

  if ( nargout >= 1 ),
    varargout{1} = noise_color;
  end;
  
  if ( nargout >= 2 ),
  
    noisecov_synth = mrir_array_stats_matrix(noise_color, 'cov', 0);
    varargout{2} = noisecov_synth;

    varargout{3} = setstate;
    
  end;
  
    
  
  return;


  %************************************************************************%
  %%% $Source: /space/padkeemao/1/users/jonp/cvsjrp/PROJECTS/IMAGE_RECON/mrir_toolbox/mrir_noise_synthesize.m,v $
  %%% Local Variables:
  %%% mode: Matlab
  %%% fill-column: 76
  %%% comment-column: 0
  %%% End:

