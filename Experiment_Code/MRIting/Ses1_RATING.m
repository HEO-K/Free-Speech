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

import java.awt.Robot;
import java.awt.event.*;
robot = Robot;
addpath(genpath(fullfile(pwd,'Inst','INTRO')));%,'question_generator.m')));
subName = input('\n\nGroup (ex. 01, 02)                                                  >> ','s');
if length(subName) < 1
    subName = 'test';
end

% Sub number
sexName = input('\nSubject (1:male, 2:female)                                          >> ','s');
GENDER = str2double(sexName);

RunName = input('\nRun (1:Init, 2:INTRO1, 3:INTRO2, 4:INTRO3, 5:CHATTING, 6:TRUTHLIE)  >> ','s');
RUN = str2double(RunName);

% Is it behavior?
listen = str2double(input('\nExperiment type (1: scan, 2:test)                                   >> ','s'));
if isnan(listen)
    listen = 2;
end
ses_folder = fullfile(pwd, 'Data', strcat('sub-',subName,'0',sexName), 'ses-1');
mkdir(ses_folder);

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
Abort = KbName('escape');
Space = KbName('space');

key1 = KbName('a');
key2 = KbName('s');
key3 = KbName('d');

key4 = KbName('j');
key5 = KbName('k');
key6 = KbName('l');

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
fontsize = 40;

% Window Setting
[win,rect] = Screen('OpenWindow', ScreenID, black);
[cx,cy] = RectCenter(rect);

fps = Screen('FrameRate', ScreenID);	% frames per second
ifi = Screen('GetFlipInterval', win);
Screen('BlendFunction', win, 'GL_SRC_ALPHA', 'GL_ONE_MINUS_SRC_ALPHA');
fprintf("*** Interframe interval = %4.4fms\n", ifi*1000);

if fps
    fprintf("*** Refresh rate = %4.4fHz\n", fps);
else % make sure that fps = 0 in some settings.
    fps = 1/ifi;
    fprintf("*** Calculated refresh rate = %4.4fHz\n", fps);
end
Screen('Flip', win);	% Do initial flip...

% timing Setting
blankTime_first  = (round(8/ifi)-0.5)*ifi;
blankTime_last  = (round(8/ifi)-0.5)*ifi;
fixTime    = (round(2/ifi)-0.5)*ifi;
delayTime  = (round(1/ifi)-0.5)*ifi;

priorityLevel=MaxPriority(win);
Priority(priorityLevel);
HideCursor;

d = GetMouseIndices;
d = d(1);

%% Monitor ratio
standard = [1920 1080];
current_size = [1920 1080];
dotSize = 10; %radius [px]
monitor_ratio = current_size(2)/standard(2);

%% Instruction
if RUN == 1
    ins = imread(fullfile(pwd,'Inst','INTRO','inst', 'inst2_1.jpg'));
else
    ins = imread(fullfile(pwd,'Inst','INTRO','inst', 'inst2_2.jpg'));
end
inst = Screen('MakeTexture', win, ins);
instSize = [1280 720] * monitor_ratio;
instLoc = [cx-instSize(1)/2 cy-instSize(2)/2 cx+instSize(1)/2 cy+instSize(2)/2];

%% file save
fileName_stm = fullfile(ses_folder, strcat('sub-',subName,'0',sexName,'_ses-1_task-RATING_run-',num2str(RUN),'_impression.csv'));


data.SN = str2double(subName);
data.Gender = GENDER;
data.RunNo = RUN;


data.fulldata = fullfile(ses_folder, strcat('sub-',subName,'0',sexName,'_ses-1_task-RATING_run-',num2str(RUN),'_impression.mat`'));
data.subject = strcat('sub-',subName,'0',sexName);
data.starttime = datestr(clock,0);

dataFile = fopen(fileName_stm,'a');
fprintf(dataFile,'SN,Gender,RunNo,TrialNo,TrialOnset,TrialDur,Attribute,Char1,Pred,Rating,RT\n');

