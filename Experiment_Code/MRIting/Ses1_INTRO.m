%% Initialize
close all;
clear all;
clear mex;
IOPort('Closeall');
Screen('Close');
Screen('Closeall');
Screen('Preference', 'SkipSyncTests', 2);
Screen('Preference', 'TextRenderer', 1);
Screen('Preference', 'TextAntiAliasing', 1);
Screen('Preference', 'TextAlphaBlending', 0);
Screen('Preference', 'DefaultTextYPositionIsBaseline', 1);
AssertOpenGL
commandwindow;

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
topic1_num = [1,2,3,4,5,6,7,8];
topic2_num = [3,6,8,15,19,20];
topic3_num = [5,7,11,14,18];
speechTime = 420;
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
audio_device = PsychPortAudio('GetDevices');
fprintf("\n--------\nMIC Info\n--------\n")
fprintf(strcat("Name should be 'USB Audio CODEC': ", audio_device(2).DeviceName))
fprintf(strcat("\nInput channel shoud be 2: ", num2str(audio_device(2).NrInputChannels)))


% Enter subject ID
subName = input('\n\nGroup (ex. 01, 02)                       >> ','s');
if length(subName) < 1
    subName = 'test';
end

% Sub number
sexName = input('\nSubject (1:male, 2:female)               >> ','s');

% Run number
RUN = input('\nRun (1:intro, 2:common, 3:diff)          >> ','s');
RUN = str2double(RUN);

% Is it behavior?
listen = str2double(input('\nExperiment type (1: scan, 2:test)        >> ','s'));
if isnan(listen)
    listen = 2;
end
ses_folder = fullfile(pwd, 'Data', strcat('sub-',subName,'0',sexName), 'ses-1');
mkdir(ses_folder);

%% Monitor ratio
standard = [1920 1080];
current_size = [1920 1080];

monitor_ratio = current_size(2)/standard(2);



%% Keyborad and Input Device Setup
[keyboardIndex, deviceName, allInfo] = GetKeyboardIndices;

% ================== Macbook keyboard ====================
[,Experimenter] = find(strcmp(deviceName,'Apple Internal Keyboard / Trackpad'));
Experimenter = keyboardIndex(Experimenter);


% ================== Participant =========================
[,Participant] = find(strcmp(deviceName,'932'));
Participant = keyboardIndex(Participant);

% ================== Scanner =============================
[,Scanner] = find(strcmp(deviceName,'KeyWarrior8 Flex'));
Scanner = keyboardIndex(Scanner);

if listen == 2
    Participant = Experimenter;
    Scanner = Experimenter;
end

% if empty use default
if isempty(Participant) Participant = Experimenter; end
if isempty(Scanner) Scanner = Experimenter; end

% keyboard
KbName('UnifyKeyNames');
syncNum = KbName('s');
Abort = KbName('q');
Space = KbName('space');

key1 = KbName('a'); % 65
key2 = KbName('s'); % 83
key3 = KbName('d'); % 68

key4 = KbName('j'); % 74
key5 = KbName('k'); % 75
key6 = KbName('l'); % 76

%% Screen Settings & Video Encoding
global win cx cy;
wininfo = Screen('Resolution', 0);   % width,heigth,pixelSize,hz
ScreenID = max(Screen('Screens'));
Screen('Preference', 'TextRenderer', 1);
Screen('Preference', 'TextAntiAliasing', 1);
Screen('Preference', 'TextAlphaBlending', 0);
Screen('Preference', 'DefaultTextYPositionIsBaseline', 1);

% Color Setting
white = WhiteIndex(ScreenID);
black = BlackIndex(ScreenID);
gray = (white+black)/2;
fontsize = 40 * monitor_ratio;

% Window Setting
[win,rect] = Screen('OpenWindow', ScreenID, gray);
[cx,cy] = RectCenter(rect);

fps = Screen('FrameRate', ScreenID);	% frames per second
ifi = Screen('GetFlipInterval', win);
Screen('BlendFunction', win, 'GL_SRC_ALPHA', 'GL_ONE_MINUS_SRC_ALPHA');
fprintf("*** Interframe interval = %4.4fms\n", ifi*1000);

waitTime = (round(10/ifi)-0.5)*ifi;
mainTime = (round(speechTime/ifi)-0.5)*ifi;

