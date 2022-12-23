function Res = adjD(y)

res = adjDx(y(:,:,:,1)) + adjDy(y(:,:,:,2));

Res = fft2c(res);

return;


function res = adjDy(x)
res = x(:,[1,1:end-1],:) - x;
res(:,1,:) = -x(:,1,:);
res(:,end,:) = x(:,end-1,:);

function res = adjDx(x)
res = x([1,1:end-1],:,:) - x;
res(1,:,:) = -x(1,:,:);
res(end,:,:) = x(end-1,:,:);


