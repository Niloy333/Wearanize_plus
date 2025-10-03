"""
https://github.com/Niloy333/Wearanize_plus
Created by Niloy Sikder (scholar.google.com/citations?user=0ALk5j4AAAAJ&hl=en)
Affiliations: PhD Candidate, Radboud University Medical Center, Donders Institute for Brain, Cognition and Behaviour, Nijmegen, The Netherlands &
Scientific Assistant, Faculty of Technology and Bionics, Rhine-Waal University of Applied Sciences, Kleve, Germany.
Contact: niloy.sikder@donders.ru.nl, niloy.sikder@hochschule-rhein-waal.de.
Project Supervision: Matthias Krauledat, Paul Zerr, and Martin Dresler.
Copyright (c) 2025 Niloy Sikder

Export synchronized signals from per-subject Parquet files into EDF+ files.
"""
# file: scripts/parquet_to_synced_edf.py
"""
Export synchronized signals from per-subject Parquet files into EDF+ files.

WHY:
- Consolidate multi-device signals into a single EDF for plug-and-play usage.
- Preserve original sampling, scaling, labels, and attached sleep scores.

NOTE:
- Core behavior and control flow are unchanged.
- Function signatures remain exactly the same.
"""

# %% Imports
import os
import glob
import json  # kept for parity; not used but present in original
import numpy as np
import pandas as pd
import pyedflib
import pyarrow as pa
import pyarrow.parquet as pq
from datetime import datetime

# %% I/O paths
data_dir = r"C:\3028005.01_Local\Wearanize+_dataset_v1.0\parquet"
out_dir = r"C:\3028005.01_Local\Wearanize+_dataset_v1.0\Wearanize+_PlugNPlay"

pq_files = glob.glob(os.path.join(data_dir, "*.parquet"))


def is_flat(signal):
    """
    Return True if the entire 1D array is constant.
    WHY: Helper retained from original (not used in loop).
    """
    return np.all(signal == signal[0])


# %% main():
for sub_dir in pq_files:
    # sub_dir = pq_files[94]
    sub_data = pd.read_parquet(sub_dir)
    sub_id = sub_data['SubjectID']['PSG']
    print(f"Processing {sub_id}...")

    # Build BIDS-like EDF path 
    sub_id_n = sub_id[:-2]
    sub_id_n = sub_id_n[3:]
    edf_file_path = os.path.join(
        out_dir, f"sub-{sub_id_n}", 'eeg', f"sub-{sub_id_n}_task-sleep_proc-synced_eeg.edf"
    )
    os.makedirs(os.path.dirname(edf_file_path), exist_ok=True)

    # Count channels across all rows; add 1 per sleep-score stream if present
    total_channels = sum(sub_data["NumOfSignals"])
    if "Manual" in sub_data["SleepScores"]['PSG']:
        total_channels = total_channels + 1
    if "Usleep" in sub_data["SleepScores"]['PSG']:
        total_channels = total_channels + 1

    # Special-case override 
    if sub_id == 'Sub115s1':
        total_channels = 46

    # Create EDF writer
    edf_writer = pyedflib.EdfWriter(
        edf_file_path, total_channels, file_type=pyedflib.FILETYPE_EDFPLUS
    )

    # Global EDF metadata
    patient_name = sub_id
    edf_writer.setPatientName(patient_name)
    edf_writer.setRecordingAdditional("Wearanize+_dataset")

    # Collect per-signal headers and sample arrays
    signal_headers = []
    signal_data = []

    # Fixed global start date-time 
    start_datetime = datetime(2000, 1, 1, 0, 0, 0)
    edf_writer.setStartdatetime(start_datetime)

    # Iterate over devices/rows
    for index, row in sub_data.iterrows():
        subject_id = row["SubjectID"]      
        device = row["Device"]             
        signal_labels = row["SignalLabel"]

        for signal_name in signal_labels:
            # Make unique label from row-index + signal name
            if signal_name == "EMG+":
                unique_signal_name = f"{index}_EMG_plus"
            elif signal_name == "EMG-":
                unique_signal_name = f"{index}_EMG_minus"
            else:
                unique_signal_name = f"{index}_{signal_name}"

            # Extract metadata for EDF header
            sampling_rate = row["SamplingRate"].get(signal_name)
            duration_sec = row["SignalDurationSec"].get(signal_name)
            min_val = row["SignalMin"].get(signal_name)
            max_val = row["SignalMax"].get(signal_name)
            signal_type = row["SignalType"].get(signal_name)
            signal_unit = row["SignalUnit"].get(signal_name)

            # Normalize a couple of unit labels to EDF-friendly strings
            if signal_unit == 'MicroSie':
                signal_unit = 'µS'
            elif signal_unit == 'Position':
                signal_unit = 'Unitless'

            # Avoid equal physical min/max (flat signals) which breaks EDF scaling
            if min_val == max_val:
                if sub_id == 'Sub115s1':
                    continue
                else:
                    max_val = min_val + 0.001  # tiny epsilon to keep scale valid

            data = row["SignalData"].get(signal_name)

            # Append EDF signal header
            signal_headers.append({
                'label': unique_signal_name,
                'dimension': signal_unit,
                'sample_rate': sampling_rate,
                'physical_min': min_val,
                'physical_max': max_val,
                'digital_min': -32768,
                'digital_max': 32767,
                'transducer': signal_type,
                'prefilter': '',
                'startdate': start_datetime,
                'duration': duration_sec
            })

            # Append corresponding samples
            signal_data.append(data)

        # Attach sleep scores as additional signals on PSG row
        if index == 'PSG':
            # Manual scores
            if "Manual" in row["SleepScores"]:
                unique_signal_name = "PSG_Manual_scores"
                sampling_rate = 1 / 30
                duration_sec = row["SleepScoreEpochs"]
                min_val = -1
                max_val = 4
                signal_type = "Sleep_scores"
                signal_unit = "Unitless"
                data = row["SleepScores"].get("Manual")

                signal_headers.append({
                    'label': unique_signal_name,
                    'dimension': signal_unit,
                    'sample_rate': sampling_rate,
                    'physical_min': min_val,
                    'physical_max': max_val,
                    'digital_min': -32768,
                    'digital_max': 32767,
                    'transducer': signal_type,
                    'prefilter': '',
                    'startdate': start_datetime,
                    'duration': duration_sec
                })
                signal_data.append(data)

            # U-Sleep scores
            if "Usleep" in row["SleepScores"]:
                unique_signal_name = "PSG_USleep_scores"
                sampling_rate = 1 / 30
                duration_sec = row["SleepScoreEpochs"]
                min_val = -1
                max_val = 4
                signal_type = "Sleep_scores"
                signal_unit = "Unitless"
                data = row["SleepScores"].get("Usleep")

                signal_headers.append({
                    'label': unique_signal_name,
                    'dimension': signal_unit,
                    'sample_rate': sampling_rate,
                    'physical_min': min_val,
                    'physical_max': max_val,
                    'digital_min': -32768,
                    'digital_max': 32767,
                    'transducer': signal_type,
                    'prefilter': '',
                    'startdate': start_datetime,
                    'duration': duration_sec
                })
                signal_data.append(data)

    # Finalize EDF
    edf_writer.setSignalHeaders(signal_headers)
    edf_writer.writeSamples(signal_data)
    edf_writer.close()

    # Explicit cleanup
    del sub_data, edf_writer
