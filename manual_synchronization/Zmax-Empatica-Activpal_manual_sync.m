% https://github.com/Niloy333/Wearanize_plus
% Created by Niloy Sikder (scholar.google.com/citations?user=0ALk5j4AAAAJ&hl=en)
% Affiliations: PhD Candidate, Radboud University Medical Center, Donders Institute for Brain, Cognition and Behaviour, Nijmegen, The Netherlands &
% Scientific Assistant, Faculty of Technology and Bionics, Rhine-Waal University of Applied Sciences, Kleve, Germany.
% Contact: niloy.sikder@donders.ru.nl, niloy.sikder@hochschule-rhein-waal.de.
% Project Supervision: Matthias Krauledat, Paul Zerr, and Martin Dresler.
% Copyright (c) 2025 Niloy Sikder

% Description:
%   Plot Zmax, Empatica, and ActivPAL accelerometry for a subject, including
%   Zmax truncation markers from the sync table, with interactive data cursor.
%   MATLAB R2023b+
% Requirements:
%   - EDF files: Zmax dX/dY/dZ under 2.Zmax
%   - Empatica ZIP with ACC.csv under 3.Empatica
%   - ActivPAL *-Accelerometer.csv under 4.Activpal
%   - MATLAB Signal Processing Toolbox (for edfread)

% File: overlay_zmax_emp_actpal.m
% Description:
%   Plot Zmax, Empatica, and ActivPAL accelerometry for a subject, including
%   Zmax truncation markers from the sync table, with interactive data cursor.
%
% Requirements:
%   - EDF files: Zmax dX/dY/dZ under 2.Zmax
%   - Empatica ZIP with ACC.csv under 3.Empatica
%   - ActivPAL *-Accelerometer.csv under 4.Activpal
%   - MATLAB Signal Processing Toolbox (for edfread)

clc
close all
clearvars

%% Configuration and globals
global root_dir sm_zmax sm_emp sm_actpal
root_dir = 'C:\3028005.01_Local\Wearanize+_dataset_v1.0\1.Raw_data';
sm_zmax  = 256;
sm_emp   = 32;
sm_actpal= 20;

