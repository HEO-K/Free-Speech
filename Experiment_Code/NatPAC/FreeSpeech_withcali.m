% Shimlab_localizer/7T_FreeSpeech 경로에서 코드 시작
% 피험자 bids 번호와 세션(01,02,...)번호를 알맞게 입력해야 한다.
% 세션 번호에 맞는 실험이 자동으로 시작된다.
% 만약 MOVIE run, 3 topics run (세션 02,03,04,09,10)이라면 left time을 입력해야 한다.
% left time은 스캔 가능한 남은 시간을 분 단위로 입력하고, 커맨드 창에 나오는 TR을 시퀀스에 적용한다.
% left time을 입력한 run에서는 피험자가 말을 일찍 끝낼 수 있으니 소리 키고, 화면에 집중하자. 끝나면 시퀀스 종료한다.
% left_TR = (floor(left*60/8)*8)/1.6+10+25



%% Initialize
close all; clear all; clear mex;
IOPort('Closeall'); Screen('Close'); Screen('Closeall');
addpath(genpath(fullfile(pwd, '_COMMON')));


% Sub number
subName = input('\n\nSub No(ex. 001, 002, ...)                    >> ','s');
if length(subName) < 1
    subName = 'test';
end


% Task 번호 
SesNum_raw = input('\nSession No(01~14)                            >> ','s');
SesNum = SesNum_raw(~isletter(SesNum_raw));   % 숫자만 인식
if SesNum == "01" || SesNum == "11"
    task = 'FREE';
elseif SesNum == "10"
    task = 'TOPICS';
elseif SesNum == "07" || SesNum == "08" || SesNum == "13" || SesNum=="14"
    task = "MC";
else
    task = 'MOVIE';
end
runtypes = ["TA", "MOV", "MOV", "MOV", "MC", "MC", "MC", "MC", "MOV", "FS","MC", "MC", "MC", "MC"];
Speech_type = runtypes(str2num(SesNum));


% 저장되는 파일
sfile   = fullfile(pwd, '_CSV', strcat('sub-',subName,'_ses-',SesNum_raw,'_task-speech',task,'_run-1_events.csv'));
time_matrix = ["SubNum", "RunNum", "Cond", "Onset", "Dur"];
afile   = fullfile(pwd, '_AUDIO', strcat('sub-',subName,'_ses-',SesNum_raw,'_task-speech',task,'_run-1_audio.wav'));


% Listen for scanner
listen = str2double(input('\nListen for scanner 1=yes, 2=no               >> ','s'));
if isnan(listen)
    listen = 2;
end


% 일부 과제의 남은 시간 설정
if Speech_type == "MOV" || Speech_type == "FS" 
    left = input('\nLeft time(minutes)                           >> ','s');
    left = num2str(round(str2num(left)));
    msg = sprintf("중앙의 흰 점이 사라진 시점부터 다시 흰 점이 나타나기 전까지\n(최대 %s분 동안)\n\n", left);
else
    left = '10';
end
left_TR = (floor(str2num(left)*60/8)*8)/1.6+10+25


% Instructs
FS_insts = "세 가지 주제에 대해,\n자유로운 순서대로 이야기하기.";
FS_insts_set = ["기억나는 화났거나 짜증났던 경험을 최대한 자세히 회상하기", "사형 제도를 찬성하는가? 그 이유는?", "친구(들)을 최대한 자세히 묘사하기. (외형, 성격, 관계 등등)"];
FS_insts_set = FS_insts_set(randperm(3));
FS_insts_sub = "\n\n주제1: "+FS_insts_set(1)+"\n주제2: "+FS_insts_set(2)+"\n주제3: "+FS_insts_set(3);
FS_insts = FS_insts+FS_insts_sub+"\n\n전부 말했다면, 1번 버튼 누르기.";

