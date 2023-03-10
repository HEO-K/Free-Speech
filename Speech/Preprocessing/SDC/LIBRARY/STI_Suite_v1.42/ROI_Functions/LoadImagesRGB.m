function LoadImagesRGB(hObject,handles,ctrl)
% Wei Li, Duke University, June 2010
[file,file_path] = uigetfile('*.mat','MultiSelect','on');
my_var=load([file_path file]);
my_name=fieldnames(my_var);

switch ctrl
    case 1
        handles.Mi=getfield(my_var,my_name{1});
        ss=size(handles.Mi);
        Image=squeeze(handles.Mi(:,:,round(ss(3)/2),:));
    case 2
        handles.M2=getfield(my_var,my_name{1});
        ss=size(handles.M2);
        Image=squeeze(handles.M2(:,:,round(ss(3)/2),:));
end

set(handles.FrameSelect3D, 'Max', ss(3),'SliderStep',[1/ss(3) 2/ss(3)]); 

switch ctrl
    case 1

        handles.LeftImax=max(Image(:));
        handles.LeftImin=min(Image(:));

        Image=(Image-handles.LeftImin)/(handles.LeftImax-handles.LeftImin);
        handles.LeftImax1=str2double(get(handles.RGBhigh,'string'));
        handles.LeftImin1=str2double(get(handles.RGBlow,'string'));

        Image=(Image-handles.LeftImin1)/(handles.LeftImax1-handles.LeftImin1);

        Image(Image>1)=1;
        Image(Image<0)=0;        

        handles.himage1=imshow(Image,[],'parent',handles.ImageAxes);
    case 2

        handles.RightImax=max(Image(:));
        handles.RightImin=min(Image(:));
        Image=(Image-handles.RightImin)/(handles.RightImax-handles.RightImin);

        handles.RightImax1=str2double(get(handles.RGBhigh,'string'));
        handles.RightImin1=str2double(get(handles.RGBlow,'string'));

        Image=(Image-handles.RightImin1)/(handles.RightImax1-handles.RightImin1);

        Image(Image>1)=1;
        Image(Image<0)=0;
        handles.himage2=imshow(Image,[],'parent',handles.ImageAxes2);
end


set(handles.FrameSelect3D, 'value', round(ss(3)/2)); 
set(handles.status,'string','Images loaded.')
guidata(hObject, handles);
