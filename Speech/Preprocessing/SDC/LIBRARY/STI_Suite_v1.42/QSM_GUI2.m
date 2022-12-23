function varargout = QSM_GUI2(varargin)
% Wei Li, Duke University, May 2010
% Wei Li, Updated on 10/28/2010 to include 4D display functionality
%


% Begin initialization code - DO NOT EDIT
gui_Singleton = 1;
gui_State = struct('gui_Name',       mfilename, ...
                   'gui_Singleton',  gui_Singleton, ...
                   'gui_OpeningFcn', @QSM_GUI2_OpeningFcn, ...
                   'gui_OutputFcn',  @QSM_GUI2_OutputFcn, ...
                   'gui_LayoutFcn',  [] , ...
                   'gui_Callback',   []);
if nargin && ischar(varargin{1})
    gui_State.gui_Callback = str2func(varargin{1});
end

if nargout
    [varargout{1:nargout}] = gui_mainfcn(gui_State, varargin{:});
else
    gui_mainfcn(gui_State, varargin{:});
end
% End initialization code - DO NOT EDIT


% --- Executes just before QSM_GUI2 is made visible.
function QSM_GUI2_OpeningFcn(hObject, eventdata, handles, varargin)
% This function has no output args, see OutputFcn.
% hObject    handle to figure
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
% varargin   command line arguments to QSM_GUI2 (see VARARGIN)

% Choose default command line output for QSM_GUI2

handles.output = hObject;
handles.currentContour=1;
try
    set(handles.VariableSelect,'string',varargin{1});
    Visualize(hObject,handles,1)
end
% UIWAIT makes QSM_GUI2 wait for user response (see UIRESUME)
% uiwait(handles.figure1);
guidata(hObject, handles);

% --- Outputs from this function are returned to the command line.
function varargout = QSM_GUI2_OutputFcn(hObject, eventdata, handles) 
% varargout  cell array for returning output args (see VARARGOUT);
% hObject    handle to figure
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Get default command line output from handles structure
varargout{1} = handles.output;


function LoadImages_Callback(hObject, eventdata, handles)
LoadImages(hObject,handles,1);

function Transforms_Callback(hObject, eventdata, handles)
Transforms(hObject,handles,1);

function Thres_Callback(hObject, eventdata, handles)
mythresh(hObject,handles);
UniqueID=get(handles.UniqueID,'string');
assignin('base',[UniqueID '_MyMask'],handles.M2);


function LoadBinFIle_Callback(hObject, eventdata, handles)
LoadBinFile(hObject,handles,2);

function FrameSelect_Callback(hObject, eventdata, handles)

value = round(get(hObject,'Value'));
set(hObject,'Value',value);
set(handles.Frame,'String',num2str(value));
SliceSelection(hObject,handles);

function FrameSelect_CreateFcn(hObject, eventdata, handles)
if isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor',[.9 .9 .9]);
end

function Frame_CreateFcn(hObject, eventdata, handles)

if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end

function FrameSelect_ButtonDownFcn(hObject, eventdata, handles)
SliceSelection(hObject,handles);

function SaveMag2Nii_Callback(hObject, eventdata, handles)
SaveMag2Nii(hObject,handles,1);

function Intensity_Callback(hObject, eventdata, handles)
AdjustIntensity(hObject,handles,1);

function Intensity_CreateFcn(hObject, eventdata, handles)
if isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor',[.9 .9 .9]);
end


function Contrast_Callback(hObject, eventdata, handles)
AdjustIntensity(hObject,handles,2);

function Contrast_CreateFcn(hObject, eventdata, handles)
if isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor',[.9 .9 .9]);
end

function VariableSelect_Callback(hObject, eventdata, handles)
%set(handles.nDims,'String','Intensity');
Visualize(hObject,handles,1);

function VariableSelect_CreateFcn(hObject, eventdata, handles)
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end

function Disp_SelectionChangeFcn(hObject, eventdata, handles)
SliceSelection(hObject,handles);

function ColorScheme_SelectionChangeFcn(hObject, eventdata, handles)
ColorScheme(hObject,handles);

