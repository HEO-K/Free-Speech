function data_correl = mrir_array_stats_sim_data(data_indep, V0)
%MRIR_ARRAY_STATS_SIM_DATA
%
% data_correl = mrir_array_stats_sim_data(data_indep, V0)

% jonathan polimeni <jonp@padkeemao.nmr.mgh.harvard.edu>, 2007/jul/03
% $Id$
%**************************************************************************%

  VERSION = '$Revision: 1.5 $';
  if ( nargin == 0 ), help(mfilename); return; end;


  %==--------------------------------------------------------------------==%

  % assume input data is meant to be independent

  % the Cholesky decomposition gives the mapping
  P = chol(V0/2);

  data_correl = data_indep*P;


  % test the transformation to correlated coordinates
  V1 = cov(data_correl);

  v0 = V0(logical(triu(ones(size(V0)))));
  v1 = V1(logical(triu(ones(size(V1)))));

  v_mag_err_rel = ( (v0 - v1) ./ v1 );
  v_mag_err_rms = sqrt(mean(abs(v_mag_err_rel).^2));

  disp(sprintf('correlated data exhibits prescribed covariance with [[%2.1f%%]] accuracy', 100*v_mag_err_rms));


  return;


  %************************************************************************%
  %%% $Source: /home/jonp/cvsroot/dotfiles/emacs,v $
  %%% Local Variables:
  %%% mode: Matlab
  %%% fill-column: 76
  %%% comment-column: 0
  %%% End:
