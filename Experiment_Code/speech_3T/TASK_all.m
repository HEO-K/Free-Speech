% 1. 실험 전에 꼭 소리 키우기 (70이상)
% 2. 헤드폰인지 확인
% 3. 무조건 연결 먼저 하고 매트랩 킬것


%% Initialize
close all; 
clear;
IOPort('Closeall'); Screen('Close'); Screen('Closeall');
clc;
KbName('UnifyKeyNames');

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
space = 40;



audio_device = PsychPortAudio('GetDevices');
fprintf("\n--------\nMIC Info\n--------\n")
fprintf(strcat("Name should be 'USB Audio CODEC': ", audio_device(2).DeviceName))
fprintf(strcat("\nInput channel shoud be 2: ", num2str(audio_device(2).NrInputChannels)))

% Sub number
subName = input('\nSubject(bids)                               >> ','s');
if length(subName) < 1
    subName = 'test';
end

% behavior?
listen = input('\nBehavior?(Scan:1, Beh:2)                    >> ','s');
listen = str2double(listen);

% speech random 
seed_number = num2str(GetSecs());
seed_number = seed_number(end-2:end);
rng(str2num(seed_number));
speechrun = randperm(3);
listeningrun = randperm(2);

% taskname
speechs = ["speechFREE", "speechTOPIC", "speechSTROLL"];
listenings = ["listeningFREE", "listeningTOPIC"];
fprintf("\n--------------\ntask sequence\n--------------\n");
fprintf("REST\n")
i=0;
for runName=speechrun
    i = i+1;
    taskname = speechs(runName);
    if i == 3
        fprintf("T1\n")
    end
    fprintf('%s\n', taskname);
end

for runName=listeningrun
    taskname = listenings(runName);
    fprintf('%s\n', taskname);
end

fprintf("\nPress ENTER to continue, sound check first");
WaitSecs(1);
while 1
    [keyIsDown, secs, keyCode, deltaSecs] = KbCheck(Experimenter);
    if keyCode(space)
        break;
    end
end


if listen==1
    soundtest;
end
clc

fprintf("\n\nNext task: REST\nPress ENTER to continue");
while 1
    [keyIsDown, secs, keyCode, deltaSecs] = KbCheck(Experimenter);
    if keyCode(space)
        break;
    end
end
% Resting
resting(subName, listen);
% speech & T1
i=0;
for runName=speechrun
    clc
    i = i+1;
    taskname = speechs(runName);
    runName = num2str(runName);
    if i == 3
        WaitSecs(2);
        fprintf("\n\nT1\nPress ENTER if T1 ends");
        while 1
            [keyIsDown, secs, keyCode, deltaSecs] = KbCheck(Experimenter);
            if keyCode(space)
                break;
            end
        end
    end
    WaitSecs(2);
    fprintf("\n\nNext task: %s\nPress ENTER to continue", taskname);
    while 1
        [keyIsDown, secs, keyCode, deltaSecs] = KbCheck(Experimenter);
        if keyCode(space)
            break;
        end
    end
    speech(subName, runName, listen);
end

i = 0;
for runName=listeningrun
    clc
    i = i+1;
    taskname = listenings(runName);
    runName = num2str(runName);
    WaitSecs(2);
    fprintf("\n\nNext task: %s\nPress ENTER to continue", taskname);
    while 1
        [keyIsDown, secs, keyCode, deltaSecs] = KbCheck(Experimenter);
        if keyCode(space)
            break;
        end
    end
    listening(subName, runName, listen);
end


fprintf("\n\nScan finished, STT is started\n");
sub_dir = "./_DATA/sub-"+subName+'/';
file = dir(sub_dir+'*.wav');
for i=1:3
    stt_command = "python3 ./Clova_STT.py " + sub_dir + " " + file(i).name;
    system(stt_command);
end

