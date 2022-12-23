function [Output, Output_all] =  poly_sensitivity_fit_coils(sens, order, mask_roi)
% poly fit inside the mask

N = size(sens(:,:,1));

if nargin < 3
    mask_roi = ones(N);
end

if nargin < 2      
    order = 5;
end


valid_idx = find(mask_roi);
all_idx = find(ones(size(mask_roi)));

[xx,yy] = meshgrid( linspace(-1,1,N(2)), linspace(-1,1,N(1)) );


x_all_idx = xx(1:end)';
y_all_idx = yy(1:end)';


%select valid indices if mask is used
x_idx = x_all_idx(valid_idx);
y_idx = y_all_idx(valid_idx);

xAll_idx = x_all_idx(all_idx);
yAll_idx = y_all_idx(all_idx);


if(max(size(order))==1)
    order_list = [0:order];
else
    order_list = order;
end


% making regressors
Col = 1;
for ii = 1:length(order_list)
    for jj = 1:(length(order_list)+1-ii)
        Col = Col+1;
    end
end



col = 1;
A = zeros(length(valid_idx), Col);

for ii = 1:length(order_list)
    for jj = 1:(length(order_list)+1-ii)
        x_order = order_list(ii);
        y_order = order_list(jj);

        A(:,col) = (x_idx.^(x_order)).*(y_idx.^(y_order));
        col = col+1;
    end
end


col = 1;
A_all = zeros(length(all_idx), Col);

for ii = 1:length(order_list)
    for jj = 1:(length(order_list)+1-ii)
        x_order = order_list(ii);
        y_order = order_list(jj);

        A_all(:,col) = (xAll_idx.^(x_order)).*(yAll_idx.^(y_order));
        col = col+1;
    end
end


% least squares solution
Output = zeros(size(sens));
Output_all = zeros(size(sens));

for c = 1:size(sens,3)
    sns = sens(:,:,c);
    rimg = sns(valid_idx);

    output = zeros(N);
    coeffs = (pinv(A'*A)*A'*rimg);

    fit = A * coeffs;
    output(valid_idx) = fit;
    Output(:,:,c) = output;
    
    
    fit = A_all * coeffs;
    output_all = zeros(N);
    output_all(all_idx) = fit;
    Output_all(:,:,c) = output_all;
end



end