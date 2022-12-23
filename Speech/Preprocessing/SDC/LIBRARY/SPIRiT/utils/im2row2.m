function Res = im2row2(im, winSize)
%res = im2row(im, winSize)
[sx,sy,sz,ne] = size(im);


Res = zeros(ne * (sx-winSize(1)+1)*(sy-winSize(2)+1),prod(winSize),sz);

for n = 1:ne

    res = zeros((sx-winSize(1)+1)*(sy-winSize(2)+1),prod(winSize),sz);
    count=0;
    for y=1:winSize(2)
        for x=1:winSize(1)
            count = count+1;
            res(:,count,:) = reshape(im(x:sx-winSize(1)+x,y:sy-winSize(2)+y,:,n),...
                (sx-winSize(1)+1)*(sy-winSize(2)+1),1,sz);
        end
    end

    Res( 1 + (n-1) * (sx-winSize(1)+1)*(sy-winSize(2)+1) : n * (sx-winSize(1)+1)*(sy-winSize(2)+1), :, : ) = res;
    
end