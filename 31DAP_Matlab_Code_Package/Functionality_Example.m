% Clear variables 
clearvars

% Make a PYNQ_obj obj with the default settings.
PYNQ_obj = PYNQ_LIB.PYNQ_ML;
% Write something to the display. Writes each item of a string array to a
% separate line on the display. With maximum 20 characters per line and 6
% lines.
PYNQ_obj.Display_ShowMessage(["Functionality", "example","","Have fun!"]);

%% Set an LED intensity using PWM
% See the syllabus for more information regarding PWM

PWM_period = 2000; % Use a period of 2000 * 10ns = 10 microseconds

PYNQ_obj.SwitchBox_map(PYNQ_obj.LED_CHANNELS(1),"PWM0") % Set input for leds channel to PWM
disp("Slowly switching on LED 1")
for i=0.01:0.05:1   % Starting loop at 0.01 and increasing to 1 with steps of 0.01
    PYNQ_obj.PWM_set(1,PWM_period,i) % Changing the duty cycle to in the end be on the entire time (duty cylce of 1)
    pause(0.02);
end
disp("Finished switching on LED 1")

%% Show the RGB Led"s
PYNQ_obj.RGBLED_set(1,[0 0 1]) % Blue on first RGB LED
PYNQ_obj.RGBLED_set(2,[1 1 0]) % Yellow on second RGB LED

%% Set a pin ("AR2", which is connected to DI0) to high output (3.3V)
PYNQ_obj.SwitchBox_map("AR2","GPIO"); % Map the pin to be a General Purpose IO pin
PYNQ_obj.DigitalPin_set_Dir("AR2","OUT"); % Set its direction to output
PYNQ_obj.DigitalPin_write("AR2",1); % Write a logical 1 (on/true) to it

%% Set DAC 1 (marked DAC0 on board) to 2V output
PYNQ_obj.DAC_initialize(1); % Initialize the first DAC (DAC0 on the PCB)
PYNQ_obj.DAC_setV(1,2); % Set the first DAC to 2V output

%% Read an analog in and switch LEDs using the pushbuttons

PYNQ_obj.SwitchBox_map(PYNQ_obj.LED_CHANNELS(1),"GPIO")  % Set input of LEDS to GPIO pins (buttons)

tic; % Start timer
tNextAction = 0;
interval = 0.5;
MEASUREMENT_TIME = 15; % Duration in seconds

disp("Measuring voltage on A0. Push buttons to switch LEDs")
while toc<MEASUREMENT_TIME
    if toc>tNextAction
        voltage = PYNQ_obj.ADC_PYNQ_read(1);    % Reading voltage over ADC pin 1 (can be connected to the A0 connector)
        fprintf("Measured voltage: %.3g V. Still %.1f seconds to go.\n",...
            voltage, MEASUREMENT_TIME-toc); % Printing the voltage every second
        tNextAction=tNextAction+interval;
    end 
    PYNQ_obj.LEDs_switch(PYNQ_obj.Buttons_read); % Turning the LEDs on with the four buttons
end

%% Read a value of an analog input using the ADS1115

tic; % Start timer
tNextAction = 0;
interval = 0.5;
MEASUREMENT_TIME = 15; % Duration in seconds
% Set ADS1115 first channel ("A0TG"), highest range (6V), and 8 SPS
PYNQ_obj.ADC_Ext_set("A0TG",1,1); 

disp("Measuring voltage on A0 using ADS1115.")
while toc<MEASUREMENT_TIME
    if toc>tNextAction
        voltage = PYNQ_obj.ADC_Ext_read;    % Reading voltage over ADS1115
        fprintf("Measured voltage: %.3g V. Still %.1f seconds to go.\n",...
            voltage, MEASUREMENT_TIME-toc); % Printing the voltage every second
        tNextAction=tNextAction+interval;
    end 
end

%% Read many points fast from the ADS1115
tic; % Start timer
tNextAction = 0.5;
interval = 0.5;
delay = 3000; % interval in microseconds
MEASUREMENT_TIME = 5; % Duration in seconds
PYNQ_obj.ADC_Ext_set("A0TG",5,"SPS860"); % Set ADS1115 first channel ("A0TG"), highest range (6V), and 860 SPS
PYNQ_obj.ADC_Ext_Fast_ClearChannels; % Clear any existing fast data acquisition channels.
PYNQ_obj.ADC_Ext_Fast_Add_Channel("A0TG",1); % Add first channel
PYNQ_obj.ADC_Ext_Fast_Add_Channel("A2TG",1); % Add second channel
PYNQ_obj.ADC_Ext_Fast_Start(delay); % Start the data acquisition on the PYNQ board
% Read the first voltages, see below for more details.
voltagetable = PYNQ_obj.ADC_Ext_Fast_Get_Points;

