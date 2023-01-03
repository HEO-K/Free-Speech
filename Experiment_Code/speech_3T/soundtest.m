function soundtest
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


% if empty use default
if isempty(Participant) Participant = Experimenter; end
if isempty(Scanner) Scanner = Experimenter; end

Movie_name = fullfile(pwd, 'Instruction', 'sound_check.mp4');
listen=1;
% keyboard


KbName('UnifyKeyNames');
syncNum = KbName('s');
Abort = KbName('q');



%% Screen Settings & Video Encoding
wininfo = Screen('Resolution', 0);   % width,heigth,pixelSize,hz
screenid = max(Screen('Screens'));

% Color Setting
white = WhiteIndex(screenid);
black = BlackIndex(screenid);
gray = (white+black)/2;
fontsize = 40;


% Window Setting
[win,rect] = Screen('OpenWindow', screenid, black);


fps = Screen('FrameRate', screenid);	% frames per second
ifi = Screen('GetFlipInterval', win);
Screen('BlendFunction', win, 'GL_SRC_ALPHA', 'GL_ONE_MINUS_SRC_ALPHA');

blankTime  = (round(5/ifi)-0.5)*ifi;
fixTime    = (round(0.5/ifi)-0.5)*ifi;

fliprate = Screen('GetFlipInterval', win);  % estimate of the monitor flip interval
priorityLevel=MaxPriority(win);
Priority(priorityLevel);
HideCursor;

% Video file encoding

[moviePtr, film_duration, film_fps, film_width, film_height, film_count, film_aspectRatio] = Screen('OpenMovie', win, Movie_name);

% note Screen and Movie info

data.schedule_movie = film_duration;
%% Instruction

Screen(win, 'FillRect', black);
img_file = imread('./Instruction/soundtest.jpg');
img_texture = Screen('MakeTexture', win, img_file);
Screen('DrawTexture', win, img_texture, [], []);
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
end

data.exp_firstS = firstS;

%% Main experiments - Nature
% t1 = GetSecs;
% Screen('FillRect', win, black);
% Screen('Flip', win);
% WaitSecs(blankTime);
t2 = GetSecs;
% fprintf("blank: %1.4f\n", t2-t1);
Screen('SetMovieTimeIndex', moviePtr, 0);    % set film start time to 0
Screen('PlayMovie', moviePtr, 1, [], 1);

showing = 'sound check';
videotexid = 0;
videotime = 0;
count=1;
prev_onset = 0; %Caution ! compare onset time within while loop
lastS = firstS;
done = 0;

data.exp_nature_start = GetSecs;
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

Screen('CloseAll');
IOPort('CloseAll');
Priority(0); ListenChar(0);
ShowCursor;

end