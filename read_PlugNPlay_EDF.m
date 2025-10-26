%% read_PlugNPlay_EDF_matlab_simple.m
% Script to read and process subject data from the PlugNPlay version of the Wearanize+ dataset.
% Author: Niloy Sikder
% Affiliations:
% - Radboud University Medical Center, Donders Institute for Brain, Cognition and Behaviour, Nijmegen, The Netherlands
% - Faculty of Technology and Bionics, Rhine-Waal University of Applied Sciences, Kleve, Germany
% Contact: niloy.sikder@donders.ru.nl, niloy.sikder@hochschule-rhein-waal.de
% Google Scholar: https://scholar.google.com/citations?user=0ALk5j4AAAAJ&hl=en
% ORCID: 0000-0002-9016-6105
% Tested on MATLAB 2023b

%% Input
% Root dataset directory
data_dir = "C:\3028005.01_Local\Wearanize+_dataset_v1.0\Wearanize+_PlugNPlay";

%% Reading single-subject data
example_sub = 'sub-005';
example_edf = fullfile(data_dir, example_sub, 'eeg', [example_sub '_task-sleep_eeg.EDF']);

% read using edfread (returns timetable)
TT = edfread(example_edf);
fprintf('%s was read successfully\n', example_edf);

% get the labels of channels
signal_labels = TT.Properties.VariableNames;
n_channels = numel(signal_labels);

fprintf('Number of available channels: %d\n', n_channels);
for i = 1:numel(signal_labels)
    fprintf('%s\n', signal_labels{i});
end

% Get a sample channel's data: 'PSG_F3'
signal_name = 'PSG_F3';
idx = find(strcmp(signal_labels, signal_name), 1);
if ~isempty(idx)
    col = TT.(signal_labels{idx});
    PSG_F3 = single(vertcat(col{:}));
    fprintf('Read channel %s (samples: %d)\n', signal_name, numel(PSG_F3));
else
    warning('%s not found in this file.', signal_name);
end

% Get the corresponding manual sleep scores: 'PSG_Manual_score'
signal_name2 = 'PSG_Manual_score';
idx2 = find(strcmp(signal_labels, signal_name2), 1);
if ~isempty(idx2)
    col2 = TT.(signal_labels{idx2});
    PSG_Manual_score = col2(:);
    fprintf('Read channel %s (samples: %d)\n', signal_name2, numel(PSG_Manual_score));
else
    warning('%s not found in this file.', signal_name2);
end

% Read all channels' data and store them in a struct (like Python dict)
all_signals = struct();
for i = 1:numel(signal_labels)
    name = signal_labels{i};
    data_col = TT.(name);
    fld = matlab.lang.makeValidName(name);
    all_signals.(fld) = data_col(:);
end
fprintf('All channels'' data has been read for the example file.\n');

%% Reading multi-subject data

edfFilesLower = dir(fullfile(data_dir, '**', '*.edf'));
edfFilesUpper = dir(fullfile(data_dir, '**', '*.EDF'));
edfFiles = [edfFilesLower; edfFilesUpper];

fprintf('\nFound %d EDF files.\n', numel(edfFiles));

% container for extracted channels across subjects
all_subs_data = struct();

% loop through each file
for k = 1:numel(edfFiles)
    filePath = fullfile(edfFiles(k).folder, edfFiles(k).name);
    [~, filenameNoExt] = fileparts(edfFiles(k).name);   % e.g., 'sub-005_task-sleep_eeg'
    
    % get subject id the same way Python did: filename.split("_")[0]
    parts = split(filenameNoExt, '_');
    sub_id = parts{1};   % e.g., 'sub-005'
    fprintf('Reading data from %s...\n', sub_id);
    
    % read EDF file
    TT2 = edfread(filePath);    
    labels2 = TT2.Properties.VariableNames;
    
    % attempt to read the two channels and store them
    channelsToGet = {'PSG_F3', 'PSG_Manual_score'};
    for ci = 1:numel(channelsToGet)
        ch = channelsToGet{ci};
        idx_ch = find(strcmp(labels2, ch), 1);
        if ~isempty(idx_ch)
            col = TT2.(labels2{idx_ch});
            key = matlab.lang.makeValidName([sub_id '_' ch]);   % safe field name
            all_subs_data.(key) = col(:);
        else
            fprintf('\t%s was not found in %s\n', ch, sub_id);
        end
    end
end

fprintf('\nAll subjects'' data extraction finished. Extracted channels are in "all_subs_data".\n');