function AutoScale1_Callback(hObject, eventdata, handles)
AdjustIntensity(hObject,handles,3)

function Save2MatFile_Callback(hObject, eventdata, handles)
Save2MatFile(hObject,handles);

function ZeroPad_Callback(hObject, eventdata, handles)
ZeroPad(hObject,handles,1);

function CalculatePhase_Callback(hObject, eventdata, handles)
Transforms(hObject,handles,3);

function RestoreOrigionalSize_Callback(hObject, eventdata, handles)
ZeroPad(hObject,handles,2);

function Assign2Base_Callback(hObject, eventdata, handles)
Assign2Base(hObject,handles,1);

function Assign2Base_CreateFcn(hObject, eventdata, handles)
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end

function CalcMagn_Callback(hObject, eventdata, handles)
Transforms(hObject,handles,2);

function LoadNiiFile_Callback(hObject, eventdata, handles)
Normalization(hObject,handles,3);

function Load2ndImag_Callback(hObject, eventdata, handles)
LoadImages(hObject,handles,2);




function RightImageLoad_Callback(hObject, eventdata, handles)
Visualize(hObject,handles,2);

function RightImageLoad_CreateFcn(hObject, eventdata, handles)

if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end

function RightImageSave_Callback(hObject, eventdata, handles)
Assign2Base(hObject,handles,2);

function RightImageSave_CreateFcn(hObject, eventdata, handles)
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end

function FrameSelect3D_Callback(hObject, eventdata, handles)

value = floor(get(hObject,'Value'));
set(handles.Frame,'String',num2str(value));

SliceSelection3D(hObject,handles);

function FrameSelect3D_CreateFcn(hObject, eventdata, handles)
if isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor',[.9 .9 .9]);
end


function Load3DRgbEdit_Callback(hObject, eventdata, handles)
set(handles.nDims,'String','RGB');

VisualizeRGB(hObject,handles,1);

function Load3DRgbEdit_CreateFcn(hObject, eventdata, handles)
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


function AdjustContrastButton_Callback(hObject, eventdata, handles)
AdjustIntensity(hObject,handles,5);


% --- Executes on button press in FollowLightContrast.
function FollowLightContrast_Callback(hObject, eventdata, handles)
AdjustIntensity(hObject,handles,6);



% --- Executes on button press in AdjustContrastR.
function AdjustContrastR_Callback(hObject, eventdata, handles)
AdjustIntensity(hObject,handles,7);


% --- Executes on button press in FollowRightContrast.
function FollowRightContrast_Callback(hObject, eventdata, handles)
AdjustIntensity(hObject,handles,8);

% --- Executes when selected object is changed in FlipChange.

% --- Executes on button press in FlipUpDown.
function FlipUpDown_Callback(hObject, eventdata, handles)
SliceSelection(hObject,handles);



% --- Executes on button press in Rotate90.
function Rotate90_Callback(hObject, eventdata, handles)
SliceSelection(hObject,handles);

% --- Executes on slider movement.
function Coilslider_Callback(hObject, eventdata, handles)

value = round(get(hObject,'Value'));
set(hObject,'Value',value);
set(handles.CoilNum,'String',num2str(value));
SliceSelection(hObject,handles);



% --- Executes during object creation, after setting all properties.
function Coilslider_CreateFcn(hObject, eventdata, handles)
if isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor',[.9 .9 .9]);
end


% --- Executes on key press with focus on FrameSelect and none of its controls.
function FrameSelect_KeyPressFcn(hObject, eventdata, handles)