%% Stimulus
sen_1 = imread(fullfile(pwd,'Inst','INTRO','stim', '1sentence.jpg'));
sen_2 = imread(fullfile(pwd,'Inst','INTRO','stim', '2sentence.jpg'));
sen_3 = imread(fullfile(pwd,'Inst','INTRO','stim', '3sentence.jpg'));
sen_4 = imread(fullfile(pwd,'Inst','INTRO','stim', '4sentence.jpg'));
sen_5 = imread(fullfile(pwd,'Inst','INTRO','stim', '5sentence.jpg'));
sen_one = Screen('MakeTexture', win, sen_1);
sen_two = Screen('MakeTexture', win, sen_2);
sen_three = Screen('MakeTexture', win, sen_3);
sen_four = Screen('MakeTexture', win, sen_4);
sen_five = Screen('MakeTexture', win, sen_5);

stimSize1 = [600 600];
stimSize2 = [150 150];
stimLoc1 = [cx-stimSize1(1)/2 cy-stimSize1(2)/2 cx+stimSize1(1)/2 cy+stimSize1(2)/2];
stimLoc2 = [cx-400-stimSize2(1)/2 cy-400-stimSize2(2)/2 cx-400+stimSize2(1)/2 cy-400+stimSize2(2)/2];

%% Condition
[character_order,question_order] = BalanceFactors(1,1,1:2,1:9);
trialN = length(character_order);
f = @question_generator;

data.run = zeros(trialN,1);
data.trial = zeros(trialN,1);
data.trial_start = zeros(trialN,1);
data.total_dur = zeros(trialN,1);
data.real_dur = zeros(trialN,1);
data.trial_dur = zeros(trialN,1);
data.trial_dur_abs = zeros(trialN,1);
data.attr = cell(trialN,1);
data.ch1 = cell(trialN,1);
data.ch2 = cell(trialN,1);
data.ch1N = zeros(trialN,1);
data.ch2N = zeros(trialN,1);
data.pred = cell(trialN,1);
data.predN = zeros(trialN,1);
data.initrating = zeros(trialN,1);
data.rating = zeros(trialN,1);
data.rating_time = zeros(trialN,1);
data.rating_start = zeros(trialN,1);

dotsize = 48;
reddotsize = 36;
stimSize = 250;
tarloc1  = [cx-stimSize/2 cy-3*stimSize/2-0 cx+stimSize/2 cy-stimSize/2-0];
tarloc21 = [cx-3*stimSize/2 cy-3*stimSize/2-0 cx-stimSize/2 cy-stimSize/2-0];
tarloc22 = [cx+stimSize/2 cy-3*stimSize/2-0 cx+3*stimSize/2 cy-stimSize/2-0];
digitSize = 28;
diameter = 150;
senSize = [150 60];
downtodot = 48 + dotsize/3;
leritodot = 0;
rateloc = {[cx-diameter*cos(30*pi/180) 3*cy/2+diameter*sin(30*pi/180)],... % 1 �ſ� �׷��� �ʴ�
    [cx-diameter*cos(330*pi/180) 3*cy/2+diameter*sin(330*pi/180)],... % 2 �׷��� �ʴ�
    [cx-diameter*cos(270*pi/180) 3*cy/2+diameter*sin(270*pi/180)],... % 3 �����̴�
    [cx-diameter*cos(210*pi/180) 3*cy/2+diameter*sin(210*pi/180)],... % 4 �׷���
    [cx-diameter*cos(150*pi/180) 3*cy/2+diameter*sin(150*pi/180)],... % 5 �ſ� �׷���
    [cx 3*cy/2]};
