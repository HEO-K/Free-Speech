function img_corrected = deblur_blip(img_blip, SliceSep, PhaseShiftBtwSimulSlices, sliceThickness, z_offset)

PhaseShiftPerMM = PhaseShiftBtwSimulSlices / SliceSep;

num_slice = size(img_blip, 3);       % no of collapsed slices

SlicePos = -[-ceil((num_slice-1)/2):1:floor((num_slice-1)/2)]*sliceThickness + z_offset; % in mm


Img_blip = fftshift(fft(fftshift(img_blip, 2), [], 2), 2);

Img_corrected = zeros(size(Img_blip));

for SlcCount = 1:num_slice
    Img_corrected(:,2:2:end,SlcCount,:) = Img_blip(:,2:2:end,SlcCount,:);       
    Img_corrected(:,1:2:end,SlcCount,:) = Img_blip(:,1:2:end,SlcCount,:) * exp(-1i*PhaseShiftPerMM*SlicePos(SlcCount));
end


img_corrected = fftshift(ifft(fftshift(Img_corrected, 2), [], 2), 2);

end