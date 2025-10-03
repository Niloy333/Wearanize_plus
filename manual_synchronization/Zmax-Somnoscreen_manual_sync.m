% https://github.com/Niloy333/Wearanize_plus
% Created by Niloy Sikder (scholar.google.com/citations?user=0ALk5j4AAAAJ&hl=en)
% Affiliations: PhD Candidate, Radboud University Medical Center, Donders Institute for Brain, Cognition and Behaviour, Nijmegen, The Netherlands &
% Scientific Assistant, Faculty of Technology and Bionics, Rhine-Waal University of Applied Sciences, Kleve, Germany.
% Contact: niloy.sikder@donders.ru.nl, niloy.sikder@hochschule-rhein-waal.de.
% Project Supervision: Matthias Krauledat, Paul Zerr, and Martin Dresler.
% Copyright (c) 2025 Niloy Sikder

% Description:
%   Plot Zmax accelerometry magnitude and Somnoscreen movement for a subject so that they can be manually synchronized
%   with consistent axes and time labels; includes a data cursor callback.
%   Requirement: MATLAB R2023b+

clc
close all
clearvars

%% Configuration and globals
global root_dir sm_zmax sm_somno_movement
root_dir = 'C:\3028005.01_Local\Wearanize+_dataset_v1.0\1.Raw_data';
sm_zmax = 256;
sm_somno_movement = 128;

