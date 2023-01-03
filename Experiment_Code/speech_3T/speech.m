function speech(subName, runName, listen)
Screen('Close'); Screen('Closeall');
clc;
Screen('Preference', 'SkipSyncTests', 1);

% Sub number
if length(subName) < 1
    subName = 'test';
end
sub_dir = "_DATA/sub-"+subName;


% scan or behavior
if isnan(listen)
    listen = 2;
end

if runName == '1'
    task= 'speechFREE';
end
if runName == '2'
    task = 'speechTOPIC';
end
if runName == '3'
    task = 'speechSTROLL';
end

afile = fullfile(pwd, sub_dir, strcat('sub-',subName,'_task-',task,'.wav'));
sfile = fullfile(pwd, sub_dir, strcat('sub-',subName,'_task-',task,'_timepoint.txt'));
output_mat = strings(4,1);

%% Random Topic
seed_number = num2str(GetSecs());
seed_number = seed_number(end-2:end);
rng(str2num(seed_number));
if runName == "2"
    topics = ["A", "D", "N"];
    topics = topics(randperm(3));
    output_mat(1) = join(topics);
end

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
Space = KbName('space');
Abort_q = KbName('q');
Abort = KbName('1!');

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
if listen == 1
    InitializePsychSound;
    pahandle = PsychPortAudio('Open',1,2,0,44100,1);
    PsychPortAudio('GetAudioData', pahandle, 1260);
end
% default mic
if listen == 2
    InitializePsychSound;
    pahandle = PsychPortAudio('Open',[],2,0,44100,1);
    PsychPortAudio('GetAudioData', pahandle, 1260);
end

%% Instruction
x0=100;
y0=540;
if runName == "1"
    img_file = imread('./Instruction/TA.jpg');
    img_texture = Screen('MakeTexture', win, img_file);
    Screen('DrawTexture', win, img_texture, [], []);
elseif runName == "2"
    img_file = imread('./Instruction/3TS.jpg');
    img_texture = Screen('MakeTexture', win, img_file);
    Screen('DrawTexture', win, img_texture, [], []);
    for i = 1:3
        img_file = imread("./Instruction/topic1/"+topics(i)+".jpg");
        img_texture = Screen('MakeTexture', win, img_file);
        img_size = size(img_file);
        Screen('DrawTexture', win, img_texture, [],...
        [x0, y0+77*(i-1), x0+img_size(2), y0+77*(i-1)+img_size(1)]);
    end
else
    img_file = imread('./Instruction/STROLL.jpg');
    img_texture = Screen('MakeTexture', win, img_file);
    Screen('DrawTexture', win, img_texture, [], []);   
end
    
    
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
    PsychPortAudio('Start', pahandle, 0, 0, 1);
else
    while(~done)
        [keyIsDown, secs, keyCode, deltaSecs] = KbCheck(Experimenter);
        if keyCode(Space)
            done = 1;
        end
    end
end


%% Main Experiment
% 3TS 1
if runName == "2"
    % ready
    img_file = imread('./Instruction/3TS2.jpg');
    img_texture = Screen('MakeTexture', win, img_file);
    Screen('DrawTexture', win, img_texture, [], []);
    for i = 1:3
        img_file = imread("./Instruction/topic1/"+topics(i)+".jpg");
        img_texture = Screen('MakeTexture', win, img_file);
        img_size = size(img_file);
        Screen('DrawTexture', win, img_texture, [],...
        [x0, y0+77*(i-1), x0+img_size(2), y0+77*(i-1)+img_size(1)]);
    end
    Screen('FillOVal', win, white, fixationDot);
    Screen('Flip', win);
    t0 = GetSecs();
    while (GetSecs - t0) < 10  
    end
    

    Screen('Flip', win);
    t1 = GetSecs();
    output_mat(2) = num2str(t1-t0);
    while (GetSecs - t1) < 1200 %20min
        [keyIsDown, secs, keyCode, deltaSecs] = KbCheck(Participant);
        if keyCode(Abort)
            break;
        end
        [keyIsDown, secs, keyCode, deltaSecs] = KbCheck(Experimenter);
        if keyCode(Abort_q)
            break
        end
    end  
    
% TA
else
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
    PsychPortAudio('Stop', pahandle);
    AudioData = PsychPortAudio('GetAudioData', pahandle);
%    AudioData = AudioData';
	audiowrite(afile,AudioData,44100);
    PsychPortAudio('Close', pahandle);
    fID = fopen(sfile, 'w');
    for i=1:4
        fprintf(fID, '%s\n',output_mat(i));
    end
    fclose(fID);
end
