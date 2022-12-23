function LoadImages(hObject,handles,control)
% Wei Li, Duke University, June 2010
[file,file_path] = uigetfile('*.mat','MultiSelect','on');
my_var=load([file_path file]);
my_name=fieldnames(my_var);

switch control
    case 1
        handles.Mi=getfield(my_var,my_name{1});
        ss=size(handles.Mi);
        set(handles.FrameSelect, 'Max', ss(3),'SliderStep',[1/ss(3) 2/ss(3)]); 
       % set(handles.Contrast, 'Max', 40,'SliderStep',[1/40 2/40],'value',20); 
        handles.himage1=imshow(abs(handles.Mi(:,:,round(ss(3)/2))),[],'parent',handles.ImageAxes);
        set(handles.FrameSelect, 'value', round(ss(3)/2)); 
        handles.ImageSize=ss;
        UniqueID=get(handles.UniqueID,'string');
        assignin('base',[UniqueID '_magni'],handles.Mi);
        
        set(handles.VariableSelect,'string',[UniqueID '_magni']); 
case 2
        handles.M2=getfield(my_var,my_name{1});
        ss=size(handles.M2);
        handles.himage2=imshow(handles.M2(:,:,round(ss(3)/2)),[],'parent',handles.ImageAxes2);
        UniqueID=get(handles.UniqueID,'string');
        assignin('base',[UniqueID '_phase'],handles.M2);
        set(handles.RightImageLoad,'string',[UniqueID '_phase']); 
case 3
        handles.Mask=getfield(my_var,my_name{1});
        ss=size(handles.Mask);
        handles.himage2=imshow(abs(handles.Mask(:,:,round(ss(3)/2))),[],'parent',handles.ImageAxes2);
        UniqueID=get(handles.UniqueID,'string');
        assignin('base',[UniqueID '_Mask'],handles.Mask);
        set(handles.BrainMaskName,'string',[UniqueID '_Mask']); 
end
guidata(hObject, handles);