%% Inputs
sub_list = readtable("C:\Sciebo_files\_24. Wrnzp_data_paper\common_zmax_psg_start_times.csv");
zmax_sync_info = readtable("C:\Sciebo_files\_24. Wrnzp_data_paper\Manual sync zmax psg emp actpal.xlsx");
zmax_sync_info.SubjectID = strrep(zmax_sync_info.SubjectID, '''', '');

%% Loop subjects (kept as a single subject: index 16)
for i = 16:1:16
    subj = strjoin([root_dir, string(sub_list.sub_id(i))], '\');
    subjid = string(split(subj, '\')); %#ok<NASGU>
    subjid = subjid(end);

    % Zmax truncation info from table
    row = find(strcmp(zmax_sync_info.SubjectID, string(sub_list.sub_id(i))));
    zmax_start = zmax_sync_info.Zmax_start_sec(row);
    zmax_end   = zmax_sync_info.Zmax_end_sec(row);

    % Zmax load and preprocess
    [zmax_dx, zmax_dy, zmax_dz] = zmax_data_read(subj);
    zmax_acc_norm = sqrt(sum([zmax_dx; zmax_dy; zmax_dz].^2, 1));
    zmax_acc_norm(zmax_acc_norm < 1) = 2 - zmax_acc_norm(zmax_acc_norm < 1); % rectify around 1 g
    zmax_acc_norm = zmax_acc_norm - 1;                                       % center
    zmax_time = single(1/sm_zmax : 1/sm_zmax : length(zmax_acc_norm)/sm_zmax);

    % Somno movement
    somno_mov  = read_somno_mov(subj);
    somno_mov2 = somno_mov / 1000;
    somno_time = single(1/sm_somno_movement : 1/sm_somno_movement : length(somno_mov)/sm_somno_movement);

    % Shared x-limit (seconds)
    xxlim = max([zmax_time(end), somno_time(end)]);

    % Figure
    figure('Units', 'normalized', 'OuterPosition', [0 0 1 1]);
    tiledlayout(2, 1, 'TileSpacing', 'compact', 'Padding', 'compact');

    % Zmax plot
    nexttile;
    p1 = plot(zmax_time, zmax_acc_norm, 'LineWidth', 1.1);
    ylim([-.1 2]);
    xlim([0 xxlim]);
    hold on;
    line([zmax_start zmax_end], [1.8 1.8], 'Color', 'r', 'LineWidth', 1.5, 'LineStyle', '-');
    ax1 = ancestor(p1, 'axes');
    ax1.XAxis.Exponent = 0;
    ax1.FontName = 'Times New Roman';
    ax1.FontSize = 12;
    grid on;
    xlabel('Elapsed Time (hh:mm)', 'FontName', 'Times New Roman', 'FontSize', 12);
    ylabel('Acceleration (g)', 'FontName', 'Times New Roman', 'FontSize', 12);
    text(-1500, 0, '(a)', 'FontSize', 14, 'FontWeight', 'bold', 'FontName', 'Times New Roman');
    title(sprintf('Zmax (duration = %d s)', zmax_time(1, end)), 'FontName', 'Times New Roman', 'FontSize', 13);
    xticks1 = 0:3600:xxlim; % 1-hour intervals
    ax1.XTick = xticks1;
    ax1.XTickLabel = datestr(datetime(0,'ConvertFrom','posixtime') + seconds(xticks1), 'HH:MM');
    hold off;

    % Somnoscreen plot
    nexttile;
    p2 = plot(somno_time, somno_mov2, 'LineWidth', 1.1);
    xlim([0 xxlim]);
    ylim([-.1 2]);
    hold on;
    line([67 34356], [1.700 1.700], 'Color', 'r', 'LineWidth', 1.5, 'LineStyle', '-');
    ax2 = ancestor(p2, 'axes');
    ax2.XAxis.Exponent = 0;
    ax2.FontName = 'Times New Roman';
    ax2.FontSize = 12;
    xlabel('Elapsed Time (hh:mm)', 'FontName', 'Times New Roman', 'FontSize', 12);
    ylabel('Acceleration (g)', 'FontName', 'Times New Roman', 'FontSize', 12);
    text(-1500, 0, '(b)', 'FontSize', 14, 'FontWeight', 'bold', 'FontName', 'Times New Roman');
    title(sprintf('Somnoscreen (duration = %d s)', somno_time(1, end)), 'FontName', 'Times New Roman', 'FontSize', 13);
    grid on;
    xticks2 = 0:3600:xxlim; % 1-hour intervals
    ax2.XTick = xticks2;
    ax2.XTickLabel = datestr(datetime(0,'ConvertFrom','posixtime') + seconds(xticks2), 'HH:MM');
    hold off;

    % Data cursor that copies rounded X to clipboard
    dcm = datacursormode;
    datacursormode on;
    set(dcm, 'UpdateFcn', @myupdatefcn);
end

%% Local functions (kept minimal and used)

function [zmax_dx, zmax_dy, zmax_dz] = zmax_data_read(subj)
%ZMAX_DATA_READ Read Zmax dX/dY/dZ EDFs and return single-precision vectors.
    zmax_files = ['dX.edf'; 'dY.edf'; 'dZ.edf'];
    zmax_path  = strjoin([subj, '2.Zmax'], '\');
    zmax_dx    = zmax_edfread(strjoin([zmax_path, zmax_files(1, :)], '\'));
    zmax_dy    = zmax_edfread(strjoin([zmax_path, zmax_files(2, :)], '\'));
    zmax_dz    = zmax_edfread(strjoin([zmax_path, zmax_files(3, :)], '\'));
end

function flattened = zmax_edfread(zmaxpath)
%ZMAX_EDFREAD Expand 1-second EDF cells to a per-sample vector at sm_zmax Hz.
    global sm_zmax
    zmax_tbl  = edfread(zmaxpath);
    zmax_cell = table2array(zmax_tbl);
    flattened = zeros(1, length(zmax_cell) * sm_zmax, 'single');
    for i = 1:length(zmax_cell)
        flattened((i-1)*sm_zmax + 1 : i*sm_zmax) = zmax_cell{i};
    end
end

function somno_mov = read_somno_mov(subj)
%READ_SOMNO_MOV Read Somno "Move." channel and expand to sm_somno_movement Hz.
    global sm_somno_movement
    somno_channels = {'Move.'};
    somno_path = subj + "\1.Somno";
    somno_edf  = dir(fullfile(somno_path, '*.edf'));
    if length(somno_edf) ~= 1
        error('length(somno_edf) = %d.', length(somno_edf));
    end
    somno_path = somno_path + "\" + string(somno_edf(1).name);
    somno_tbl  = edfread(somno_path, "SelectedSignals", somno_channels);
    somno_cell = table2array(somno_tbl);

    flattened = zeros(1, length(somno_cell) * sm_somno_movement, 'single');
    for k = 1:length(somno_cell)
        flattened((k-1)*sm_somno_movement + 1 : k*sm_somno_movement) = somno_cell{k};
    end
    somno_mov = flattened;
end

function txt = myupdatefcn(~, event_obj)
%MYUPDATEFCN Datacursor callback: copies rounded X to clipboard and shows X.
    pos = get(event_obj, 'Position');
    x_value = pos(1);
    rounded_x_value = round(x_value);
    clipboard('copy', rounded_x_value);
    formatted_x_value = sprintf('%.1f', x_value);
    txt = {['X: ', formatted_x_value], 'X copied'};
end