rateloc_sen = {[rateloc{1}(1)-senSize(1)/2 rateloc{1}(2)+downtodot-senSize(2)/2 rateloc{1}(1)+senSize(1)/2 rateloc{1}(2)+downtodot+senSize(2)/2],...
    [rateloc{2}(1)-senSize(1)/2 rateloc{2}(2)+downtodot-senSize(2)/2 rateloc{2}(1)+senSize(1)/2 rateloc{2}(2)+downtodot+senSize(2)/2],...
    [rateloc{3}(1)-senSize(1)/2 rateloc{3}(2)+downtodot-senSize(2)/2 rateloc{3}(1)+senSize(1)/2 rateloc{3}(2)+downtodot+senSize(2)/2],...
    [rateloc{4}(1)-senSize(1)/2 rateloc{4}(2)+downtodot-senSize(2)/2 rateloc{4}(1)+senSize(1)/2 rateloc{4}(2)+downtodot+senSize(2)/2],...
    [rateloc{5}(1)-senSize(1)/2 rateloc{5}(2)+downtodot-senSize(2)/2 rateloc{5}(1)+senSize(1)/2 rateloc{5}(2)+downtodot+senSize(2)/2]};

%% Instruction
Screen(win, 'FillRect', gray);
Screen('DrawTexture', win, inst, [], instLoc);
Screen('Flip', win);

done = 0;
scanPulse=0;
while scanPulse~=1 %wait for a pulse
    [keyIsDown, ~, keyCode] = KbCheck(Scanner); % Here change Scanner -> -3
    if keyIsDown
        if keyCode(syncNum)
            robot.keyPress(KeyEvent.VK_F2);
            robot.keyRelease(KeyEvent.VK_F2);
            scanPulse = 1;
            firstS = GetSecs;
            trigger = 1;
%             starttime = datestr(clock,'YYYY/mm/dd HH:MM:SS:FFF');
%             fprintf(stimFile,'%s', starttime);
            start = GetSecs;
            break;
        end
    end
end

%% Main Experiment
total_start = GetSecs;
Screen('FillRect', win, gray);
Screen('Flip', win);
total_dur = 8;
WaitSecs(blankTime_first);
% blank = GetSecs;
% fprintf(stimFile,'\nblank %1.4f', blank - start);
dotSize = 10; %radius [px]
fixationDot = [-dotSize -dotSize dotSize dotSize];
dotsize = 48;
blackdot = [-dotsize/2 -dotsize/2 dotsize/2 dotsize/2];
fixationDot = CenterRect(fixationDot, rect);
reddot = [-reddotsize/2 -reddotsize/2 reddotsize/2 reddotsize/2];
for t = 1:trialN
    
    trial_start_real = GetSecs - total_start;
    trial_start = GetSecs;

    Screen('FillOVal', win, white, fixationDot);
    Screen('Flip', win);
    WaitSecs(fixTime);
    
    output = f(character_order(t), question_order(t));
    switch output.ch1
        case 'FEMALE'; ch1N = 1;
        case 'MALE'; ch1N = 2;
    end
    
    go = 0;
    resp_start = GetSecs;
    SetMouse(cx, 3*cy/2, win);
    while ~go
        [x,y,button,~,~,~] = GetMouse(win);
        if x < cx - diameter; x = cx - diameter;
        elseif x > cx + diameter; x = cx + diameter; end
        if y < 3*cy/2 - diameter; y = 3*cy/2 - diameter;
        elseif y > 3*cy/2 + diameter; y = 3*cy/2 + diameter; end
        SetMouse(x,y, win);
        if button(1)
            rt_secs = GetSecs;
            rating_time = rt_secs - resp_start;
            go = 1;
        end
        if x < cx-diameter/2
            if y < 3*cy/2; rating = 2; color = [255,0,0];
            elseif y >= 3*cy/2; rating = 1; color = [255,0,0]; end
        elseif (x > cx-diameter/2 && x < cx) || (x > cx && x < cx+diameter/2)
            if y < 3*cy/2; rating = 3; color = [255,0,0]; end
        elseif x == cx
            if y < 3*cy/2; rating = 3; color = [255,0,0];
            elseif y == 3*cy/2; rating = 6; color = [0,0,0];
            end
        elseif x > cx+diameter/2
            if y < 3*cy/2; rating = 4; color = [255,0,0];
            elseif y >= 3*cy/2; rating = 5; color = [255,0,0]; end
        end
