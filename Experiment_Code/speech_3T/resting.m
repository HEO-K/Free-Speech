function resting(subName, listen)
Screen('Close'); Screen('Closeall');
clc;
Screen('Preference', 'SkipSyncTests', 1);

% Sub number
if length(subName) < 1
    subName = 'test';
end
sub_dir = "_DATA/sub-"+subName;
mkdir(sub_dir);
% scan or behavior
if isnan(listen)
    listen = 2;
end


sfile = fullfile(pwd, sub_dir, strcat('sub-',subName,'_task-REST_timepoint.txt'));
output_mat = strings(4,1);

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
syncNum = KbName('s');
Abort = KbName('1!');
Space = KbName('space');
Abort_q = KbName('q');


%% Screen Settings
wininfo = Screen('Resolution', 0);   % width,heigth,pixelSize,hz
screenid = max(Screen('Screens'));

Screen('Preference', 'SkipSyncTests', 1);

% Color Setting
white = WhiteIndex(screenid);
black = BlackIndex(screenid); % pixel value for black
gray = (white+black)/2;
fontsize = 60;

% Window Setting
if listen == 2
    [win,rect] = Screen('OpenWindow', screenid, gray, [0 0 1600 1000]);
else
    [win,rect] = Screen('OpenWindow', screenid, gray);
%    HideCursor;
end
fliprate = Screen('GetFlipInterval', win);  % estimate of the monitor flip interval
priorityLevel=MaxPriority(win);
Priority(priorityLevel); 

%%
img_file = imread('./Instruction/REST.jpg');
img_texture = Screen('MakeTexture', win, img_file);
Screen('DrawTexture', win, img_texture, [], []);


% fixation
dotSize = 10; %radius [px]
fixationDot = [-dotSize -dotSize dotSize dotSize];
fixationDot = CenterRect(fixationDot, rect);
Screen('FillOVal', win, white, fixationDot);
Screen('Flip', win);


% Wait Pulse
done = 0;
scanPulse=0;
if listen == 1
    while scanPulse~=1 
        [keyIsDown, ~, keyCode] = KbCheck(Scanner);
        if keyIsDown
            if keyCode(syncNum)
                scanPulse = 1;
                break;
            end
        end
    end

else
    while(~done)
        [keyIsDown, secs, keyCode, deltaSecs] = KbCheck(Experimenter);
        if keyCode(Space)
            done = 1;
        end
    end
end


%% Main Experiment
% ready
Screen('FillOVal', win, white, fixationDot);
Screen('Flip', win);
t0 = GetSecs();
while (GetSecs - t0) < 10
end

% main
Screen('Flip', win);
t1 = GetSecs();
output_mat(2) = num2str(t1-t0);
while (GetSecs - t1) < 600 %10min
    [keyIsDown, secs, keyCode, deltaSecs] = KbCheck(Experimenter);
    if keyCode(Abort_q)
        break
    end
end

% final screen
Screen('FillOVal', win, white, fixationDot);
Screen('Flip', win);
t2 = GetSecs();
output_mat(3) = num2str(t2-t1);
while (GetSecs - t2) < 10
end


% finish
t3 = GetSecs();
output_mat(4) = num2str(t3-t2);
IOPort('CloseAll');
sca;
Priority(0); ListenChar(0);
ShowCursor;


if listen == 1
    fID = fopen(sfile, 'w');
    for i=1:4
        fprintf(fID, '%s\n',output_mat(i));
    end
    fclose(fID);
end