MOV_insts = "방금 본 영화 내용을 시간 순서대로 이야기하기.\n\n각 장면마다\n먼저 장면의 내용을 최대한 자세히 설명한 후,\n나의 생각인 해석을 이야기하기.\n\n전부 말했다면, 1번 버튼 누르기.";
MC_insts = "중앙의 흰 점이 사라진 시점부터 다시 흰 점이 나타나기 전까지\n(10분 동안)\n\n이전에 진행했던 마인크래프트 과제에 대해 자유롭게 이야기하기.\n\n\n\n마인크래프트 과제에 대해 최선을 다해 전부 말했음에도\n시간이 남으면 원하는 주제에 대해 자유롭게 이야기하기.";
if Speech_type == "FS"
    msg = msg + FS_insts;
elseif Speech_type == "MC"
    msg = MC_insts;
elseif Speech_type == "MOV"
    msg = msg + MOV_insts;
elseif Speech_type == "TA"
    msg = "중앙의 흰 점이 사라진 시점부터 다시 흰 점이 나타나기 전까지\n(10분 동안)\n\n마음 속에 떠오르는 생각을 자유롭게 이야기하기.\n\n(여러 가지 다른 주제에 대해 이야기 할 것을 권장합니다.\n보이는 것, 들리는 것, 몸에서 느껴지는 감각 등\n그때그때 생각을 사로잡는 것에 대해 이야기하셔도 됩니다.)\n\n";
end



%% Keyborad and Input Device Setup
% [keyboardIndex, deviceName, allInfo] = GetKeyboardIndices;
device(1).product = 'Magic Keyboard with Numeric Keypad';
device(1).vendorID= 76;
% % ===== Participant
device(2).product = '932';
device(2).vendorID= [1240 6171]; % 6171 ;
% ===== Scanner
device(3).product = 'KeyWarrior8 Flex';
device(3).vendorID= 1984;

if listen == 1
    Experimenter = IDKeyboards(device(1));
    try
        Participant = IDKeyboards(device(2));
        Scanner = IDKeyboards(device(3));  % experimenter manually press 's'(space) signal
    catch
        Scanner = IDKeyboards(device(3));
        Participant = IDKeyboards(device(1)); 
    end
else
    % test in 7T room, without MRI
    Experimenter = IDKeyboards(device(1));
    Scanner = IDKeyboards(device(1));
    Participant = IDKeyboards(device(1));
end

% keyboard
KbName('UnifyKeyNames');
syncNum = KbName('s');
Abort = KbName('q');
Space = KbName('space');



%% Screen Settings
wininfo = Screen('Resolution', 0);   % width,heigth,pixelSize,hz
screenid = max(Screen('Screens'));
%screenid = 0;

Screen('Preference', 'SkipSyncTests', 1);


% Color Setting
white = WhiteIndex(screenid);
black = BlackIndex(screenid); % pixel value for black
gray = (white+black)/2;
blue = [10 10 235];
red = [235 10 10];
green = [10 235 10];
fontsize = 60;


% Window Setting
if listen == 1
    [win,rect] = Screen('OpenWindow', screenid, black);
    % assert(screenRect(3)==1600 && screenRect(4)==1000, 'The resolution is not 1600*1000');
    % full screen propixx [0 0 1920 1080]
    HideCursor;
elseif listen == 2
    [win,rect] = Screen('OpenWindow', screenid, black, [0 0 1600 1000]);   % demi screen for mac-notebook
end

fliprate = Screen('GetFlipInterval', win);  % estimate of the monitor flip interval
priorityLevel=MaxPriority(win);
Priority(priorityLevel); 



%% Audio Recording
% check audio device info using "PsychPortAudio('GetDevices')"
% Sound recording: Preallocate an internal audio recording  buffer with a capacity of 10 seconds
%'Open' [deviceid] [mode] [reqlatencyclass] [frequency] [channels]
if listen == 1
    InitializePsychSound;
    pahandle = PsychPortAudio('Open',2,2,0,44100,2);
    PsychPortAudio('GetAudioData', pahandle, 1800);
end



