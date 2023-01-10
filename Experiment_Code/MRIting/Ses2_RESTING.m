%% Initialize
close all; 
clear;
IOPort('Closeall'); Screen('Close'); Screen('Closeall');
clc;

% speech time, 600s
speech_time = 600;

% screensize, 3t:[0 0 1920 1080]  7t: [0 0 1600 900]
basic_screen = [0 0 1920 1080];

% Enter subject ID
gName = input('\n\nGroup (ex. 01, 02)                       >> ','s');
if length(gName) < 1
    gName = 'test';
end

% Sub number
subName = input('\nSubject (1:male, 2:female)               >> ','s');


% Is it behavior?
listen = str2double(input('\nExperiment type (1: scan, 2:test)        >> ','s'));
if isnan(listen)
    listen = 2;
end
ses_folder = fullfile(pwd, 'Data', strcat('sub-',gName,'0',subName), 'ses-2');
mkdir(ses_folder);
sfile = fullfile(ses_folder, strcat('sub-',gName,'0',subName,'_ses-2_task-RESTING_timestamp.txt'));
time = strings(4,1);


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




%% Screen Settings
wininfo = Screen('Resolution', 0);   % width,heigth,pixelSize,hz
screenid = max(Screen('Screens'));

Screen('Preference', 'SkipSyncTests', 1);

% Color Setting
white = WhiteIndex(screenid);
black = BlackIndex(screenid); % pixel value for black
gray = (white+black)/2;


% Window Setting
if listen == 2
    [win,rect] = Screen('OpenWindow', screenid, gray, [0 0 1600 1000]);
else
    [win,rect] = Screen('OpenWindow', screenid, gray);
    HideCursor;
end
fliprate = Screen('GetFlipInterval', win);  % estimate of the monitor flip interval
priorityLevel=MaxPriority(win);
Priority(priorityLevel); 

ratio_x = rect(3)/basic_screen(3);
ratio_y = rect(4)/basic_screen(4);
if ratio_x < ratio_y
    left_y = (rect(4)-(basic_screen(4)*ratio_x))/2;
    scaled_screen = [0 left_y basic_screen(3)*ratio_x rect(4)-left_y];
else
    left_x = (rect(3)-(basic_screen(3)*ratio_y))/2;
    scaled_screen = [left_x 0 rect(3)-left_x basic_screen(4)*ratio_y];    
end

    



%% Instruction
% inst img
img_file = imread(fullfile(pwd, 'Inst', 'RESTING', 'Inst.jpg'));
img_texture = Screen('MakeTexture', win, img_file);
Screen('DrawTexture', win, img_texture, [], scaled_screen);

% fixation
dotSize = 10; %radius [px]
fixationDot = [-dotSize -dotSize dotSize dotSize];
fixationDot = CenterRect(fixationDot, rect);
Screen('FillOVal', win, white, fixationDot);
Screen('Flip', win);

% Wait Pulse
done = 0;
scanPulse=0;

while scanPulse~=1 
    [keyIsDown, ~, keyCode] = KbCheck(Scanner);
    if keyIsDown
        if keyCode(syncNum)
            scanPulse = 1;
            break;
        end
    end
end



%% Main Experiment
time(1) = datestr(datetime('now'),'yyyy-mm-ddTHH:MM:SS:FFF');
% first screen
Screen('FillOVal', win, white, fixationDot);
Screen('Flip', win);
t0 = GetSecs();
while (GetSecs - t0) < 10
    [keyIsDown, secs, keyCode, deltaSecs] = KbCheck(Experimenter);
    if keyCode(Abort)
       break;
    end
end

% main
Screen('Flip', win);
t1 = GetSecs();
while (GetSecs - t1) < speech_time
    [keyIsDown, secs, keyCode, deltaSecs] = KbCheck(Experimenter);
    if keyCode(Abort)
        break;
    end
end

% final screen
Screen('FillOVal', win, white, fixationDot);
Screen('Flip', win);

t2 = GetSecs();
time(2) = num2str(t1-t0);
time(3) = num2str(t2-t1);
while (GetSecs - t2) < 10
    [keyIsDown, secs, keyCode, deltaSecs] = KbCheck(Experimenter);
    if keyCode(Abort)
        break;
    end    
end


%% finish
t3 = GetSecs();
time(4) = num2str(t3-t2);
IOPort('CloseAll');
sca;
Priority(0); ListenChar(0);
ShowCursor;

fID = fopen(sfile, 'w');
for i=1:4
    fprintf(fID, '%s\n',time(i));
end
fclose(fID);

