function mythresh(hObject,handles)

level=thresh_tool(get(handles.himage1,'CData'),'gray');
if isempty(level);
    return
end
Mag=handles.Mi(:,:,:,get(handles.Coilslider,'value'));


tic
ImageMask=Mag>level;
ImageLabel = bwlabeln(ImageMask);
stats = regionprops(ImageLabel,'Area');
RegionArea = [stats.Area];
biggest = find(RegionArea==max(RegionArea));
NewMask=(ImageLabel==biggest);
STATS = regionprops(NewMask, 'FilledImage','BoundingBox');
FilledImage=STATS(1,1).FilledImage;
B=STATS(1,1).BoundingBox;
FinalMask=NewMask;
FinalMask((B(2)+0.5):(B(2)+B(5)-0.5),(B(1)+0.5):(B(1)+B(4)-0.5),(B(3)+0.5):(B(3)+B(6)-0.5))=FilledImage;
toc
handles.M2=FinalMask;
handles.FinalMask=FinalMask;

UniqueID=get(handles.UniqueID,'string');
assignin('base',[UniqueID '_MyMask'],double(FinalMask));

set(handles.BrainMaskName,'string',[UniqueID '_MyMask']); 
ss=size(handles.M2);
handles.himage2=imshow(abs(handles.M2(:,:,round(ss(3)/2))),[],'parent',handles.ImageAxes2);
set(handles.Coilslider, 'value', 1); 
guidata(hObject, handles);