if fps
    fprintf("*** Refresh rate = %4.4fHz\n", fps);
else % make sure that fps = 0 in some settings.
    fps = 1/ifi;
    fprintf("*** Calculated refresh rate = %4.4fHz\n", fps);
end
Screen('Flip', win);	% Do initial flip...

priorityLevel=MaxPriority(win);
Priority(priorityLevel);
HideCursor;

%% Instruction
topic1 = cell(1,8);
for i = 1:8
    tmp = imread(fullfile(pwd,'Inst','INTRO','stim',sprintf('stim01_%02d.jpg',i)));
    tmp2 = Screen('MakeTexture', win, tmp);
    topic1{i} = tmp2;
end

topic2 = cell(1,20);
for i = 1:20
    tmp = imread(fullfile(pwd,'Inst','INTRO','stim', sprintf('stim02_%02d.jpg',i)));
    tmp2 = Screen('MakeTexture', win, tmp);
    topic2{i} = tmp2;
end

ins_1 = imread(fullfile(pwd,'Inst','INTRO','inst','inst1_1.jpg'));
ins_2 = imread(fullfile(pwd,'Inst','INTRO','inst','inst1_2.jpg'));
ins_3 = imread(fullfile(pwd,'Inst','INTRO','inst','inst1_3.jpg'));

inst_1 = Screen('MakeTexture', win, ins_1);
inst_2 = Screen('MakeTexture', win, ins_2);
inst_3 = Screen('MakeTexture', win, ins_3);

instSize = [1920 1080] * monitor_ratio;
instLoc = [cx-instSize(1)/2 cy-instSize(2)/2 cx+instSize(1)/2 cy+instSize(2)/2];

topicSize1 = [480 270] * monitor_ratio;
topicSize2 = [640 360] * monitor_ratio;

dy1 = current_size(2)/4 * monitor_ratio;
dx1 = current_size(1)/4 * monitor_ratio;
topicLoc1 = {[cx-dx1-topicSize1(1)/2 cy-dy1-topicSize1(2)/2 cx-dx1+topicSize1(1)/2 cy-dy1+topicSize1(2)/2],...
            [cx-dx1-topicSize1(1)/2 cy+dy1-topicSize1(2)/2 cx-dx1+topicSize1(1)/2 cy+dy1+topicSize1(2)/2],...
            [cx+dx1-topicSize1(1)/2 cy-dy1-topicSize1(2)/2 cx+dx1+topicSize1(1)/2 cy-dy1+topicSize1(2)/2],...
            [cx+dx1-topicSize1(1)/2 cy+dy1-topicSize1(2)/2 cx+dx1+topicSize1(1)/2 cy+dy1+topicSize1(2)/2],...
            [cx-topicSize1(1)/2 cy-topicSize1(2)/2 cx+topicSize1(1)/2 cy+topicSize1(2)/2]};

topicLoc2 = {[cx-dx1-topicSize2(1)/2 cy-dy1-topicSize2(2)/2 cx-dx1+topicSize2(1)/2 cy-dy1+topicSize2(2)/2],...
            [cx-dx1-topicSize2(1)/2 cy+dy1-topicSize2(2)/2 cx-dx1+topicSize2(1)/2 cy+dy1+topicSize2(2)/2],...
            [cx+dx1-topicSize2(1)/2 cy-dy1-topicSize2(2)/2 cx+dx1+topicSize2(1)/2 cy-dy1+topicSize2(2)/2],...
            [cx+dx1-topicSize2(1)/2 cy+dy1-topicSize2(2)/2 cx+dx1+topicSize2(1)/2 cy+dy1+topicSize2(2)/2],...
            [cx-topicSize2(1)/2 cy-topicSize2(2)/2 cx+topicSize2(1)/2 cy+topicSize2(2)/2]};

%% file save
fileName_stm = fullfile(ses_folder, strcat('sub-',subName,'0',sexName,'_ses-1_task-INTRO_run-',num2str(RUN),'_timestamp.txt'));
stimFile = fopen(fileName_stm,'w');
afile = fullfile(ses_folder, strcat('sub-',subName,'0',sexName,'_ses-1_task-INTRO_run-',num2str(RUN),'_audio.wav'));