switch eventdata.Character
    case '4'
        value = floor(get(handles.FrameSelect,'Value'));
        if  value <2
        else
            set(handles.FrameSelect,'Value',value-1);
            set(handles.Frame,'String',num2str(value-1));
            SliceSelection(hObject,handles);
        end
        
    case '6'
        value = floor(get(handles.FrameSelect,'Value'));
        if  value > get(handles.FrameSelect,'max')-1
        else
            set(handles.FrameSelect,'Value',value+1);
            set(handles.Frame,'String',num2str(value+1));
           SliceSelection(hObject,handles);
        end
    case '8' 
        value = floor(get(handles.Coilslider,'Value'));
        if  value > get(handles.Coilslider,'max')-1
        else
            set(handles.Coilslider,'Value',value+1);
            set(handles.CoilNum,'String',num2str(value+1));
            SliceSelection(hObject,handles);
        end
    case '2'
        value = floor(get(handles.Coilslider,'Value'));
        if value<2 
        else
            set(handles.Coilslider,'Value',value-1);
            set(handles.CoilNum,'String',num2str(value-1));
            SliceSelection(hObject,handles);
        end
        
end



function Load3DRgbEditRight_Callback(hObject, eventdata, handles)
VisualizeRGB(hObject,handles,2);

% --- Executes during object creation, after setting all properties.
function Load3DRgbEditRight_CreateFcn(hObject, eventdata, handles)
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end




function RGBlow_Callback(hObject, eventdata, handles)
SliceSelection3D(hObject,handles);



% --- Executes during object creation, after setting all properties.
function RGBlow_CreateFcn(hObject, eventdata, handles)

if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function RGBhigh_Callback(hObject, eventdata, handles)
SliceSelection3D(hObject,handles);


% --- Executes during object creation, after setting all properties.
function RGBhigh_CreateFcn(hObject, eventdata, handles)

if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function Frame_Callback(hObject, eventdata, handles)
framenumber=str2double(get(handles.Frame,'string'));
set(handles.FrameSelect,'value',framenumber);
SliceSelection(hObject,handles);


function RightLow_Callback(hObject, eventdata, handles)
SliceSelection3D(hObject,handles);


% --- Executes during object creation, after setting all properties.
function RightLow_CreateFcn(hObject, eventdata, handles)
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function RightHigh_Callback(hObject, eventdata, handles)
SliceSelection3D(hObject,handles);

% --- Executes during object creation, after setting all properties.
function RightHigh_CreateFcn(hObject, eventdata, handles)
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end

% --- Executes on key press with focus on Coilslider and none of its controls.
function Coilslider_KeyPressFcn(hObject, eventdata, handles)


% --- Executes when selected object is changed in ImagePlane.
function ImagePlane_SelectionChangeFcn(hObject, eventdata, handles)

switch get(hObject,'string')
    case 'Y-Z'
        handles.ImageAxisNum=1;
    case 'X-Z'
        handles.ImageAxisNum=2;
    case 'X-Y'
        handles.ImageAxisNum=3;
end
guidata(hObject, handles);       

SliceSelection(hObject,handles);


% --- Executes during object creation, after setting all properties.
function ImagePlane_CreateFcn(hObject, eventdata, handles)
handles.ImageAxisNum=3;
guidata(hObject, handles);       


% --- Executes on button press in SaveMag2Nii2.
function SaveMag2Nii2_Callback(hObject, eventdata, handles)
SaveMag2Nii(hObject,handles,2);
% hObject    handle to SaveMag2Nii2 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)


% --- Executes on button press in LoadBinFIle2.
function LoadBinFIle2_Callback(hObject, eventdata, handles)
LoadBinFile(hObject,handles,4);

% hObject    handle to LoadBinFIle2 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)


% --- Executes on button press in readmrdata.
function readmrdata_Callback(hObject, eventdata, handles)
LoadBinFile(hObject,handles,5);



% --- Executes on button press in loadphase.
function loadphase_Callback(hObject, eventdata, handles)
LoadBinFile(hObject,handles,6);



% --- Executes when selected object is changed in uipanel10.
function uipanel10_SelectionChangeFcn(hObject, eventdata, handles)

set(handles.Coilslider, 'value', 1); 
switch get(hObject,'string')
    case 'PhiFiltered'
        handles.M2=handles.PhiFiltered;
    case 'UpdatedMask'
        handles.M2=handles.FinalMask;
    case 'X'
        handles.M2=handles.X;
end
guidata(hObject, handles);       

if strcmp(get(handles.nDims,'string'),'Intensity')
    SliceSelection(hObject,handles);
