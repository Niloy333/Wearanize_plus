%% Wearanize+ Dataset Analysis Script (MATLAB Version)
% Script to read and process subject data from the PlugNPlay version of the Wearanize+ dataset
%
% Author: Niloy Sikder
% Affiliations:
% - Radboud University Medical Center, Donders Institute for Brain, Cognition and Behaviour, Nijmegen, The Netherlands
% - Faculty of Technology and Bionics, Rhine-Waal University of Applied Sciences, Kleve, Germany
% Contact: niloy.sikder@donders.ru.nl, niloy.sikder@hochschule-rhein-waal.de
% Google Scholar: https://scholar.google.com/citations?user=0ALk5j4AAAAJ&hl=en
% ORCID: 0000-0002-9016-6105

%% Initialize Environment
clc
clear all
close all

%% Load a Sample Subject's Data
% Note: This code was written and tested on Matlab R2023b. 
% Previous versions may not read and process Parquet files as expected.
data_dir = "C:\Wearanize+_PlugNPlay_v1.0"  % This is the data directory; %update as needed.
sub_1 = 'Sub005s1';
sub_dir = fullfile(data_dir, [sub_1 '.parquet']);

% Parquetread() does not read the RowNames as indexes. Force RowNames:
% Read data with proper indexing
sub_data = parquetread(sub_dir);
sub_data.Properties.RowNames = sub_data.x__index_level_0__;
sub_data.x__index_level_0__ = [];  % Remove the temporary index column

% Display dataset structure
disp("Dataset Columns:");
disp(sub_data.Properties.VariableNames);

%% Data Description
% Column Overview:
% 1. 'SubjectID': Unique identifier for the subject.
% 2. 'Device': Name of the recording device.
%    Devices: Zmax, PSG, Empatica, ActivPAL.
% 3. 'NumOfSignals': Number of signals recorded in 'SignalData'.
% 4. 'SignalLabel': List of signal names recorded by the device.
%    Example: {'Zmax EEG L', 'Zmax EEG R', 'Zmax dX', etc.}.
% 5. 'SignalStartDateTime': Start date and time of each signal's recording.
%    Format: "yyyy-MM-dd HH:mm:ss". For Zmax, the start times are unreliable.
% 6. 'SamplingRate': Sampling rate of each signal.
% 7. 'SignalDurationSec': Duration of each signal in seconds.
% 8. 'SignalLength': Length of each signal in data points.
% 9. 'SignalMin'/'SignalMax': Minimum and maximum values of signals.
% 10. 'SignalType'/'SignalUnit': Signal modalities (e.g., EEG, EMG) and units.
% 11. 'SignalData': Actual recorded data for each signal.
% 12. 'SleepScoreEpochs': Number of 30-second epochs in associated sleep scores.
% 13. 'SleepScores': Available sleep scores identified from PSG and Zmax data.

% Notes:
% - MATLAB does not allow symbols (:, ., +) in column names. For Somnoscreen, Use:
%   signal_labels_psg = ["A1", "A2", "C3", "C3_A2", "C4", "C4_A1", "ECG2", "EMG", "EMG_", ...
%       "EMG__1", "EOG1", "EOG1_A1", "EOG1_A2", "EOG2", "EOG2_A1", "EOG2_A2", "F3", "F3_A2", ...
%       "F4", "F4_A1", "Move_", "O1", "O1_A2", "O2", "O2_A1", "Pos_"];
% - MATLAB standardizes the dictionary structure by aggregating keys across rows.
% - Use 'SignalLabel' as the definitive key for fetching data from a column. 
%   To extract data from columns (from SignalStartDateTime to SignalData), 
%   use only the keys present in the SignalLabel column for that specific device, disregarding any empty or aggregated keys.
% - In the 'SleepScores' column, PSG has two sets of scores:
%       - 'Manual': Manual sleep stages identified from PSG data.
%       - 'Usleep': Autoscores from the U-Sleep v2.0 model.
% - PSG scores (manual or Usleep) may not always be present. Always check before reading.
%% Example Usage
% Subject and device info
subject_id = sub_data.SubjectID("Zmax");
device_name = sub_data.Device("Zmax");
disp("Subject ID: " + subject_id + ", Device: " + device_name);

% Signal metadata
num_signals = sub_data.NumOfSignals("Zmax");
signal_labels = sub_data.SignalLabel("Zmax");
signal_labels = signal_labels{:};
disp("Number of Signals: " + string(num_signals));
disp("Labels:");
disp(signal_labels);

% PSG (Somnoscreen) Start Times (with MATLAB-valid signal names)
signal_labels_psg = ["A1","A2","C3","C3_A2","C4","C4_A1","ECG2","EMG","EMG_",...
              "EMG__1","EOG1","EOG1_A1","EOG1_A2","EOG2","EOG2_A1",...
              "EOG2_A2","F3","F3_A2","F4","F4_A1","Move_","O1","O1_A2",...
              "O2","O2_A1","Pos_"];

signal_start_times = sub_data.SignalStartDateTime("PSG", signal_labels_psg);
signal_start_date_times = [];
for i= 1: 1: length(signal_labels_psg)
    signal_start_date_times = [signal_start_date_times; datetime(signal_start_times{1,i}, 'InputFormat', 'yyyy-MM-dd HH:mm:ss')];
end


% Signal characteristics
sampling_rates = sub_data.SamplingRate("Zmax", signal_labels);
signal_durations = sub_data.SignalDurationSec("Zmax", signal_labels);
signal_lengths = sub_data.SignalLength("Zmax", signal_labels);
disp("Sampling Rates:"); disp(sampling_rates);
disp("Durations:"); disp(signal_durations);
disp("Lengths:"); disp(signal_lengths);

%SignalData
signal_data_zmax_eegl = sub_data.SignalData("Zmax", :).EEGL{:};
signal_data_psg_f3 = sub_data.SignalData("PSG", :).F3_A2{:};

%%
signal_data_psg_o1 = sub_data.SignalData("PSG", :).O1{:};
a = 1975;    % Lower bound of target range
b = -1976;   % Upper bound of target range

% Find min and max of the input signal
X_min = min(signal_data_psg_o1);
X_max = max(signal_data_psg_o1);

% Perform min-max normalization
signal_data_psg_o1_norm = ((signal_data_psg_o1 - X_min) / (X_max - X_min)) * (b - a) + a;
max(signal_data_psg_o1_norm)
min(signal_data_psg_o1_norm)

%%
% Sleep scores
psg_scores = sub_data.SleepScores("PSG", :);
if ismember('Manual', psg_scores.Properties.VariableNames)
    if ~ismissing(psg_scores.Manual)
        manual_scores = psg_scores.Manual{:};
    end
end
if ismember('Usleep', psg_scores.Properties.VariableNames)
    if ~ismissing(psg_scores.Usleep)
        usleep_scores = psg_scores.Usleep{:};
    end
end

%% Utility Notes
% 1. MATLAB requires different handling of nested tables compared to Python dicts
% 2. Use {:} for cell dereferencing and {} for table cell access
% 3. Field existence checks crucial due to potential missing scores
% 4. Memory management important for large datasets - clear unused variables
