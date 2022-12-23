function Assign2BaseROI_Gray(hObject,handles,ctrl)
switch ctrl 
    case 1
            TempROIvalues=ones(size(handles.M2));
            myvarname=get(handles.RightImageLoad,'string');
            MyROIAnalysis=evalin('base', myvarname);
            MyROIs=MyROIAnalysis.ROI;
            
            for ii=1:9
                TempROIvalues(MyROIs{ii})=ii*0.01+handles.baseAlpha;
            end            
            handles.M2=TempROIvalues;
            guidata(gcbo,handles);
    case 2
        DataSetNumber=round(str2double(get(handles.CoilNum,'String')));
        Imag=handles.Mi(:,:,:,DataSetNumber);
        Imag2=zeros(size(Imag));
        MyROIs=handles.M2;
        for ii=1:9
            ROI_ii=find(MyROIs==ii*0.01+handles.baseAlpha);
            ROI_Value_ii=Imag(ROI_ii);
            MyROIAnalysis.ROI{ii}=ROI_ii;
            MyROIAnalysis.data{ii}=ROI_Value_ii;
            MyROIAnalysis.mean(ii)=mean(ROI_Value_ii);
            Imag2(ROI_ii)=ii;
        end
        
        ROIvalues=(MyROIAnalysis.mean);
        ROIvalues(isnan(ROIvalues))=[];
        set(handles.status,'string',num2str(ROIvalues))
        assignin('base','Roivalue',ROIvalues);
        
        myvarname=[get(handles.RightImageSave,'string') '_struct' ];
        myvarname1=[get(handles.RightImageSave,'string') '_image'];
        assignin('base',myvarname,MyROIAnalysis);
        assignin('base',myvarname1,Imag2);
    case 3
        [file,file_path] = uigetfile('*.mat');
        try
        my_var=load([file_path file]);
        catch
            return
        end
        my_name=fieldnames(my_var);
        TempROIvalues=ones(size(handles.M2));
        MyROIAnalysis=getfield(my_var,my_name{1});
        MyROIs=MyROIAnalysis.ROI;
        for ii=1:9
            TempROIvalues(MyROIs{ii})=ii*0.01+handles.baseAlpha;
        end            
        handles.M2=TempROIvalues;
        guidata(gcbo,handles);
    case 4
        DataSetNumber=round(str2double(get(handles.CoilNum,'String')));
        Imag1=handles.Mi(:,:,:);
        MyROIs=handles.M2;
        for ii=1:9
            ROI_ii=find(MyROIs==ii*0.01+handles.baseAlpha);
            ROI_Value_ii=-Imag1(ROI_ii);
            MyROIAnalysis.ROI{ii}=ROI_ii;
            MyROIAnalysis.Chi{ii}=ROI_Value_ii;
            MyROIAnalysis.ChiMean(ii)=mean(ROI_Value_ii);
        end
        uisave('MyROIAnalysis','myROI');
end