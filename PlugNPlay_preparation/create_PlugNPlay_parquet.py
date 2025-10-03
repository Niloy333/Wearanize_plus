
"""
https://github.com/Niloy333/Wearanize_plus
Created by Niloy Sikder (scholar.google.com/citations?user=0ALk5j4AAAAJ&hl=en)
Affiliations: PhD Candidate, Radboud University Medical Center, Donders Institute for Brain, Cognition and Behaviour, Nijmegen, The Netherlands &
Scientific Assistant, Faculty of Technology and Bionics, Rhine-Waal University of Applied Sciences, Kleve, Germany.
Contact: niloy.sikder@donders.ru.nl, niloy.sikder@hochschule-rhein-waal.de.
Project Supervision: Matthias Krauledat, Paul Zerr, and Martin Dresler.
Copyright (c) 2025 Niloy Sikder

Batch-sync and export PSG, Zmax, Empatica, and ActivPAL data to per-subject
gzipped Parquet files, aligning to PSG epochs and attaching sleep scores.
"""
#%% Imports:
import os
import pandas as pd
import pyedflib
import math
import numpy as np
import gc
import pyarrow as pa
import pyarrow.parquet as pq
import zipfile
from datetime import datetime
from colorama import Fore, Style
import time

#%% Paths & settings
raw_data_dir = r"C:\3028005.01_Local\Wearanize+_dataset_v1.0\1.Raw_data"
manual_scores_dir = r"C:\3028005.01_Local\Wearanize+_dataset_v1.0\2.Sleep_scores\1.PSG_manual_scores"
usleep_scores_dir = r"C:\3028005.01_Local\Wearanize+_dataset_v1.0\2.Sleep_scores\2.PSG_autoscores_U-Sleep_v2.0"
dreamento_scores_dir = r"C:\3028005.01_Local\Wearanize+_dataset_v1.0\2.Sleep_scores\3.Zmax_autoscores_Dreamento"
usable_scores_dir = r"C:\3028005.01_Local\Wearanize+_dataset_v1.0\2.Sleep_scores\4.Zmax_autoscores_Dreamento_with_eegUsability"
sync_points = pd.read_excel(
    r"C:\3028005.01_Local\Wearanize+_dataset_v1.0\3.Manual_synchronization\Manual sync zmax psg emp actpal.xlsx")
sync_points["SubjectID"] = sync_points["SubjectID"].str.rstrip("'")
out_dir = r"C:\3028005.01_Local\Wearanize+_dataset_v1.0\parquet"

# %% Subject list and constants
sub_ids = [
    folder for folder in os.listdir(raw_data_dir)
    if os.path.isdir(os.path.join(raw_data_dir, folder))
]
epoch_len = 30
col_order = [
    "SubjectID", "Device", "NumOfSignals", "SignalLabel", "SignalStartDateTime",
    "SamplingRate", "SignalDurationSec", "SignalLength", "SignalMin", "SignalMax",
    "SignalType", "SignalUnit", "SignalData", "SleepScoreEpochs", "SleepScores"
]

# %% Functions
def ignore_device(sync_row):
    """
    Decide whether Empatica/ActivPAL should be ignored based on sentinel values.
    WHY: Avoids processing/validating devices without valid sync intervals.
    """
    ignore_emp = ignore_actpal = False
    if (
        ((sync_row["Emp_start_sec"].iloc[0] == 0) | (sync_row["Emp_start_sec"].iloc[0] == -999))
        & ((sync_row["Emp_end_sec"].iloc[0] == 0) | (sync_row["Emp_end_sec"].iloc[0] == -999))
    ):
        ignore_emp = True

    if (
        ((sync_row["Actpal_start_sec"].iloc[0] == 0) | (sync_row["Actpal_start_sec"].iloc[0] == -999))
        & ((sync_row["Actpal_end_sec"].iloc[0] == 0) | (sync_row["Actpal_end_sec"].iloc[0] == -999))
    ):
        ignore_actpal = True
    return ignore_emp, ignore_actpal


def validate_scores(scores):
    """
    Validate sleep stage labels belong to {-1, 0, 1, 2, 3, 4}.
    WHY: Catch label drift or file parsing issues early.
    """
    allowed_scores = {-1, 0, 1, 2, 3, 4}
    unique_values = set(scores)
    if not unique_values.issubset(allowed_scores):
        os.system('echo \a')
        raise ValueError(f"Invalid values found in zmax_scores: {unique_values - allowed_scores}")
    else:
        return None


