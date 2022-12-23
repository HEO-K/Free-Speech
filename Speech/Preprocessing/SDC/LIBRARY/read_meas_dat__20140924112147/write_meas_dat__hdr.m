function write_meas_dat__hdr(header, filename)
%WRITE_MEAS_DAT__HDR
%
% write_meas_dat__hdr(header, filename)

% jonathan polimeni <jonp@nmr.mgh.harvard.edu>, 2010/may/22
% $Id: write_meas_dat__hdr.m,v 1.1 2010/12/07 14:39:22 jonp Exp $
%**************************************************************************%

  VERSION = '$Revision: 1.1 $';
  if ( nargin == 0 ), help(mfilename); return; end;


  %==--------------------------------------------------------------------==%

  hdr_file = regexprep(filename, '\.dat$', '.hdr');
  
  
  [fp, errmsg] = fopen(hdr_file, 'w', 'l');

  if ( fp == -1 ),
    disp(errmsg);
    error('error writing to file "%s"', hdr_file);
  end;

  % header is defined to be char string that starts immediately after first
  % 32-bit int in file (which is the data_start position) and runs all the
  % way up to data_start position, so the data_start can be inferred from
  % the length of the header
  data_start = length(header)+4;
  fwrite(fp, data_start, 'uint32');  

  % read in with fread, so write back out with fwrite
  fwrite(fp, header, 'uchar');
  
  if ( ftell(fp) ~= data_start ),
    fclose(fp);
    error('length of written file does not match expected header length---check if disk is full');
  end;

  fclose(fp);

    
  disp(sprintf('==> [%s]: wrote header file "%s"', mfilename, hdr_file));
  


  return;


  %************************************************************************%
  %%% $Source: /space/padkeemao/1/users/jonp/cvsjrp/PROJECTS/IMAGE_RECON/mrir_toolbox/write_meas_dat__hdr.m,v $
  %%% Local Variables:
  %%% mode: Matlab
  %%% fill-column: 76
  %%% comment-column: 0
  %%% End:
