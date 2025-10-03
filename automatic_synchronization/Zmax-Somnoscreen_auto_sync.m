% https://github.com/Niloy333/Wearanize_plus
% Created by Niloy Sikder (scholar.google.com/citations?user=0ALk5j4AAAAJ&hl=en)
% Affiliations: PhD Candidate, Radboud University Medical Center, Donders Institute for Brain, Cognition and Behaviour, Nijmegen, The Netherlands &
% Scientific Assistant, Faculty of Technology and Bionics, Rhine-Waal University of Applied Sciences, Kleve, Germany.
% Contact: niloy.sikder@donders.ru.nl, niloy.sikder@hochschule-rhein-waal.de.
% Project Supervision: Matthias Krauledat, Paul Zerr, and Martin Dresler.
% Copyright (c) 2025 Niloy Sikder

% Description:
%   Align Zmax accelerometry with PSG movement via cross-correlation and
%   generate comparison plots for visual validation.
% Requirements:
%   - MATLAB R2023b+
%   - EDF files: Zmax dX/dY/dZ and Somno "Move." channel.
%   - Annotation table containing truncation/sync points.
% Usage:
%   Adjust paths below and run this script.

%% Paths & Globals
global root_dir sm_zmax sm_psg
root_dir   = 'C:\3028005.01_Local\Wearanize+_dataset_v1.0\1.Raw_data';

