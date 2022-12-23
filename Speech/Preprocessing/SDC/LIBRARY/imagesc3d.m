function [  ] = imagesc3d( img, pos, fig_num, rot_deg, scale_fig, avg_size, title_fig, MIP )
%IMAGESC3D Summary of this function goes here
%   Detailed explanation goes here

if norm(imag(img(:))) > 0
    img = abs(img);
end

if nargin < 2
    pos = round(size(img)/2);
end

if nargin < 3
    fig_num = 1;
end

if nargin < 4
    rot_deg = [0,0,0];
end

if nargin < 5
    scale_fig = [min(img(:)), max(img(:))];
end

if nargin < 6
    avg_size = 0;
end

if nargin < 7
    title_fig = '';
end

if nargin < 8
    MIP = 0;
end
 

if ~MIP
    figure(fig_num), subplot(131), imagesc( imrotate(squeeze(mean(img(pos(1)-avg_size:pos(1)+avg_size,:,:),1)), rot_deg(1)), scale_fig ), axis image off, colormap gray
    figure(fig_num), subplot(132), imagesc( imrotate(squeeze(mean(img(:,pos(2)-avg_size:pos(2)+avg_size,:),2)), rot_deg(2)), scale_fig ), axis image off, colormap gray
        title(title_fig, 'color', 'w', 'fontsize', 24)
    figure(fig_num), subplot(133), imagesc( imrotate(mean(img(:,:,pos(3)-avg_size:pos(3)+avg_size),3), rot_deg(3)), scale_fig ), axis image off, colormap gray
else
    figure(fig_num), subplot(131), imagesc( imrotate(squeeze(min(img(pos(1)-avg_size:pos(1)+avg_size,:,:),[],1)), rot_deg(1)), scale_fig ), axis image off, colormap gray
    figure(fig_num), subplot(132), imagesc( imrotate(squeeze(min(img(:,pos(2)-avg_size:pos(2)+avg_size,:),[],2)), rot_deg(2)), scale_fig ), axis image off, colormap gray
        title(title_fig, 'color', 'w', 'fontsize', 24)
    figure(fig_num), subplot(133), imagesc( imrotate(min(img(:,:,pos(3)-avg_size:pos(3)+avg_size),[],3), rot_deg(3)), scale_fig ), axis image off, colormap gray    
end
    set(gcf, 'color', 'k')

end