else
    SliceSelection3D(hObject,handles);
end
AdjustIntensity(hObject,handles,3)




% --------------------------------------------------------------------
function uitoggletool3_ClickedCallback(hObject, eventdata, handles)
% hObject    handle to uitoggletool3 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)


% --- Executes on button press in Scaling.
% function Scaling_Callback(hObject, eventdata, handles)

% SliceSelection(hObject,handles);


% --------------------------------------------------------------------
function uitoggletool3_OffCallback(hObject, eventdata, handles)
set(handles.ImageAxes2,'XLim',get(handles.ImageAxes,'XLim'),...
                       'YLim',get(handles.ImageAxes,'YLim'));


% --------------------------------------------------------------------
function uitoggletool5_OffCallback(hObject, eventdata, handles)
set(handles.ImageAxes2,'XLim',get(handles.ImageAxes,'XLim'),...
                       'YLim',get(handles.ImageAxes,'YLim'));




% --- Executes on button press in checkbox5.
function checkbox5_Callback(hObject, eventdata, handles)
SliceSelection(hObject,handles);



function LeftResolution_Callback(hObject, eventdata, handles)

phaseres=get(handles.LeftResolution,'string');
set(handles.VoxelSizeForQSM,'string',phaseres);

% hObject    handle to LeftResolution (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of LeftResolution as text
%        str2double(get(hObject,'String')) returns contents of LeftResolution as a double


% --- Executes during object creation, after setting all properties.
function LeftResolution_CreateFcn(hObject, eventdata, handles)
% hObject    handle to LeftResolution (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function RightResolution_Callback(hObject, eventdata, handles)
% hObject    handle to RightResolution (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of RightResolution as text
%        str2double(get(hObject,'String')) returns contents of RightResolution as a double


% --- Executes during object creation, after setting all properties.
function RightResolution_CreateFcn(hObject, eventdata, handles)
% hObject    handle to RightResolution (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end




% --- Executes on button press in AutoScale.
function AutoScale_Callback(hObject, eventdata, handles)
AdjustIntensity(hObject,handles,3)






function BrainMaskName_Callback(hObject, eventdata, handles)
% hObject    handle to BrainMaskName (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of BrainMaskName as text
%        str2double(get(hObject,'String')) returns contents of BrainMaskName as a double


% --- Executes during object creation, after setting all properties.
function BrainMaskName_CreateFcn(hObject, eventdata, handles)
% hObject    handle to BrainMaskName (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


% --- Executes on button press in pushbutton29.
function pushbutton29_Callback(hObject, eventdata, handles)
% hObject    handle to pushbutton29 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)


% --- Executes on button press in pushbutton30.
function pushbutton30_Callback(hObject, eventdata, handles)
% hObject    handle to pushbutton30 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)



function PadSize_Callback(hObject, eventdata, handles)
% hObject    handle to PadSize (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of PadSize as text
%        str2double(get(hObject,'String')) returns contents of PadSize as a double


% --- Executes during object creation, after setting all properties.
function PadSize_CreateFcn(hObject, eventdata, handles)
% hObject    handle to PadSize (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function H_Vector_Callback(hObject, eventdata, handles)
% hObject    handle to H_Vector (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of H_Vector as text
%        str2double(get(hObject,'String')) returns contents of H_Vector as a double


% --- Executes during object creation, after setting all properties.
function H_Vector_CreateFcn(hObject, eventdata, handles)
% hObject    handle to H_Vector (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


% --- Executes on button press in pushbutton31.
function pushbutton31_Callback(hObject, eventdata, handles)
% hObject    handle to pushbutton31 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)


% --- Executes on button press in HARPERELLA.
function HARPERELLA_Callback(hObject, eventdata, handles)
% hObject    handle to HARPERELLA (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
HARPERELLA_Function(hObject,handles,'HARPERELLA')


function ProcessedPhaseName_Callback(hObject, eventdata, handles)
% hObject    handle to ProcessedPhaseName (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of ProcessedPhaseName as text
%        str2double(get(hObject,'String')) returns contents of ProcessedPhaseName as a double


% --- Executes during object creation, after setting all properties.
function ProcessedPhaseName_CreateFcn(hObject, eventdata, handles)
% hObject    handle to ProcessedPhaseName (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function NewMaskName_Callback(hObject, eventdata, handles)
% hObject    handle to NewMaskName (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of NewMaskName as text
%        str2double(get(hObject,'String')) returns contents of NewMaskName as a double


% --- Executes during object creation, after setting all properties.
function NewMaskName_CreateFcn(hObject, eventdata, handles)
% hObject    handle to NewMaskName (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function PadSizeForQSM_Callback(hObject, eventdata, handles)
% hObject    handle to PadSizeForQSM (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of PadSizeForQSM as text
%        str2double(get(hObject,'String')) returns contents of PadSizeForQSM as a double


% --- Executes during object creation, after setting all properties.
function PadSizeForQSM_CreateFcn(hObject, eventdata, handles)
% hObject    handle to PadSizeForQSM (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function VoxelSizeForQSM_Callback(hObject, eventdata, handles)
% hObject    handle to VoxelSizeForQSM (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of VoxelSizeForQSM as text
%        str2double(get(hObject,'String')) returns contents of VoxelSizeForQSM as a double


% --- Executes during object creation, after setting all properties.
function VoxelSizeForQSM_CreateFcn(hObject, eventdata, handles)
% hObject    handle to VoxelSizeForQSM (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


% --- Executes on button press in QSM_LSQR.
function QSM_LSQR_Callback(hObject, eventdata, handles)
% hObject    handle to QSM_LSQR (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

HARPERELLA_Function(hObject,handles,'QSM')


function B0Value_Callback(hObject, eventdata, handles)
% hObject    handle to B0Value (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of B0Value as text
%        str2double(get(hObject,'String')) returns contents of B0Value as a double


% --- Executes during object creation, after setting all properties.
function B0Value_CreateFcn(hObject, eventdata, handles)
% hObject    handle to B0Value (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function TE_value_Callback(hObject, eventdata, handles)
% hObject    handle to TE_value (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of TE_value as text
%        str2double(get(hObject,'String')) returns contents of TE_value as a double


% --- Executes during object creation, after setting all properties.
function TE_value_CreateFcn(hObject, eventdata, handles)
% hObject    handle to TE_value (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


% --- Executes on button press in pushbutton34.
function pushbutton34_Callback(hObject, eventdata, handles)
% hObject    handle to pushbutton34 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)


% --- Executes on button press in pushbutton35.
function pushbutton35_Callback(hObject, eventdata, handles)
% hObject    handle to pushbutton35 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)



function UniqueID_Callback(hObject, eventdata, handles)
% hObject    handle to UniqueID (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of UniqueID as text
%        str2double(get(hObject,'String')) returns contents of UniqueID as a double


% --- Executes during object creation, after setting all properties.
function UniqueID_CreateFcn(hObject, eventdata, handles)
% hObject    handle to UniqueID (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function Niter_Callback(hObject, eventdata, handles)
% hObject    handle to Niter (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of Niter as text
%        str2double(get(hObject,'String')) returns contents of Niter as a double


% --- Executes during object creation, after setting all properties.
function Niter_CreateFcn(hObject, eventdata, handles)
% hObject    handle to Niter (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function PhaseIter_Callback(hObject, eventdata, handles)
% hObject    handle to PhaseIter (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of PhaseIter as text
%        str2double(get(hObject,'String')) returns contents of PhaseIter as a double


% --- Executes during object creation, after setting all properties.
function PhaseIter_CreateFcn(hObject, eventdata, handles)
% hObject    handle to PhaseIter (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function phaseRadius_Callback(hObject, eventdata, handles)
% hObject    handle to phaseRadius (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of phaseRadius as text
%        str2double(get(hObject,'String')) returns contents of phaseRadius as a double


% --- Executes during object creation, after setting all properties.
function phaseRadius_CreateFcn(hObject, eventdata, handles)
% hObject    handle to phaseRadius (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end
