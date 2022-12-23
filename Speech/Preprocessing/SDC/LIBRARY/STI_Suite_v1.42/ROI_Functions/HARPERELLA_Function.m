function HARPERELLA_Function(hObject,handles,ctrl)

switch ctrl
    case 'HARPERELLA'
        disp(' Starting HARPERELLA processing ...')
        set(handles.status,'string','Starting HARPERELLA processing, please wait ...')
        drawnow
        myvarname=get(handles.RightImageLoad,'string');
        phase=evalin('base', myvarname);

        myvarname=get(handles.BrainMaskName,'string');
        BrainMask=evalin('base', myvarname);


        eval(['SpatialRes=' get(handles.LeftResolution,'string') ';'])
        eval(['padsize=' get(handles.PadSize,'string') ';'])
        eval(['nIter=' get(handles.PhaseIter,'string') ';'])
        eval(['Radius=' get(handles.phaseRadius,'string') ';'])

        [TissuePhase,NewMask]=HARPERELLA(phase,SpatialRes,padsize,BrainMask,nIter,Radius);
        NewMask=PolishMask(NewMask);
        TissuePhase=TissuePhase.*NewMask;
        UniqueID=get(handles.UniqueID,'string');
        assignin('base',[UniqueID '_TissuePhase_H'],TissuePhase);
        assignin('base',[UniqueID '_NewMask_H'],NewMask);

        set(handles.ProcessedPhaseName,'string',[UniqueID '_TissuePhase_H']);
        set(handles.NewMaskName,'string',[UniqueID '_NewMask_H']);
        handles.M2=TissuePhase;
        disp(' HARPERELLA done.')
        set(handles.status,'string','HARPERELLA Done. Now please fill in the QSM paramteters, and click "QSM using LSQR"')
        drawnow
    case 'VSHARP'
        disp(' Starting Laplacian Phase Unwrapping and V-SHARP ...')
        set(handles.status,'string','Starting phase unwrapping and V-SHARP processing, please wait ...')
        drawnow
        myvarname=get(handles.RightImageLoad,'string');
        phase=evalin('base', myvarname);

        myvarname2=get(handles.BrainMaskName,'string');
        BrainMask=evalin('base', myvarname2);

        eval(['SpatialRes=' get(handles.LeftResolution,'string') ';'])
        eval(['padsize=' get(handles.PadSize,'string') ';'])
        eval(['Radius=' get(handles.VSHARPRadius,'string') ';'])
        disp(['[TissuePhase_V,NewMask_V]=V_SHARP(' myvarname ',' myvarname2 ',' get(handles.VSHARPRadius,'string')  ','  get(handles.PadSize,'string') ','  get(handles.LeftResolution,'string') ');'])

        Unwrapped_Phase=LaplacianPhaseUnwrap(phase,SpatialRes,padsize);
        [TissuePhase,NewMask,TissuePhaseDecov]=V_SHARP(Unwrapped_Phase,BrainMask,Radius,padsize,SpatialRes);
        NewMask=PolishMask(NewMask);
        if get(handles.Deconvolution,'value');
            TissuePhase=TissuePhaseDecov.*NewMask;
        else
            TissuePhase=TissuePhase.*NewMask;
        end
        
        UniqueID=get(handles.UniqueID,'string');
        assignin('base',[UniqueID '_TissuePhase_V'],TissuePhase);
        assignin('base',[UniqueID '_NewMask_V'],NewMask);

        set(handles.ProcessedPhaseName,'string',[UniqueID '_TissuePhase_V']);
        set(handles.NewMaskName,'string',[UniqueID '_NewMask_V']);
        handles.M2=TissuePhase;
        disp(' V-SHARP done.')
        set(handles.status,'string','Phase unwrapping and V-SHARP Done. Now please fill in the QSM paramteters, and click "QSM using LSQR"')
        drawnow
    case 'QSM'
        disp(' Starting QSM using LSQR ...')
        set(handles.status,'string','Starting QSM processing, please wait ...')
         drawnow
        myvarname=get(handles.ProcessedPhaseName,'string');
        TissuePhase=evalin('base', myvarname);

        myvarname2=get(handles.NewMaskName,'string');
        NewMask=evalin('base', myvarname2);

        eval(['SpatialRes=' get(handles.VoxelSizeForQSM,'string') ';'])
        eval(['padsize=' get(handles.PadSizeForQSM,'string') ';'])
        eval(['H=' get(handles.H_Vector,'string') ';'])
        eval(['niter=' get(handles.Niter,'string') ';'])
        eval(['B0=' get(handles.B0Value,'string') ';'])
        eval(['TE=' get(handles.TE_value,'string') ';'])
        
        SF=ScalingFactor(B0,TE);
        disp(['X = QSM_LSQR(' myvarname ',' myvarname2 ',' get(handles.H_Vector,'string') ',' get(handles.VoxelSizeForQSM,'string') ',' get(handles.PadSizeForQSM,'string') ',' get(handles.Niter,'string') ');'])

        X = QSM_LSQR(TissuePhase,NewMask,H,SpatialRes,padsize,niter);
        
        
        FrequencyShift=TissuePhase*SF.Freq;
        Susceptibility=X*SF.X;

        UniqueID=get(handles.UniqueID,'string');
        assignin('base',[UniqueID '_Susceptibility'],Susceptibility);
        assignin('base',[UniqueID '_FrequencyShift'],FrequencyShift);
        assignin('base',[UniqueID '_ScallingFactor'],SF);
        handles.Mi=FrequencyShift;
        handles.M2=Susceptibility;
        set(handles.status,'string','QSM done. All variables are saved in workspace, Starting with Unique ID. Have a nice day!')
        drawnow
end

guidata(hObject, handles);
SliceSelection(hObject,handles);
AdjustIntensity(hObject,handles,3)