%% Inputs
zmax_sync_info = readtable("C:\Sciebo_files\_24. Wrnzp_data_paper\Manual sync zmax psg emp actpal.xlsx");
zmax_sync_info.SubjectID = strrep(zmax_sync_info.SubjectID, '''', '');

%% Discover subjects
file_list = {};
file_list = search_files(root_dir, 'dX.edf', file_list);
file_list = string(file_list(:)).';

%% Main loop (kept to single subject index 14 as in the provided script)
for i = 14:1:14
    subject_dir = file_list(i);
    path_parts  = split(subject_dir, filesep);
    sub_id      = path_parts{end-2};

    % Truncation window from table
    row = find(strcmp(zmax_sync_info.SubjectID, sub_id));
    start_sec = zmax_sync_info.Zmax_start_sec(row);
    end_sec   = zmax_sync_info.Zmax_end_sec(row);
    dur       = zmax_sync_info.Zmax_dur_sec(row);

    % Load signals
    [zmax_dx, zmax_dy, zmax_dz] = zmax_data_read(sub_id);
    [emp_dx, emp_dy, emp_dz]    = read_emp_data(sub_id);
    [actpal_dx, actpal_dy, actpal_dz] = read_actpal_data(sub_id);

    % Figure with three panels
    figure('Units', 'normalized', 'OuterPosition', [0 0 1 1]);
    tiledlayout(3, 1, 'TileSpacing', 'compact', 'Padding', 'compact');

    nexttile; zmax_plot(zmax_dx, zmax_dy, zmax_dz, start_sec, end_sec, dur, sub_id);
    nexttile; emp_plot(emp_dx, emp_dy, emp_dz);
    nexttile; actpal_plot(actpal_dx, actpal_dy, actpal_dz);

    % Data cursor copies rounded X to clipboard
    dcm = datacursormode;
    datacursormode on;
    set(dcm, 'UpdateFcn', @myupdatefcn);
end

%% Local functions

function [zmax_dx, zmax_dy, zmax_dz] = zmax_data_read(subj)
%ZMAX_DATA_READ Read Zmax dX/dY/dZ EDFs and return single-precision vectors.
    global root_dir
    zmax_files = ['dX.edf'; 'dY.edf'; 'dZ.edf'];
    zmax_path  = strjoin({root_dir, subj, '2.Zmax'}, '\');
    zmax_dx    = zmax_edfread(strjoin({zmax_path, zmax_files(1, :)}, '\'));
    zmax_dy    = zmax_edfread(strjoin({zmax_path, zmax_files(2, :)}, '\'));
    zmax_dz    = zmax_edfread(strjoin({zmax_path, zmax_files(3, :)}, '\'));
end

function flattened = zmax_edfread(zmaxpath)
%ZMAX_EDFREAD Expand 1-second EDF cells to a per-sample vector at sm_zmax Hz.
    global sm_zmax
    ztbl      = edfread(zmaxpath);
    zcells    = table2array(ztbl);
    flattened = zeros(1, length(zcells) * sm_zmax, 'single');
    for ii = 1:length(zcells)
        flattened((ii-1)*sm_zmax + 1 : ii*sm_zmax) = zcells{ii};
    end
end

function [emp_dx, emp_dy, emp_dz] = read_emp_data(subj)
%READ_EMP_DATA Unzip Empatica archive, read ACC.csv, return axes as row vectors.
    global root_dir
    emp_path  = strjoin({root_dir, subj, '3.Empatica'}, '\');
    emp_zip   = dir(fullfile(emp_path, '*.zip'));
    emp_path2 = strjoin({emp_path, emp_zip.name}, '\');
    dest_dir  = strjoin({emp_path, 'CSVs'}, '\');
    if ~exist(dest_dir, 'dir'), mkdir(dest_dir); end
    unzip(emp_path2, dest_dir);
    emp_xyz   = strjoin({dest_dir, 'ACC.csv'}, '\');
    emp_data  = csvread(emp_xyz);       % first row is meta; fix by copying row 2
    emp_data(1, :) = emp_data(2, :);
    emp_dx = single(emp_data(:, 1)');
    emp_dy = single(emp_data(:, 2)');
    emp_dz = single(emp_data(:, 3)');
    rmdir(dest_dir, 's');
end

function [actpal_dx, actpal_dy, actpal_dz] = read_actpal_data(subj)
%READ_ACTPAL_DATA Read ActivPAL accelerometer CSV and return axes as row vectors.
    global root_dir
    actpal_path = strjoin({root_dir, subj, '4.Activpal'}, '\');
    listing = dir(actpal_path);
    target  = '';
    for k = 1:numel(listing)
        if endsWith(listing(k).name, '-Accelerometer.csv')
            target = listing(k).name; break;
        end
    end
    if isempty(target), error('ActivPAL accelerometer file not found for %s', subj); end
    actpal_xyz = strjoin({actpal_path, target}, '\');
    M = readmatrix(actpal_xyz);
    actpal_dx = single(M(:, 3)');
    actpal_dy = single(M(:, 4)');
    actpal_dz = single(M(:, 5)');
end

function zmax_plot(zmax_dx, zmax_dy, zmax_dz, start_sec, end_sec, dur, sub_id)
%ZMAX_PLOT Plot Zmax axes with truncation line and title.
    global sm_zmax
    zt = single(1/sm_zmax : 1/sm_zmax : length(zmax_dx)/sm_zmax);
    p = plot(zt, zmax_dx, 'Color', 'b', 'LineWidth', 1);
    hold on
    plot(zt, zmax_dy, 'Color', "#018749", 'LineWidth', 1);
    plot(zt, zmax_dz, 'Color', 'm', 'LineWidth', 1);
    ylim([-2 2.2])
    line([start_sec end_sec], [2 2], 'Color', 'r', 'LineWidth', 1.5, 'LineStyle', '-');
    ax = ancestor(p, 'axes'); ax.XAxis.Exponent = 0;
    grid on
    title(sprintf('%s\nZmax Acc., Duration = %d sec', sub_id, dur))
    hold off
end

function emp_plot(emp_dx, emp_dy, emp_dz)
%EMP_PLOT Plot Empatica axes.
    global sm_emp
    tt = single(1/sm_emp : 1/sm_emp : length(emp_dx)/sm_emp);
    p = plot(tt, emp_dx, 'Color', 'b', 'LineWidth', 1);
    hold on
    plot(tt, emp_dy, 'Color', "#018749", 'LineWidth', 1);
    plot(tt, emp_dz, 'Color', 'm', 'LineWidth', 1);
    ax = ancestor(p, 'axes'); ax.XAxis.Exponent = 0;
    grid on
    title('Emp Acc.')
    hold off
    zoom xon
end

function actpal_plot(actpal_dx, actpal_dy, actpal_dz)
%ACTPAL_PLOT Plot ActivPAL axes.
    global sm_actpal
    tt = single(1/sm_actpal : 1/sm_actpal : length(actpal_dx)/sm_actpal);
    p = plot(tt, actpal_dx, 'Color', 'b', 'LineWidth', 1);
    hold on
    plot(tt, actpal_dy, 'Color', "#018749", 'LineWidth', 1);
    plot(tt, actpal_dz, 'Color', 'm', 'LineWidth', 1);
    ax = ancestor(p, 'axes'); ax.XAxis.Exponent = 0;
    grid on
    ylim([-3 3])
    title('ActivPAL Acc.')
    hold off
    zoom xon
end

function file_list = search_files(current_dir, target_file, file_list)
%SEARCH_FILES Recursively gather paths to files named target_file.
    entries = dir(current_dir);
    for k = 1:length(entries)
        name = entries(k).name;
        if strcmp(name, '.') || strcmp(name, '..'), continue; end
        full_path = fullfile(current_dir, name);
        if entries(k).isdir
            file_list = search_files(full_path, target_file, file_list);
        else
            if strcmp(name, target_file)
                file_list{end+1} = full_path; %#ok<AGROW>
            end
        end
    end
end

function txt = myupdatefcn(~, event_obj)
%MYUPDATEFCN Datacursor callback: copies rounded X to clipboard and shows X.
    pos = get(event_obj, 'Position');
    x_value = pos(1);
    rounded_x_value = round(x_value);
    clipboard('copy', rounded_x_value);
    txt = {['X: ', sprintf('%.1f', x_value)], 'X copied'};
end