def check_manual_sleep_scores_set(scores_dir):
    """
    QA helper to scan all manual score files and count labels.
    NOTE: Preserves original side-effect-only behavior.
    """
    combined_scores = pd.DataFrame()
    for file_name in os.listdir(scores_dir):
        if file_name.endswith(".txt"):
            file_path = os.path.join(scores_dir, file_name)
            scores = pd.read_csv(file_path, delimiter='\t', usecols=[0], header=None)
            combined_scores = pd.concat([combined_scores, scores], ignore_index=True)
    unique_values = set(combined_scores[0].unique())
    value_counts = combined_scores[0].value_counts()
    existing_labels = pd.DataFrame({
        "Label": list(unique_values),
        "Count": [value_counts.get(label, 0) for label in unique_values]
    })

def pseudo_correct_len(sub_row, man_scores):
    """
    Trim/pad manual scores to match expected length difference.
    WHY: Ensures equalized lengths where manual labels drift.
    """
    trim = int(sub_row["difference_length (E-F)"])
    if trim < 0:
        man_scores = man_scores[:trim]
    elif trim > 0:
        last_value = man_scores.iloc[-1]
        filling = pd.Series([last_value] * trim)
        man_scores = pd.concat([man_scores, filling], ignore_index=True)
    else:
        pass
    return man_scores


def check_length_duration(sub_data, device):
    """
    Validate equal SleepScoreEpochs and durations across devices.
    WHY: Fail fast on desync to avoid silent errors downstream.
    """
    first_key = next(iter(sub_data["SignalDurationSec"][device]))
    if sub_data["SleepScoreEpochs"]['Zmax'] != sub_data["SleepScoreEpochs"]['PSG']:
        os.system('echo \a')
        raise ValueError(f"SleepScoreEpochs are not equal: Zmax & {device}")
    if sub_data["SignalDurationSec"]['Zmax']['EEGL'] != sub_data["SignalDurationSec"][device][first_key]:
        os.system('echo \a')
        raise ValueError(f"SignalDurationSec are not equal: Zmax & {device}")


def tic():
    """Start timer."""
    return time.time()