points_dir = "C:\3028005.01_Local\Wearanize+_dataset_v1.0\5.Manual_synchronization\Manual sync zmax psg emp actpal.xlsx";
points_data = readtable(points_dir);
points_data.SubjectID = strrep(points_data.SubjectID, '''', '');

psg_out_dir = "C:\Sciebo_files\Truncate_Sync\Wearanize+_corr_sync\Zmax_psg";

sm_zmax    = 256;
sm_psg     = 128;

%% Discover Zmax files
file_list = {};
file_list = search_files(root_dir, 'dX.edf', file_list);
file_list = string(file_list(:));

%% Main Processing Loop
start_sec_pred = table([], [], 'VariableNames', {'SubjectID', 'psg_pred_start_sec'});

% Loop bounds preserved as in the provided script (single subject at index 81).
for i = 81:1:81
    if i ~= 71 && i ~= 56
        subject_dir = file_list(i);
        path_parts  = split(subject_dir, filesep);
        sub_id      = path_parts{end-2};
        sm_zmax     = 256;

        if points_data.PSG_start_sec(i) > 0 && points_data.PSG_offset(i) == 0
            % Load and prepare signals
            zmax_agg  = zmax_data_read(sub_id, points_data);
            somno_mov = read_somno_mov(sub_id);

            % Resample Zmax to PSG rate
            orig_time = (0:length(zmax_agg)-1) / sm_zmax;
            new_time  = (0:(length(zmax_agg)/2 - 1)) / sm_psg; % 256 → 128 halves samples
            zmax_agg  = interp1(orig_time, zmax_agg, new_time, 'pchip');
            sm_zmax   = sm_psg;

            % Preprocess
            zmax_comp  = process_zmax(zmax_agg);
            somno_comp = process_somno(somno_mov);

            % Taper to reduce edge effects in xcorr
            w = hann(length(somno_comp))';
            somno_comp = somno_comp .* w;
            w = hann(length(zmax_comp))';
            zmax_comp  = zmax_comp  .* w;

            % One-sided cross-correlation (non-negative lags only)
            if length(somno_comp) > length(zmax_comp)
                maxlag = length(somno_comp) - length(zmax_comp);
                [corr_values, lags] = xcorr(somno_comp, zmax_comp, maxlag, 'none');

                positive_indices = lags >= 0;
                corr_values = corr_values(positive_indices);
                lags        = lags(positive_indices);

                [~, max_index] = max(corr_values);
                start_index = lags(max_index);
                start_index = min(start_index, length(somno_comp) - length(zmax_comp) + 1);
                end_index   = start_index + length(zmax_comp) - 1;

                somno_comp_aligned = somno_comp(start_index:end_index);
                start_index_sec    = round(start_index / sm_zmax);

                % Manual window for comparison
                somno_man_start_idx = (points_data.PSG_start_sec(i) - 1) * sm_zmax + 1;
                somno_man_end_idx   = points_data.PSG_end_sec(i) * sm_zmax;
                somno_man           = somno_comp(somno_man_start_idx:somno_man_end_idx);
                diff_sec            = start_index_sec - points_data.PSG_start_sec(i);

                % Plot & save
                out_fl = fullfile(psg_out_dir, [sub_id, '.jpg']);
                plot_fig(sub_id, zmax_comp, somno_man, somno_comp_aligned, diff_sec, out_fl);

                % Collect predictions
                start_sec_pred = [start_sec_pred; {sub_id, start_index_sec}];
            end
        end
    end

    % Free large arrays in long runs
    clear start_index_sec zmax_comp zmax_agg somno_comp somno_mov corr_values max_index start_index end_index
end

%% Optional: Write predictions (kept disabled)
% start_sec_pred = join(start_sec_pred, points_data(:, {'SubjectID', 'PSG_start_sec'}), 'Keys', 'SubjectID');
% writetable(start_sec_pred, 'C:\Users\NSI\sciebo\Truncate_Sync\W+_corr_sync_zmax_somno.xlsx');

%% Local Functions
function zmax_agg = zmax_data_read(subj, points_data)
%ZMAX_DATA_READ Read EDF XYZ channels for a subject, crop to truncation window,
%and return Euclidean magnitude.
    global root_dir
    zmax_files = ['dX.edf'; 'dY.edf'; 'dZ.edf'];
    zmax_path  = strjoin({root_dir, subj, '2.Zmax'}, '\');
    zmax_dx    = zmax_edfread(strjoin({zmax_path, zmax_files(1, :)}, '\'));
    zmax_dy    = zmax_edfread(strjoin({zmax_path, zmax_files(2, :)}, '\'));
    zmax_dz    = zmax_edfread(strjoin({zmax_path, zmax_files(3, :)}, '\'));

    [start_idx, end_idx, ~] = read_trun_pnts(subj, points_data);
    zmax_dx = zmax_dx(1, start_idx:end_idx);
    zmax_dy = zmax_dy(1, start_idx:end_idx);
    zmax_dz = zmax_dz(1, start_idx:end_idx);

    zmax_agg = euclidean_norm([zmax_dx; zmax_dy; zmax_dz]);
end

function flattened = zmax_edfread(zmaxpath)
%ZMAX_EDFREAD Read a Zmax EDF where each row is a 1-second cell vector and
%return a single precision row vector at sm_zmax Hz.
    global sm_zmax
    zmax      = edfread(zmaxpath);
    zmax      = table2array(zmax);
    flattened = zeros(1, length(zmax) * sm_zmax, 'single');
    for i = 1:length(zmax)
        flattened((i-1)*sm_zmax + 1 : i*sm_zmax) = zmax{i};
    end
end

function zmax_comp = process_zmax(zmax_agg)
%PROCESS_ZMAX Rectify around 1 g, center, amplify, clip, and threshold.
    zmax_agg(zmax_agg < 1) = 2 - zmax_agg(zmax_agg < 1);
    zmax_agg = zmax_agg - 1;
    zmax_comp = zmax_agg * 100;
    cut_off = 100; zmax_comp(zmax_comp > cut_off) = cut_off;
    thr = mean(zmax_comp) + 6 * std(zmax_comp);
    zmax_comp(zmax_comp <= thr) = 0;
end

function somno_comp = process_somno(somno_mov)
%PROCESS_SOMNO Scale, clip, and threshold PSG movement.
    somno_mov = double(somno_mov);
    somno_comp = somno_mov / 10;
    cut_off = 100; somno_comp(somno_comp > cut_off) = cut_off;
    thr = mean(somno_comp) + 6 * std(somno_comp);
    somno_comp(somno_comp <= thr) = 0;
end

function [start_point, end_point, dur]  = read_trun_pnts(subj, points_data)
%READ_TRUN_PNTS Compute sample indices of the Zmax truncation window.
    global sm_zmax
    idx = find(strcmp(points_data.SubjectID, subj));
    start_sec   = points_data.Zmax_start_sec(idx);
    end_sec     = points_data.Zmax_end_sec(idx);
    start_point = (start_sec - 1) * sm_zmax + 1;
    end_point   = end_sec * sm_zmax;
    dur         = points_data.Zmax_dur_sec(idx); %#ok<NASGU>
end

function somno_mov = read_somno_mov(subj)
%READ_SOMNO_MOV Read Somno EDF "Move." channel and return a single precision
%row vector at sm_psg Hz.
    global root_dir sm_psg
    somno_channels = {'Move.'};
    somno_path = strjoin({root_dir, subj, "1.Somno"}, '\');
    somno_edf  = dir(fullfile(somno_path, '*.edf'));
    if length(somno_edf) ~= 1
        error('length(somno_edf) = %d.', length(somno_edf));
    end
    somno_path = somno_path + "\" + string(somno_edf(1).name);
    somno_tbl  = edfread(somno_path, "SelectedSignals", somno_channels);
    somno_cell = table2array(somno_tbl);

    flattened = zeros(1, length(somno_cell) * sm_psg, 'single');
    for k = 1:length(somno_cell)
        flattened((k-1)*sm_psg + 1 : k*sm_psg) = somno_cell{k};
    end
    somno_mov = flattened;
end

function eu_norm = euclidean_norm(all_channels)
%EUCLIDEAN_NORM Compute Euclidean norm of tri-axial data (rows 1:3).
    if size(all_channels, 1) < 3
        error('Input matrix must have at least 3 rows for x, y, z data.');
    end
    eu_norm = sqrt(sum(all_channels(1:3, :).^2, 1));
end

function plot_fig(sub_id, zmax_comp, somno_man, somno_comp_aligned, diff_sec, out_fl)
%PLOT_FIG Save comparison plots: Zmax vs manual PSG window, Zmax vs xcorr-aligned PSG.
    global sm_zmax

    % Invert Somno for visual contrast
    somno_comp_aligned = int16(0) - int16(somno_comp_aligned);
    somno_man          = int16(0) - int16(somno_man);

    time_vector = single((1/sm_zmax : 1/sm_zmax : length(zmax_comp)/sm_zmax) / 3600);

    fig = figure('Visible', 'off', 'Units', 'inches', 'Position', [1, 1, 10, 6]); 
    tiledlayout(2, 1, 'TileSpacing', 'compact', 'Padding', 'compact');

    all_data = [int16(zmax_comp), somno_man, somno_comp_aligned];
    y_min = min(all_data) - 10; 
    y_max = max(all_data) + 10;
    if y_min >= y_max, y_min = y_min - 5; y_max = y_max + 5; end

    nexttile;
    plot(time_vector, zmax_comp);
    hold on; plot(time_vector, somno_man);
    title(sprintf('%s: Zmax ACC agg (blue) & Somno manual sync (green)', sub_id));
    ylim([y_min, y_max]); xlim([min(time_vector) max(time_vector)]); grid on;

    nexttile;
    plot(time_vector, zmax_comp);
    hold on; plot(time_vector, somno_comp_aligned);
    title(sprintf('%s: Zmax ACC agg (blue) & Somno correlation sync (red), difference: %d sec', sub_id, diff_sec));
    ylim([y_min, y_max]); xlim([min(time_vector) max(time_vector)]); grid on;

    [folder_path, ~, ~] = fileparts(out_fl);
    if ~exist(folder_path, 'dir'), mkdir(folder_path); end
    set(fig, 'PaperUnits', 'inches', 'PaperSize', [10, 6], 'PaperPosition', [0, 0, 10, 6]);
    print(fig, out_fl, '-djpeg', '-r200'); 
    close(fig);
end

function file_list = search_files(current_dir, target_file, file_list)
%SEARCH_FILES Recursively collect paths of files named target_file.
    entries = dir(current_dir);
    for ii = 1:length(entries)
        name = entries(ii).name;
        if strcmp(name, '.') || strcmp(name, '..'), continue; end
        full_path = fullfile(current_dir, name);
        if entries(ii).isdir
            file_list = search_files(full_path, target_file, file_list);
        else
            if strcmp(name, target_file)
                file_list{end+1} = full_path; %#ok<AGROW>
            end
        end
    end
end
