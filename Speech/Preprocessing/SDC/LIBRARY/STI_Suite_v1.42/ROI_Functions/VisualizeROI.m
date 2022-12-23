function VisualizeROI(hObject,handles,ctrl)
try
            myvarname=get(handles.VariableSelect,'string');
            handles.Mi=evalin('base', myvarname);
            ss=size(handles.Mi);
catch 
    set(handles.status,'string','Error! No Image Selected ...')
    return
end
set(handles.FrameSelect, 'Max', ss(3),'SliderStep',[1/ss(3) 2/ss(3)]); 
set(handles.FrameSelect, 'visible','on'); 

handles.M2=ones(size(handles.Mi,1),size(handles.Mi,2),size(handles.Mi,3));


handles.img1(:,:,1)=real(handles.M2(:,:,round(ss(3)/2)));
handles.img1(:,:,3)=0;
handles.himage1=imshow(handles.img1,'parent',handles.ImageAxes);
handles.himage2=imshow(real(handles.Mi(:,:,round(ss(3)/2))),[],'parent',handles.ImageAxes2);
AlphaMap=handles.M2(:,:,round(ss(3)/2));
AlphaMap=(AlphaMap>0);
set(handles.himage2,'AlphaData',AlphaMap);
set(handles.himage1,'CDataMapping','scaled')
if get(handles.Grey,'value')
    colormap gray
else 
    colormap jet
end

sss=size(handles.Mi,4);
if sss>1
    set(handles.Coilslider,'Max', sss,'SliderStep',[1/sss 2/sss]); 
    if get(handles.Coilslider, 'value')>sss;
        set(handles.Coilslider, 'value', sss/2); 
        
    end
    set(handles.Coilslider,'value', 1); 
end

Xlim2=get (handles.ImageAxes2,'Xlim');
Ylim2=get (handles.ImageAxes2,'ylim');

XYLimMax=max([Xlim2(2)-Xlim2(1) Ylim2(2)-Ylim2(1)]);

set (handles.ImageAxes2,'Xlim',[0 XYLimMax]+0.5,'Ylim',[0 XYLimMax]+0.5);
set (handles.ImageAxes,'Xlim',[0 XYLimMax]+0.5,'Ylim',[0 XYLimMax]+0.5);
set(handles.FrameSelect, 'value', round(ss(3)/2)); 
set(handles.status,'string','Images loaded.')
handles.ImageAxisNum=3;
handles.NumberSelect=1;
handles.baseAlpha=0.5;
guidata(hObject, handles);