%% Audio Recording
% check audio device info using "PsychPortAudio('GetDevices')"
% Sound recording: Preallocate an internal audio recording  buffer with a capacity of 10 seconds
%'Open' [deviceid] [mode] [reqlatencyclass] [frequency] [channels]
% maybe id=1
if listen == 1
    InitializePsychSound;
    pahandle = PsychPortAudio('Open',1,2,0,44100,1);
    PsychPortAudio('GetAudioData', pahandle, speechTime+60);
end

% default mic
if listen == 2
    InitializePsychSound;
    pahandle = PsychPortAudio('Open',[],2,0,44100,1);
    PsychPortAudio('GetAudioData', pahandle, speechTime+60);
end


%% Instruction
Screen(win, 'FillRect', gray);
if RUN == 1
    Screen('DrawTexture', win, inst_1, [], instLoc);
elseif RUN == 2
    Screen('DrawTexture', win, inst_2, [], instLoc);
elseif RUN == 3
    Screen('DrawTexture', win, inst_3, [], instLoc);
end
Screen('Flip', win);
% showInstruction('Ready', fontsize, 0);

done = 0;
scanPulse=0;
while scanPulse~=1 %wait for a pulse
    [keyIsDown, ~, keyCode] = KbCheck(Scanner); % Here change Scanner -> -3
    if keyIsDown
        if keyCode(syncNum)
            scanPulse = 1;
            firstS = GetSecs;
            trigger = 1;
            starttime = datestr(clock,'YYYY/mm/dd HH:MM:SS:FFF');
            fprintf(stimFile,'%s', starttime);
            start = GetSecs;
            break;
        end
    end
end
PsychPortAudio('Start', pahandle, 0, 0, 1); % start audio

%% Main Experiment
Screen('FillRect', win, gray);
dotSize = 10; %radius [px]
fixationDot = [-dotSize -dotSize dotSize dotSize];
fixationDot = CenterRect(fixationDot, rect);
Screen('FillOVal', win, white, fixationDot);
Screen('Flip', win);
WaitSecs(waitTime);
blank = GetSecs;
fprintf(stimFile,'\nblank %1.4f', blank-start);

finish = 0;

count = 0;
if RUN == 1
    rs = Shuffle(topic1_num);
    topic = topic1;
    topicLoc = topicLoc1;
elseif RUN == 2
    rs = Shuffle(topic2_num);
    topic = topic2;
    topicLoc = topicLoc2;
elseif RUN == 3
    rs = Shuffle(topic3_num);
    topic = topic2;
    topicLoc = topicLoc2;
end
while ~finish && GetSecs - blank < mainTime
    for s = 1:5
        Screen('DrawTexture', win, topic{rs(s)}, [], topicLoc{s});
    end
    Screen('Flip', win);
    [keyIsDown, ~, keyCode] = KbCheck(Scanner); % Here change Scanner -> -3
    if keyIsDown
        if keyCode(Abort)
            finish = 1;
        end
    end
end

main = GetSecs;
fprintf(stimFile,'\nmain %1.4f', main-blank);

Screen('FillRect', win, gray);
Screen('FillOVal', win, white, fixationDot);
Screen('Flip', win);
WaitSecs(waitTime);
blank2 = GetSecs;
fprintf(stimFile,'\nend %1.4f', blank2-main);

% audio stop
PsychPortAudio('Stop', pahandle);
fclose('all');
Screen('CloseAll');
IOPort('CloseAll');
Priority(0); ListenChar(0);
ShowCursor;

% save
AudioData = PsychPortAudio('GetAudioData', pahandle);
AudioData = AudioData';
audiowrite(afile,AudioData,44100);
PsychPortAudio('Close', pahandle);

%% showinstruction
function showInstruction(txt, txtsize, txtcolor)
% see DrawHighQualityUnicodeTextDemo.m
global win;
% Text files edited with a text editor such as vi or nano.

xtext = txt';
xtext = double(transpose(xtext));

% type 'listfonts' and find your font from the list.
% In case you're using PC and your Matlab's using Korean as basic
% language, go to 'Preference > General' and choose English as 'Desktop
% language.' Turn on and off Matlab. Type 'listfonts' again.
% see http://cogneuro.or.kr/mediawiki/index.php/PsychToolBox
Screen('TextFont', win, 'Gulim', 0);
Screen('TextColor', win, txtcolor);
Screen('TextSize', win, txtsize);

DrawFormattedText(win, xtext, 'center', 'center',[],[],0);
Screen('Flip', win);
end