%         Screen('DrawTexture', win, tarFace, [], tarLoc);
        
        for k=1:5
            Screen('FillOVal', win, 255, [rateloc{k} rateloc{k}]+blackdot);
        end
        
        Screen('DrawTexture', win, sen_one, [], rateloc_sen{1});
        Screen('DrawTexture', win, sen_two, [], rateloc_sen{2});
        Screen('DrawTexture', win, sen_three, [], rateloc_sen{3});
        Screen('DrawTexture', win, sen_four, [], rateloc_sen{4});
        Screen('DrawTexture', win, sen_five, [], rateloc_sen{5});
        Screen('FillOVal', win, color, [rateloc{rating} rateloc{rating}]+reddot);
        showInstruction(output.question, fontsize, 0, rect);
    end
    if rating == 6; rating = 0; end
    trial_end = GetSecs;
    trial_dur = trial_end - trial_start;
    trial_dur_abs = ceil(trial_dur);
    real_dur = trial_end - total_start;
    total_dur = total_dur + trial_dur_abs;
    
    data.trial(t) = t;
    data.trial_start(t) = trial_start_real;
    data.total_dur(t) = total_dur;
    data.real_dur(t) = real_dur;
    data.trial_dur(t) = trial_dur;
    data.trial_dur_abs(t) = trial_dur_abs;
    data.attr{t} = output.att;
    data.ch1{t} = output.ch1;
    data.pred{t} = output.pred;
    data.ch1N(t) = ch1N;
    data.predN(t) = output.predN;
    data.rating(t) = rating;
    data.rating_time(t) = rating_time;
    fprintf('run: %d, trial: %d, trial_start: %1.4f, trial duration: %1.4f, type: %s, ch1: %s, predicate: %d, rating: %d, rating_time: %1.4f\n',...
        data.RunNo, data.trial(t), data.trial_start(t), data.trial_dur(t), output.att,...
        output.ch1, output.predN, rating, rating_time);
    fprintf(dataFile,'%d,%d,%d,%d,%1.4f,%1.4f,%s,%s,%d,%d,%1.4f\n',...
        data.SN, data.Gender, data.RunNo, data.trial(t), data.trial_start(t),...
        data.trial_dur(t), output.att,...
        output.ch1, output.predN, data.rating(t), rating_time);
    while GetSecs-total_start < total_dur
    end
end

robot.keyPress(KeyEvent.VK_F2);
robot.keyRelease(KeyEvent.VK_F2);
% main = GetSecs;
% fprintf(stimFile,'\nmain %1.4f', main-blank);

Screen('FillRect', win, gray);
Screen('Flip', win);
WaitSecs(blankTime_last);
% blank2 = GetSecs;
% fprintf(stimFile,'\nend %1.4f', blank2-main);

fclose('all');
Screen('CloseAll');
IOPort('CloseAll');
Priority(0); ListenChar(0);
ShowCursor;

%% showinstruction
function showInstruction(txt, txtsize, txtcolor, rect)
% see DrawHighQualityUnicodeTextDemo.m
global win;
% Text files edited with a text editor such as vi or nano.

% type 'listfonts' and find your font from the list.
% In case you're using PC and your Matlab's using Korean as basic
% language, go to 'Preference > General' and choose English as 'Desktop
% language.' Turn on and off Matlab. Type 'listfonts' again.
% see http://cogneuro.or.kr/mediawiki/index.php/PsychToolBox
Screen('TextFont', win, 'NanumGothic', 0);
Screen('TextColor', win, txtcolor);
Screen('TextSize', win, txtsize);

msg = convertStringsToChars(txt);
msg = double(native2unicode(msg));
[tx, ty]    = RectCenter(rect);
tRect = Screen('TextBounds', win, msg);
tRect = CenterRectOnPoint(tRect, tx, ty);
Screen('Preference', 'TextRenderer', 0)
DrawFormattedText(win, msg, 'center','center',0);
Screen('Flip', win);
end