def toc(start_time, m, n, N):
    """
    Print mean per-night processing time and ETA.
    WHY: Operator feedback for long batch runs.
    """
    e_secs = time.time() - start_time
    sec_per_night = e_secs / m
    mins_per_night = int(sec_per_night // 60)
    sec_per_night_2 = int(sec_per_night % 60)
    total_remaining_secs = sec_per_night * (N - n)
    r_days = int(total_remaining_secs // (24 * 3600))
    total_remaining_secs %= (24 * 3600)
    r_hrs = int(total_remaining_secs // 3600)
    total_remaining_secs %= 3600
    r_mins = total_remaining_secs / 60
    print(f"{Fore.GREEN}{Style.BRIGHT}\nMean processing time per night: {mins_per_night} min {sec_per_night_2} sec")
    if r_days > 0:
        print(f"Estimated remaining time: {r_days} days {r_hrs} hrs {r_mins:.0f} mins {Style.RESET_ALL}")
    elif r_hrs > 0:
        print(f"Estimated remaining time: {r_hrs} hrs {r_mins:.0f} mins {Style.RESET_ALL}")
    else:
        print(f"Estimated remaining time: {r_mins:.1f} mins {Style.RESET_ALL}")


def decide_start_end_sec(sync_row, epoch_len, ignore_emp, ignore_actpal):
    """
    Compute aligned start/end seconds and epochs for PSG/Zmax; adjust Empatica/ActivPAL windows.
    WHY: Normalize all streams to PSG epoch grid; preserve durations after offsets.
    """
    zmax_start_sec = int(sync_row["Zmax_start_sec"].iloc[0])
    zmax_end_sec = int(sync_row["Zmax_end_sec"].iloc[0])
    psg_start_sec = int(sync_row["PSG_start_sec"].iloc[0])
    psg_end_sec = int(sync_row["PSG_end_sec"].iloc[0])
    psg_offset = int(sync_row["PSG_offset"].iloc[0])
    emp_start_sec = int(sync_row["Emp_start_sec"].iloc[0])
    emp_end_sec = int(sync_row["Emp_end_sec"].iloc[0])
    actpal_start_sec = int(sync_row["Actpal_start_sec"].iloc[0])
    actpal_end_sec = int(sync_row["Actpal_end_sec"].iloc[0])

    emp_seed_zero_sec = 0
    if emp_start_sec < 0:
        # Seed with zeros to keep lengths when Empatica starts negative vs. PSG anchor.
        emp_seed_zero_sec = 0 - emp_start_sec
        emp_start_sec = 0
        emp_end_sec = emp_end_sec + emp_seed_zero_sec

    # Adjust offset at PSG start (by cropping the other signals).
    if psg_start_sec < 0:
        psg_start_sec = psg_start_sec - 1
        zmax_start_sec = zmax_start_sec - psg_start_sec
        emp_start_sec = emp_start_sec - psg_start_sec
        actpal_start_sec = actpal_start_sec - psg_start_sec
        psg_start_sec = 1

    # Adjust offset at PSG end (by cropping the other signals).
    if psg_offset > 0:
        zmax_end_sec = zmax_end_sec - psg_offset
        psg_end_sec = psg_end_sec - psg_offset
        emp_end_sec = emp_end_sec - psg_offset
        actpal_end_sec = actpal_end_sec - psg_offset

    # Durations must match after coarse alignment.
    zmax_dur_sec = zmax_end_sec - zmax_start_sec
    psg_dur_sec = psg_end_sec - psg_start_sec
    emp_dur_sec = emp_end_sec - emp_start_sec
    actpal_dur_sec = actpal_end_sec - actpal_start_sec

    if ignore_emp is True and ignore_actpal is True:
        if not (zmax_dur_sec == psg_dur_sec):
            os.system('echo \a')
            raise ValueError("All durations are not equal. Point A")
    elif ignore_emp is True and ignore_actpal is False:
        if not (zmax_dur_sec == psg_dur_sec == actpal_dur_sec):
            os.system('echo \a')
            raise ValueError("All durations are not equal. Point A")
    elif ignore_emp is False and ignore_actpal is True:
        if not (zmax_dur_sec == psg_dur_sec == emp_dur_sec):
            os.system('echo \a')
            raise ValueError("All durations are not equal. Point A")
    else:
        if not (zmax_dur_sec == psg_dur_sec == emp_dur_sec == actpal_dur_sec):
            os.system('echo \a')
            raise ValueError("All durations are not equal. Point A")

    # Determine epoch-aligned windows.
    psg_start_epoch = int(math.ceil(psg_start_sec / epoch_len)) + 1
    psg_end_epoch = int(math.floor(psg_end_sec / epoch_len))
    psg_epoch_len = psg_end_epoch - psg_start_epoch + 1

    zmax_start_epoch = int(math.floor(zmax_start_sec / epoch_len)) + 1
    zmax_end_epoch = zmax_start_epoch + psg_epoch_len - 1
    zmax_epoch_len = zmax_end_epoch - zmax_start_epoch + 1  # noqa: F841 (kept for parity)

    # Convert back to exact seconds for aligned epochs.
    psg_start_sec2 = (psg_start_epoch - 1) * epoch_len + 1
    psg_end_sec2 = psg_end_epoch * epoch_len
    zmax_start_sec2 = (zmax_start_epoch - 1) * epoch_len + 1
    zmax_end_sec2 = zmax_end_epoch * epoch_len
    zmax_start_offset = zmax_start_sec - zmax_start_sec2
    zmax_end_offset = zmax_end_sec - zmax_end_sec2

    emp_start_sec = emp_start_sec - zmax_start_offset
    emp_end_sec = emp_end_sec - zmax_end_offset
    actpal_start_sec = actpal_start_sec - zmax_start_offset
    actpal_end_sec = actpal_end_sec - zmax_end_offset

    # Re-check durations post fine alignment.
    zmax_dur_sec = zmax_end_sec2 - zmax_start_sec2
    psg_dur_sec = psg_end_sec2 - psg_start_sec2
    emp_dur_sec = emp_end_sec - emp_start_sec
    actpal_dur_sec = actpal_end_sec - actpal_start_sec

    if ignore_emp is True and ignore_actpal is True:
        if not (zmax_dur_sec == psg_dur_sec):
            os.system('echo \a')
            raise ValueError("All durations are not equal. Point B")
    elif ignore_emp is True and ignore_actpal is False:
        if not (zmax_dur_sec == psg_dur_sec == actpal_dur_sec):
            os.system('echo \a')
            raise ValueError("All durations are not equal. Point B")
    elif ignore_emp is False and ignore_actpal is True:
        if not (zmax_dur_sec == psg_dur_sec == emp_dur_sec):
            os.system('echo \a')
            raise ValueError("All durations are not equal. Point B")
    else:
        if not (zmax_dur_sec == psg_dur_sec == emp_dur_sec == actpal_dur_sec):
            os.system('echo \a')
            raise ValueError("All durations are not equal. Point B")

    return (
        zmax_start_sec2, zmax_end_sec2, zmax_start_epoch, zmax_end_epoch,
        psg_start_sec2, psg_end_sec2, psg_start_epoch, psg_end_epoch,
        emp_start_sec, emp_end_sec, emp_seed_zero_sec, actpal_start_sec, actpal_end_sec
    )


def create_zmax_data(sub_id, zmax_start_sec, zmax_end_sec, zmax_start_epoch, zmax_end_epoch,
                     epoch_len, raw_data_dir, dreamento_scores_dir, usable_scores_dir):
    """
    Load Zmax EDFs, trim to aligned seconds, and attach Dreamento(+usability) scores.
    WHY: Provides Zmax reference stream aligned to PSG epochs.
    """
    if os.path.exists(os.path.join(raw_data_dir, sub_id, '2.Zmax', 'EEG L.edf')):
        file_list = ["EEG L.edf", "EEG R.edf", "dX.edf", "dY.edf", "dZ.edf", "NOISE.edf", "OXY_IR_AC.edf", "OXY_IR_DC.edf"]
        labels = ["EEGL", "EEGR", "ACCX", "ACCY", "ACCZ", "NOISE", "OXY_IR_AC", "OXY_IR_DC"]

        SignalLabel = []
        SamplingRate = {}
        SignalLength = {}
        SignalDurationSec = {}
        SignalStartDateTime = {}
        SignalMin = {}
        SignalMax = {}
        SignalType = {}
        SignalUnit = {}
        SignalData = {}
        SleepScores = {}

        for l, file in enumerate(file_list):
            signal = label = samp_rate = None
            file_path = os.path.join(raw_data_dir, sub_id, '2.Zmax', file)
            try:
                signal_edf = pyedflib.EdfReader(file_path)
                if signal_edf.signals_in_file != 1:
                    os.system('echo \a')
                    raise ValueError(f"Found 1+ signals in file: {file_path}")

                signal = signal_edf.readSignal(0)
                samp_rate = int(signal_edf.getSampleFrequencies()[0])
                signal = np.array(signal, dtype='float32')
                if signal is None:
                    os.system('echo \a')
                    raise ValueError(f"File not readable: {file_path}")
                label = labels[l]
            finally:
                signal_edf.close()
                del signal_edf
                gc.collect()

            start_point = int((zmax_start_sec - 1) * samp_rate)
            end_point = int(zmax_end_sec * samp_rate)
            signal = signal[start_point: end_point]

            SignalLabel.append(label)
            SamplingRate[label] = samp_rate
            SignalLength[label] = len(signal)
            SignalDurationSec[label] = len(signal) / samp_rate
            SignalStartDateTime[label] = "Unreliable"
            SignalMin[label] = np.min(signal)
            SignalMax[label] = np.max(signal)
            SignalData[label] = signal

            # Type/Unit mapping
            if label in ["EEGL", "EEGR"]:
                SignalType[label] = "EEG"
                SignalUnit[label] = "uV"
            elif label in ["ACCX", "ACCY", "ACCZ"]:
                SignalType[label] = "ACC"
                SignalUnit[label] = "g"
            elif label in ["OXY_IR_AC", "OXY_IR_DC"]:
                SignalType[label] = "PPG"
                SignalUnit[label] = "Unitless"
            else:
                SignalType[label] = "Noise"
                SignalUnit[label] = "Unitless"

        # Insert usable scores
        file_path = os.path.join(usable_scores_dir, f"{sub_id}.txt")
        zmax_scores = pd.read_csv(file_path, delimiter='\t', skiprows=11, header=None)
        zmax_scores = np.squeeze(zmax_scores)
        zmax_scores = zmax_scores.fillna(-1)
        validate_scores(zmax_scores)
        zmax_scores = zmax_scores[(zmax_start_epoch - 1): zmax_end_epoch]
        zmax_scores = np.array(zmax_scores, dtype='int8')
        SleepScores['Dreamento + eegUsability'] = zmax_scores

        # Insert Dreamento scores
        file_path = os.path.join(dreamento_scores_dir, f"{sub_id}.txt")
        dre_scores = pd.read_csv(file_path, delimiter='\t', skiprows=5, header=None)
        dre_scores = np.squeeze(dre_scores)
        dre_scores = dre_scores.fillna(-1)
        validate_scores(dre_scores)
        dre_scores = dre_scores[(zmax_start_epoch - 1): zmax_end_epoch]
        dre_scores = np.array(dre_scores, dtype='int8')
        SleepScores['Dreamento'] = dre_scores

        zmax_df = pd.DataFrame([[
            SignalLabel, SamplingRate, SignalLength, SignalDurationSec, SignalStartDateTime,
            SignalMin, SignalMax, SignalType, SignalUnit, SignalData, SleepScores
        ]], columns=[
            'SignalLabel', 'SamplingRate', 'SignalLength', 'SignalDurationSec', 'SignalStartDateTime',
            'SignalMin', 'SignalMax', 'SignalType', 'SignalUnit', 'SignalData', 'SleepScores'
        ])

        zmax_df['SubjectID'] = sub_id
        zmax_df['Device'] = 'Zmax Lite'
        zmax_df['SleepScoreEpochs'] = len(zmax_scores)
        zmax_df['NumOfSignals'] = len(SignalLabel)
        return zmax_df
    else:
        return None


def create_psg_data(sub_id, psg_start_sec, psg_end_sec, psg_start_epoch, psg_end_epoch,
                    epoch_len, raw_data_dir, manual_scores_dir, usleep_scores_dir):
    """
    Load PSG (Somno or Mentalab), trim to aligned seconds, and attach Manual/Usleep scores.
    WHY: PSG is the anchor stream; others align to it.
    """
    SignalLabel = []
    SamplingRate = {}
    SignalLength = {}
    SignalDurationSec = {}
    SignalStartDateTime = {}
    SignalMin = {}
    SignalMax = {}
    SignalType = {}
    SignalUnit = {}
    SignalData = {}
    SleepScores = {}

    if os.path.exists(os.path.join(raw_data_dir, sub_id, '1.Somno')):
        dev = 'SomnoScreen Plus'
        file_path = os.path.join(raw_data_dir, sub_id, '1.Somno')
        edf_files = [f for f in os.listdir(file_path) if f.lower().endswith('.edf')]
        if len(edf_files) != 1:
            os.system('echo \a')
            raise ValueError(f"Expected one EDF file in {file_path}, found {len(edf_files)}.")

        edf_file_path = os.path.join(file_path, edf_files[0])
        psg_edf = pyedflib.EdfReader(edf_file_path)
        try:
            for i in range(psg_edf.signals_in_file):
                signal_data = label = samp_rate = None
                label = psg_edf.getSignalLabels()[i]
                if label != 'Battery':
                    signal_data = psg_edf.readSignal(i)
                    signal_data = np.array(signal_data, dtype='float32')
                    samp_rate = int(psg_edf.getSampleFrequencies()[i])

                    start_point = int((psg_start_sec - 1) * samp_rate)
                    end_point = int(psg_end_sec * samp_rate)
                    signal_data = signal_data[start_point:end_point]

                    SignalLabel.append(label)
                    SamplingRate[label] = samp_rate
                    SignalLength[label] = len(signal_data)
                    SignalDurationSec[label] = len(signal_data) / samp_rate
                    SignalStartDateTime[label] = str(psg_edf.getStartdatetime())
                    SignalMin[label] = np.min(signal_data)
                    SignalMax[label] = np.max(signal_data)
                    SignalData[label] = signal_data
                    SignalUnit[label] = psg_edf.getPhysicalDimension(i)

                    if 'EOG' in label:
                        SignalType[label] = "EOG"
                    elif 'EMG' in label:
                        SignalType[label] = "EMG"
                    elif 'ECG' in label:
                        SignalType[label] = "ECG"
                    elif label == 'Pos.':
                        SignalType[label] = "Body Position"
                    elif label == 'Move.':
                        SignalType[label] = "ACC (aggregated)"
                    else:
                        SignalType[label] = "EEG"
        finally:
            psg_edf.close()
            del psg_edf, signal_data
            gc.collect()

    elif os.path.exists(os.path.join(raw_data_dir, sub_id, '1.Mentalab')):
        dev = 'Mentalab Explore Pro'
        exg_sig_order = [
            'EOG1', 'F8', 'FT10', 'EOG2', 'FC6', 'T8', 'C4', 'CP6', 'P8', 'P4',
            'EMG1', 'EMG2', 'FC1', 'FCz', 'FC2', 'Cz', 'CP1', 'CP2', 'Pz', 'O1', 'Oz', 'O2',
            'ECG1', 'F7', 'FT9', 'ECG2', 'FC5', 'T7', 'C3', 'CP5', 'P7', 'P3'
        ]
        act_sig_order = ["ACCX", "ACCY", "ACCZ", "GYRX", "GYRY", "GYRZ", "MAGX", "MAGY", "MAGZ"]
        act_sig_units = ['mg'] * 3 + ['mdps'] * 3 + ['uT'] * 3

        file_path = os.path.join(raw_data_dir, sub_id, '1.Mentalab')
        csv_files = [f for f in os.listdir(file_path) if f.lower().endswith('.csv')]
        if len(csv_files) != 2:
            os.system('echo \a')
            raise ValueError(f"Expected two CSV files in {file_path}, found {len(csv_files)}")

        for fl in csv_files:
            signals = pd.read_csv(os.path.join(raw_data_dir, sub_id, '1.Mentalab', fl))
            signals = signals.drop(columns=['TimeStamp'])
            signals = signals.astype(np.float32)

            for i in range(signals.shape[1]):
                signal_data = label = samp_rate = tp = unit = None
                signal_data = signals.iloc[:, i]
                signal_data = np.array(signal_data, dtype='float32')

                if fl.endswith('ExG.csv'):
                    samp_rate = 250
                    label = exg_sig_order[i]
                    if label in ['EOG1', 'EOG2', 'EMG1', 'EMG2', 'ECG1', 'ECG2']:
                        tp = label[:-1]
                    else:
                        tp = 'EEG'
                    unit = 'uV'
                elif fl.endswith('ORN.csv'):
                    samp_rate = 20
                    label = act_sig_order[i]
                    unit = act_sig_units[i]
                    if unit == 'mg':
                        tp = "Accelerometer"
                    elif unit == 'mdps':
                        tp = 'Gyroscope'
                    elif unit == 'uT':
                        tp = 'Magnetometer'
                    else:
                        raise ValueError("Mentalab point1.")
                else:
                    raise ValueError("differetnt filename Mentalab point2.")

                start_point = int((psg_start_sec - 1) * samp_rate)
                end_point = int(psg_end_sec * samp_rate)
                signal_data = signal_data[start_point:end_point]

                SignalLabel.append(label)
                SamplingRate[label] = samp_rate
                SignalLength[label] = len(signal_data)
                SignalDurationSec[label] = len(signal_data) / samp_rate
                SignalStartDateTime[label] = "Unreliable"
                SignalMin[label] = np.min(signal_data)
                SignalMax[label] = np.max(signal_data)
                SignalData[label] = signal_data
                SignalUnit[label] = unit
                SignalType[label] = tp

            del signals, signal_data
            gc.collect()

    else:
        return None

    # Insert Manual scores
    file_path = os.path.join(manual_scores_dir, f"{sub_id}.txt")
    if os.path.exists(file_path):
        man_scores = pd.read_csv(file_path, delimiter='\t', usecols=[0], skiprows=1, header=None)
        man_scores = np.squeeze(man_scores)
        # man_scores = pseudo_correct_len(sub_row, man_scores)  # Intentional no-op (original)
        man_scores = man_scores.fillna(-1)
        validate_scores(man_scores)
        man_scores = man_scores[(psg_start_epoch - 1): psg_end_epoch]
        man_scores = np.array(man_scores, dtype='int8')
        SleepScores['Manual'] = man_scores

    # Insert U-Sleep scores
    file_path = os.path.join(usleep_scores_dir, f"{sub_id}.csv")
    if os.path.exists(file_path):
        usl_scores = pd.read_csv(file_path, delimiter=',', usecols=[0], skiprows=1, header=None)
        usl_scores = np.squeeze(usl_scores)
        usl_scores = usl_scores.fillna(-1)
        validate_scores(usl_scores)
        usl_scores = usl_scores[(psg_start_epoch - 1): psg_end_epoch]
        usl_scores = np.array(usl_scores, dtype='int8')
        SleepScores['Usleep'] = usl_scores

    psg_df = pd.DataFrame([[
        SignalLabel, SamplingRate, SignalLength, SignalDurationSec, SignalStartDateTime,
        SignalMin, SignalMax, SignalType, SignalUnit, SignalData, SleepScores
    ]], columns=[
        'SignalLabel', 'SamplingRate', 'SignalLength', 'SignalDurationSec', 'SignalStartDateTime',
        'SignalMin', 'SignalMax', 'SignalType', 'SignalUnit', 'SignalData', 'SleepScores'
    ])

    psg_df['SubjectID'] = sub_id
    psg_df['Device'] = dev
    psg_df['NumOfSignals'] = len(SignalLabel)

    if len(SleepScores) > 0:
        if 'Manual' in SleepScores:
            psg_df['SleepScoreEpochs'] = len(man_scores)
        else:
            psg_df['SleepScoreEpochs'] = len(usl_scores)

    return psg_df


def create_emp_data(sub_id, emp_start_sec, emp_end_sec, emp_seed_zero_sec, raw_data_dir):
    """
    Load Empatica ZIP, trim to aligned seconds, left-pad zeros if required by negative start.
    WHY: Preserve duration matching after sync normalization.
    """
    SignalLabel = []
    SamplingRate = {}
    SignalLength = {}
    SignalDurationSec = {}
    SignalStartDateTime = {}
    SignalMin = {}
    SignalMax = {}
    SignalType = {}
    SignalUnit = {}
    SignalData = {}

    file_list = ['ACC', 'EDA', 'BVP', 'TEMP', 'HR']
    acc_sigs = ['X', 'Y', 'Z']
    units = ["g/16", "g/16", "g/16", "MicroSiemens", "Unitless", "degC", "bpm"]

    if emp_seed_zero_sec != 0:
        # Bring negative start to zero and keep final duration by reducing the end.
        emp_end_sec = emp_end_sec - emp_seed_zero_sec
        emp_seed_zero_sec = emp_seed_zero_sec - emp_start_sec
        emp_start_sec = 1

    zip_path = os.path.join(raw_data_dir, sub_id, '3.Empatica')
    zip_files = [f for f in os.listdir(zip_path) if f.lower().endswith('.zip')]

    if len(zip_files) == 0:
        return None
    elif len(zip_files) > 1:
        os.system('echo \a')
        raise ValueError(f"Expected one ZIP file in {zip_path}, found {len(zip_files)}.")
    else:
        zip_path = os.path.join(zip_path, zip_files[0])
        ctr = 0
        with zipfile.ZipFile(zip_path, 'r') as z:
            for file_name in file_list:
                with z.open(file_name + '.csv') as f:
                    signals = pd.read_csv(f)
                    for i in range(signals.shape[1]):
                        if file_name == 'ACC':
                            label = file_name + acc_sigs[i]
                        else:
                            label = file_name

                        signal = samp_rate = None
                        signal = signals.iloc[:, i]
                        samp_rate = int(signal[0])

                        # Extract start datetime from header index (stringified epoch)
                        timestamp_str = signal.name.strip()
                        timestamp_str = timestamp_str.split('.')[0] + '.' + timestamp_str.split('.')[1]
                        timestamp = float(timestamp_str)
                        start_date_time = datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

                        signal = signal.iloc[1:].to_numpy(dtype=np.float32)

                        start_point = int((emp_start_sec - 1) * samp_rate)
                        end_point = int(emp_end_sec * samp_rate)
                        signal = signal[start_point: end_point]

                        if emp_seed_zero_sec != 0:
                            filler = np.zeros((emp_seed_zero_sec + 1) * samp_rate, dtype=np.float32)
                            signal = np.concatenate((filler, signal))

                        if len(signal) < end_point - start_point:
                            signal = np.pad(
                                signal,
                                (0, end_point - start_point - signal.shape[0]),
                                mode='constant',
                                constant_values=0
                            ).astype(np.float32)

                        SignalLabel.append(label)
                        SamplingRate[label] = samp_rate
                        SignalLength[label] = len(signal)
                        SignalDurationSec[label] = len(signal) / samp_rate
                        SignalMin[label] = np.min(signal)
                        SignalMax[label] = np.max(signal)
                        SignalData[label] = signal
                        SignalType[label] = file_name
                        SignalUnit[label] = units[ctr]
                        SignalStartDateTime[label] = start_date_time
                        ctr = ctr + 1

        emp_df = pd.DataFrame([[
            SignalLabel, SamplingRate, SignalLength, SignalDurationSec, SignalStartDateTime,
            SignalMin, SignalMax, SignalType, SignalUnit, SignalData
        ]], columns=[
            'SignalLabel', 'SamplingRate', 'SignalLength', 'SignalDurationSec', 'SignalStartDateTime',
            'SignalMin', 'SignalMax', 'SignalType', 'SignalUnit', 'SignalData'
        ])

        emp_df['SubjectID'] = sub_id
        emp_df['Device'] = 'Empatica E4'
        emp_df['NumOfSignals'] = len(SignalLabel)

        return emp_df


def create_actpal_data(sub_id, actpal_start_sec, actpal_end_sec, raw_data_dir):
    """
    Load ActivPAL CSV, trim to aligned seconds (ACC X/Y/Z).
    WHY: Provides activity reference aligned to PSG/Zmax windows.
    """
    SignalLabel = []
    SamplingRate = {}
    SignalLength = {}
    SignalDurationSec = {}
    SignalStartDateTime = {}
    SignalMin = {}
    SignalMax = {}
    SignalType = {}
    SignalUnit = {}
    SignalData = {}

    csv_path = os.path.join(raw_data_dir, sub_id, '4.Activpal')
    csv_files = [f for f in os.listdir(csv_path) if f.lower().endswith('.csv')]

    if len(csv_files) == 0:
        return None
    elif len(csv_files) > 1:
        os.system('echo \a')
        raise ValueError(f"Expected one CSV file in {csv_path}, found {len(csv_files)}.")
    else:
        csv_path = os.path.join(csv_path, csv_files[0])

        dtype_mapping = {"Time": float, "Uncompres": int, "X": float, "Y": float, "Z": float}
        acc_sigs = ['X', 'Y', 'Z']

        signals = pd.read_csv(csv_path, delimiter=';', dtype=dtype_mapping, skiprows=1)
        signals = signals.drop(columns=['Uncompressed sample index'])

        for s in acc_sigs:
            signal = signals[s].to_numpy(dtype=np.float32)
            timestamp = signals["Time"][0]
            start_date_time = datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
            samp_rate = 20

            start_point = int((actpal_start_sec - 1) * samp_rate)
            end_point = int(actpal_end_sec * samp_rate)
            signal = signal[start_point: end_point]
            label = 'ACC' + s

            SignalLabel.append(label)
            SamplingRate[label] = samp_rate
            SignalLength[label] = len(signal)
            SignalDurationSec[label] = len(signal) / samp_rate
            SignalMin[label] = np.min(signal)
            SignalMax[label] = np.max(signal)
            SignalData[label] = signal
            SignalType[label] = "ACC"
            SignalUnit[label] = 'g'
            SignalStartDateTime[label] = start_date_time

        act_df = pd.DataFrame([[
            SignalLabel, SamplingRate, SignalLength, SignalDurationSec, SignalStartDateTime,
            SignalMin, SignalMax, SignalType, SignalUnit, SignalData
        ]], columns=[
            'SignalLabel', 'SamplingRate', 'SignalLength', 'SignalDurationSec', 'SignalStartDateTime',
            'SignalMin', 'SignalMax', 'SignalType', 'SignalUnit', 'SignalData'
        ])

        act_df['SubjectID'] = sub_id
        act_df['Device'] = 'ActivPAL'
        act_df['NumOfSignals'] = len(SignalLabel)

        return act_df


# %% main()
start_time = tic()
m = 0
n = 0
for sub_id in sub_ids:
    # sub_id = sub_ids[4]
    sync_info_exists = manual_score_exists = None
    sync_index = np.array(sync_points[sync_points['SubjectID'] == sub_id].index)
    n = n + 1

    if sync_index.shape[0] == 1:
        sync_info_exists = True
    if os.path.exists(os.path.join(manual_scores_dir, sub_id + '.txt')):
        manual_score_exists = True

    if sync_info_exists is True and manual_score_exists is True:
        sync_row = sync_points.iloc[sync_index]
        out_file_dir = os.path.join(out_dir, f"{sub_id}.parquet")

        # if os.path.exists(out_file_dir) is True: continue

        print(f"\nProcessing subject: {sub_id}")

        zmax_start_sec = zmax_end_sec = zmax_start_epoch = zmax_end_epoch = None
        psg_start_sec = psg_end_sec = psg_start_epoch = psg_end_epoch = None
        emp_start_sec = emp_end_sec = emp_seed_zero_sec = None
        actpal_start_sec = actpal_end_sec = None
        sub_data = psg_data = emp_data = actpal_data = None

        ignore_emp, ignore_actpal = ignore_device(sync_row)

        (
            zmax_start_sec, zmax_end_sec, zmax_start_epoch, zmax_end_epoch,
            psg_start_sec, psg_end_sec, psg_start_epoch, psg_end_epoch,
            emp_start_sec, emp_end_sec, emp_seed_zero_sec, actpal_start_sec, actpal_end_sec
        ) = decide_start_end_sec(sync_row, epoch_len, ignore_emp, ignore_actpal)

        sub_data = pd.DataFrame(columns=col_order)

        print("\tProcessing Zmax...")
        zmax_data = create_zmax_data(
            sub_id, zmax_start_sec, zmax_end_sec, zmax_start_epoch, zmax_end_epoch,
            epoch_len, raw_data_dir, dreamento_scores_dir, usable_scores_dir
        )
        if zmax_data is not None:
            zmax_data.index = ['Zmax']
            sub_data = pd.concat([sub_data, zmax_data])
        del zmax_data

        print("\tProcessing PSG...")
        psg_data = create_psg_data(
            sub_id, psg_start_sec, psg_end_sec, psg_start_epoch, psg_end_epoch,
            epoch_len, raw_data_dir, manual_scores_dir, usleep_scores_dir
        )
        if psg_data is not None:
            psg_data.index = ['PSG']
            sub_data = pd.concat([sub_data, psg_data])
        del psg_data

        check_length_duration(sub_data[["SleepScoreEpochs", "SignalDurationSec"]], 'PSG')

        if sync_row["Emp_end_sec"].iloc[0] != 0 and sync_row["Emp_end_sec"].iloc[0] != -999:
            print("\tProcessing Empatica...")
            emp_data = create_emp_data(sub_id, emp_start_sec, emp_end_sec, emp_seed_zero_sec, raw_data_dir)
            if emp_data is not None:
                emp_data.index = ['Emp']
                sub_data = pd.concat([sub_data, emp_data])
                check_length_duration(sub_data[["SleepScoreEpochs", "SignalDurationSec"]], 'Emp')
            del emp_data

        if sync_row["Actpal_end_sec"].iloc[0] != 0 and sync_row["Actpal_end_sec"].iloc[0] != -999:
            print("\tProcessing Activpal...")
            act_data = create_actpal_data(sub_id, actpal_start_sec, actpal_end_sec, raw_data_dir)
            if act_data is not None:
                act_data.index = ['ActivPal']
                sub_data = pd.concat([sub_data, act_data])
                check_length_duration(sub_data[["SleepScoreEpochs", "SignalDurationSec"]], 'ActivPal')
            del act_data

        devs = ", ".join(sub_data["Device"].unique())
        print(f"\tSaving file with data from devices:\n\t{devs}...")
        sub_data2 = pa.Table.from_pandas(sub_data)
        pq.write_table(sub_data2, out_file_dir, compression="gzip")
        del sub_data, sub_data2

        m = m + 1
        if n < len(sub_ids):
            toc(start_time, m, n, len(sub_ids))

# %% The Dreamento autoscores is not a part of the release
# del sub_data['SleepScores']['Zmax']["Dreamento"]
# del sub_data['SleepScores']['Zmax']["Dreamento + eegUsability"]
# if not sub_data.at["Zmax", "SleepScores"]:
#     sub_data.at["Zmax", "SleepScoreEpochs"] = np.nan
#     sub_data.at["Zmax", "SleepScores"] = np.nan