%% Check Subject's State
% 마인크래프트 제외 전부 실행
if Speech_type ~= "MC"
    Screen(win, 'FillRect', gray);
    Press_1 = KbName('1!');
    Press_2 = KbName('2@');

    inst_img = imread('7T_proj_general_inst_00.png');
    inst_tex = Screen('MakeTexture', win, inst_img);
    inst_press1_img = imread('7T_proj_general_inst_01.png');
    inst_press1_tex = Screen('MakeTexture', win, inst_press1_img);
    inst_press2_img = imread('7T_proj_general_inst_02.png');
    inst_press2_tex = Screen('MakeTexture', win, inst_press2_img);
    Screen('DrawTexture', win, inst_tex);
    Screen('Flip', win);

    % wait for the participant's resp.  (either 1 or 2)
    while 1
        [keyIsDown, initExpt, keyCode] = KbCheck(Participant);
        if keyIsDown
            if keyCode(Press_1)
                Screen('DrawTexture', win, inst_press1_tex);
                Screen('Flip', win);
                break;
            elseif keyCode(Press_2)
                Screen('DrawTexture', win, inst_press2_tex);
                Screen('Flip', win);
                break;
            end
        end
    end

    % wait for the experiementer's resp.  (SPACE)
    while 1
        [keyIsDown, initExpt, keyCode] = KbCheck(Experimenter);
        if keyIsDown
            if keyCode(Space)
                break;
            end
        end
    end

end



%% Instruction
% text
[tx, ty]    = RectCenter(rect);
Screen(win, 'FillRect', gray);
Screen('Preference', 'TextRenderer', 0)
Screen('TextFont',win, 'Arial'); % set default text font
Screen('TextSize',win, fontsize); % set default text size
Screen('TextStyle', win, 0); % set default text style


% speech instruction
msg = convertStringsToChars(msg);
msg = double(native2unicode(msg));
tRect = Screen('TextBounds', win, msg);
tRect = CenterRectOnPoint(tRect, tx, ty);
Screen('Preference', 'TextRenderer', 0)
DrawFormattedText(win, msg, 'center','center', black);


% fixation
dotSize = 6; %radius [px]
fixationDot = [-dotSize -dotSize dotSize dotSize];
fixationDot = CenterRect(fixationDot, rect);
Screen('FillOVal', win, white, fixationDot);
Screen('Flip', win);



%% eyetracking video
done = 0;
scanPulse=0;
cal_moviename = fullfile(pwd, '24points_calibration_40sec_1600x1000.mp4');
[cal_movie, duration] = Screen('OpenMovie', win, cal_moviename);

if listen == 1
    while scanPulse~=1 %wait for a pulse
        [keyIsDown, ~, keyCode] = KbCheck(Scanner);
        if keyIsDown
            if keyCode(syncNum)
                scanPulse = 1;
                break;
            end
        end
    end
    PsychPortAudio('Start', pahandle, 0, 0, 1);

elseif listen == 2
    while(~done)
        [keyIsDown, secs, keyCode, deltaSecs] = KbCheck(Experimenter);
        if keyCode(Space)
            done = 1;
        end
    end
end



%% Video Start
Screen(win, 'FillRect', gray);
Screen('Flip', win);
Screen('PlayMovie', cal_movie, 1, 1, 0);
vidtime = GetSecs();
t2 = GetSecs();
while (t2-vidtime)<duration
    % Wait for next movie frame, retrieve texture handle to it
    tex = Screen('GetMovieImage', win, cal_movie);
    if tex<=0
        break;
    end
    % Draw the new texture immediately to screen:
    Screen('DrawTexture', win, tex);
    Screen('Flip', win);
    Screen('Close', tex);
    t2 = GetSecs();
end
Screen('PlayMovie', cal_movie, 0);
Screen('CloseMovie', cal_movie);



%% Main experiments
t0=GetSecs;
done = 0;

dotSize = 6; %radius [px]
fixationDot = [-dotSize -dotSize dotSize dotSize];
fixationDot = CenterRect(fixationDot, rect);