disp("Measuring voltage fast on A0 and A1 using ADS1115.")
% Keep measuring until the time since start (toc) exceeds the measurement
% time
while toc<MEASUREMENT_TIME
    % If it is time for the next action, get data from the PYNQ board and
    % print something to the command line
    if toc>tNextAction
        % Reading voltage over ADS1115. ADC_Ext_Fast_Get_Points returns a
        % timetable object, which is appended to the existing
        % voltagetable variable.
        newpoints = PYNQ_obj.ADC_Ext_Fast_Get_Points;
        voltagetable = [voltagetable; newpoints] ;    %#ok<AGROW>
        % Print some status information on the command line
        fprintf("Measured %u voltages. Still %.1f seconds to go.\n",...
            size(voltagetable,1), MEASUREMENT_TIME-toc); % Printing the voltage every second        disp(size(voltagetable,1));
        % Set the time for the next activity.
        tNextAction=tNextAction+interval;
    end 
    % Wait a bit
    pause(0.2);
end
PYNQ_obj.ADC_Ext_Fast_Stop;

% Extract from the voltagetable variable only the results from either the
% "A0TG" or "A2TG" channel. They will be put into two new tables.
Channel1Data = voltagetable(voltagetable.Channels=="A0TG",:);
Channel2Data = voltagetable(voltagetable.Channels=="A2TG",:);
% Plot the data from both tables.
plot(Channel1Data.Timestamps,Channel1Data.Voltages,Channel2Data.Timestamps,Channel2Data.Voltages);
%% Add a steppermotor object and show its functionality

%Create the Stepper motor object. Simlar to the PYNQ_obj mentioned above,
%this needs to be run to set up the control of the translation stage. Only
%needs to be run at the start or whenever you reconnect.

% Using the default pins
% StepMot = PYNQ_LIB.PYNQ_StepMot(PYNQ_obj);

% Or using pins to show its functionality using two LED"s and two
% pushbuttons
StepMot = PYNQ_LIB.PYNQ_StepMot(PYNQ_obj,"LD0","LD1","BTN0","BTN1","PWM0");

%Stepper motor movement command. First element is the dir
%StepMot.startMoving(Direction,Frequency [Steps/second],No. Steps (optional));
%Direction: 0 or 1, depending on the direction of motion desired.
%Frequency: The number of steps the stepper motor makes per second [max
%1000].
%No. Steps: 
StepMot.startMoving(1,1000);

%NOTE the execution of this code does not wait for the startMoving command
%is finished! Using the pause function of matlab may help.
pause(1)
StepMot.startMoving(0,1000);
pause(1)
%Stepper motor stop moving command, relevant if no specific No. of steps is
%designated.
StepMot.stopMoving;

% Very slow pulsing showcasing the LED
StepMot.startMoving(0,5);

%% Get a frequency response from the audio ports.
% Get a frequency response between the audio out and audio in ports. Do
% this at 1000 Hz for 100 periods.
frequency = 1000;
nrofperiods = 100;
p = PYNQ_obj.FrequencyResponse_get(frequency,nrofperiods);

% Plot the results in a new figure.
figure;
plot(p);

%% Use the advanced user interface functionality
% Make a PYNQ_UI_obj object
PYNQ_UI_obj = PYNQ_LIB.PYNQ_UI(PYNQ_obj);

% Show a .bmp file on the display
PYNQ_UI_obj.displayImage("Images\PYNQ.bmp");

% Show a textbox on the display
PYNQ_UI_obj.textBox([20 30 230 100],"Hello world!",3,0xFF0000,...
    0x0000FF,0xFFFFFF,3,[2 2],3);

% Show another box on the display
PYNQ_UI_obj.drawBoxWithBorder([70 160 120 200],[255 255 255],[0 0 0],5);

PYNQ_UI_obj.writeText([10 235],"Here some green text",1,0x00FF00,[1 3])