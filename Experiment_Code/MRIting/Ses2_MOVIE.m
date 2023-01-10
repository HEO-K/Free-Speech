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

% path
addpath(genpath(fullfile(pwd)));
curr_dir = pwd;
data_dir = fullfile(pwd,'Inst', 'MOVIE');

% Enter subject ID
gName = input('\n\nGroup (ex. 01, 02)                       >> ','s');
if length(gName) < 1
    gName = 'test';
end

% Sub number
subName = input('\nSubject (1:male, 2:female)               >> ','s');

% Run number
runName = input('\nRun (0: soundtest, 1~3: main)            >> ','s');
if length(runName) < 1
    runName = '0';
end

% Is it behavior?
listen = str2double(input('\nExperiment type (1: scan, 2:test)        >> ','s'));
if isnan(listen)
    listen = 2;
end


%% movie file selection
moviefilename = sprintf('movie_run_0%s.mp4',runName);
Movie_name = fullfile(pwd, 'Inst', 'MOVIE', moviefilename);


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
Left  = KbName('1!');
Right = KbName('2@');
Rate  = KbName('3#');


%% Screen Settings & Video Encoding
%global win
wininfo = Screen('Resolution', 0);   % width,heigth,pixelSize,hz
screenid = max(Screen('Screens'));

% Color Setting
white = WhiteIndex(screenid);
black = BlackIndex(screenid);
gray = (white+black)/2;
fontsize = 40;

% Window Setting
if listen == 1
    [win,rect] = Screen('OpenWindow', screenid, black);
elseif listen == 2
    [win,rect] = Screen('OpenWindow', screenid, black, [0 0 1024 768]);
end

fps = Screen('FrameRate', screenid);	% frames per second
ifi = Screen('GetFlipInterval', win);
Screen('BlendFunction', win, 'GL_SRC_ALPHA', 'GL_ONE_MINUS_SRC_ALPHA');
fprintf("*** Interframe interval = %4.4fms\n", ifi*1000);

blankTime  = (round(10/ifi)-0.5)*ifi;
fixTime    = (round(0.5/ifi)-0.5)*ifi;

fliprate = Screen('GetFlipInterval', win);  % estimate of the monitor flip interval
priorityLevel=MaxPriority(win);
Priority(priorityLevel);
HideCursor;

% Video file encoding

[moviePtr, film_duration, film_fps, film_width, film_height, film_count, film_aspectRatio] = Screen('OpenMovie', win, Movie_name);

data.schedule_movie = film_duration;
%% Instruction

Screen(win, 'FillRect', black);
dotSize = 10; %radius [px]
fixationDot = [-dotSize -dotSize dotSize dotSize];
fixationDot = CenterRect(fixationDot, rect);
Screen('FillOVal', win, white, fixationDot);
Screen('Flip', win);


done = 0;
scanPulse=0;
if listen == 1
    while scanPulse~=1 %wait for a pulse
        [keyIsDown, ~, keyCode] = KbCheck(Scanner); % Here change Scanner -> -3
        if keyIsDown
            if keyCode(syncNum)
                scanPulse = 1;
                firstS = GetSecs;
                trigger = 1;
                break;
            end
        end
    end
    
elseif listen == 2
    while(~done)
        [keyIsDown, secs, keyCode, deltaSecs] = KbCheck;
        if keyCode(syncNum)
            firstS = GetSecs;
            trigger =-1;
            done = 1;
        end
    end
end

data.exp_firstS = firstS;

%% Main experiments - Nature
t1 = GetSecs;
Screen('FillRect', win, black);
Screen('Flip', win);
WaitSecs(blankTime);
t2 = GetSecs;
fprintf("blank: %1.4f\n", t2-t1);

Screen('SetMovieTimeIndex', moviePtr, 0);    % set film start time to 0
Screen('PlayMovie', moviePtr, 1, [], 1);

showing = 'movie';
videotexid = 0;
videotime = 0;
count=1;
prev_onset = 0; %Caution ! compare onset time within while loop
lastS = firstS;
done = 0;

data.exp_movie_start = GetSecs;
while (~done)
    % plot
    tex = Screen('GetMovieImage',win,moviePtr);
    
    % taking S
    if listen == 1
        [keyIsDown, ~, keyCode] = KbCheck(Scanner);
        if keyIsDown
            if keyCode(syncNum) && (GetSecs - lastS > 1.9 )
                trigger = trigger+1;
                lastS = GetSecs;
            end
        end
    end
    
    % abortion code 'q'
    if listen == 1
        [keyIsDown_exp, ~, keyCode_exp] = KbCheck(Experimenter);
    elseif listen == 2
        [keyIsDown_exp, secs, keyCode_exp] = KbCheck;
    end
    if keyIsDown_exp
        if keyCode_exp(Abort)
            done = 1;
            break;
        end
    end
    
    % end when it's done
    if tex <=0
        done = 1;
        break;
    end
    
    Screen('DrawTexture',win,tex);
    vbl = Screen('Flip',win);
    
    % taking S
    if listen == 1
        [keyIsDown, ~, keyCode] = KbCheck(Scanner);
        if keyIsDown
            if keyCode(syncNum) && (GetSecs - lastS > 1.9 )
                trigger = trigger+1;
                lastS = GetSecs;
            end
        end
    end
    
    % log
    onset = vbl - firstS ;
    count = count + 1;
    prev_onset = onset;
    
    Screen('Close',tex);
end

Screen('PlayMovie', moviePtr,0);    % stop playback
Screen('CloseMovie', moviePtr);

data.exp_movie_end = GetSecs;
fprintf("movie delay: %1.4f\n",data.exp_movie_start - t2);
fprintf("movie duration: %1.4f\n", data.exp_movie_end - data.exp_movie_start);

fclose('all');
Screen('CloseAll');
IOPort('CloseAll');
Priority(0); ListenChar(0);
ShowCursor;

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