% 시작 fixation
while (~done)
    Screen(win, 'FillRect', gray);
    Screen('FillOVal', win, white, fixationDot);
    if Speech_type == "FS"
        msg = "\n\n\n\n";
        msg = msg + FS_insts_sub + "\n\n";
        msg = convertStringsToChars(msg);
        msg = double(native2unicode(msg));
        tRect = Screen('TextBounds', win, msg);
        tRect = CenterRectOnPoint(tRect, tx, ty);
        Screen('Preference', 'TextRenderer', 0)
        DrawFormattedText(win, msg, 'center','center', black);
    end
    Screen('Flip',win);
    
    if GetSecs - t0 >8 
        done = 1;
        break
    end
end

% 말하기 시작
t1=GetSecs;
done = 0;
if Speech_type == "TA" || Speech_type == "MC"
    while (~done)
        if listen == 1
            [keyIsDown, ~, keyCode] = KbCheck(Experimenter);
        elseif listen == 2
            [keyIsDown, secs, keyCode, deltaSecs] = KbCheck(Experimenter);
        end
        if keyIsDown
            if keyCode(Abort)
                done = 1;
                break;
            end
        end
        if GetSecs - t1 > 600 % 10mins
            done = 1;
            break;
        end
        Screen('Flip',win);
    end
elseif Speech_type == "FS"
    left = floor(str2num(left))-1;
    while (~done)
        if listen == 1
            [keyIsDown, ~, keyCode] = KbCheck(Participant);
        elseif listen == 2
            [keyIsDown, secs, keyCode, deltaSecs] = KbCheck(Participant);
        end
        if keyIsDown
            if keyCode(Press_1)
                done = 1;
                break;
            end
        end
        if keyIsDown
            if keyCode(Abort)
                done = 1;
                break;
            end
        end
        if GetSecs - t1 > floor(left*60/8)*8 % less than (max-1)
            done = 1;
            break;
        end    
        duration = GetSecs - t1;
        Screen('Flip',win);
    end
else
    left = floor(str2num(left))-1;
    while (~done)
        if listen == 1
            [keyIsDown, ~, keyCode] = KbCheck(Participant);
        elseif listen == 2
            [keyIsDown, secs, keyCode, deltaSecs] = KbCheck(Participant);
        end
        if keyIsDown
            if keyCode(Press_1)
                done = 1;
                break;
            end
        end
        if keyIsDown
            if keyCode(Abort)
                done = 1;
                break;
            end
        end
        if GetSecs - t1 > floor(left*60/8)*8 % less than (max-1)
            done = 1;
            break;
        end

        duration = GetSecs - t1;
        Screen('Flip',win);
    end
end

% 마무리 fixation
t3=GetSecs;
done = 0;
while (~done)
    Screen(win, 'FillRect', gray);
    Screen('FillOVal', win, white, fixationDot);
    Screen('Flip',win);
    
    if GetSecs - t3 >8 %8s
        done = 1;
        break
    end
end
Screen('CloseAll');
allend = GetSecs();


%% Save files
% audio file
if listen == 1
    PsychPortAudio('Stop', pahandle);
    AudioData = PsychPortAudio('GetAudioData', pahandle);
    AudioData = AudioData';
    try
    	audiowrite(afile,AudioData,44100);
    catch
        afile = char(afile);
        audiowrite(afile,AudioData,44100);
    end
end

% timestamp
time_matrix = [time_matrix; ...
    subName, SesNum, "Calibration", 0, t0-vidtime;...
    subName, SesNum, "Fixation", t0-vidtime, t1-t0;...
    subName, SesNum, "Speech", t1-vidtime, t3-t1;...
    subName, SesNum, "Fixation", t3-vidtime, allend-t3];

csvid = fopen(sfile, 'w');
for i = 1:5
    fprintf(csvid, '%s\t%s\t%s\t%s\t%s\n', time_matrix(i,1),...
        time_matrix(i,2),time_matrix(i,3),time_matrix(i,4),time_matrix(i,5));
end

% finish
IOPort('CloseAll');
Priority(0); ListenChar(0);
ShowCursor;

if listen == 1
    PsychPortAudio('Close', pahandle);
end
