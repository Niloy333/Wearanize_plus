"""
https://github.com/Niloy333/Wearanize_plus
Created by Niloy Sikder (scholar.google.com/citations?user=0ALk5j4AAAAJ&hl=en)
Affiliations: PhD Candidate, Radboud University Medical Center, Donders Institute for Brain, Cognition and Behaviour, Nijmegen, The Netherlands &
Scientific Assistant, Faculty of Technology and Bionics, Rhine-Waal University of Applied Sciences, Kleve, Germany.
Contact: niloy.sikder@donders.ru.nl, niloy.sikder@hochschule-rhein-waal.de.
Project Supervision: Matthias Krauledat, Paul Zerr, and Martin Dresler.
Copyright (c) 2026 Niloy Sikder
"""

#%% Imports
import os
import re
import glob
import numpy as np
import pandas as pd
import pyedflib

#%% Paths
edf_dir = r"D:\wnzp_oa\Wearanize+_PlugNPlay_v1.0\Wearanize+_PlugNPlay_v1.0"
parquet_dir = r"C:\Users\BlueWin\Downloads\Wearanize+_PlugNPlay_Parquet_v1.1"
dest_dir = r"C:\Users\BlueWin\Downloads\Wearanize+_PlugNPlay_v1.1"

#%% Find source EDF files (only the top-level sub-*/eeg files, not the derivatives folder)
edf_files = glob.glob(os.path.join(edf_dir, "sub-*", "eeg", "*_task-sleep_eeg.edf"))

#%% Build a lookup from numeric subject ID to parquet file path
def extract_num_id(name):
    match = re.search(r"\d+", name)
    return match.group().zfill(3) if match else None

pq_files = glob.glob(os.path.join(parquet_dir, "*.parquet"))
pq_lookup = {extract_num_id(os.path.basename(f)): f for f in pq_files}

#%% Helper to convert a reader-style header dict into a writer-style header dict
def reader_header_to_writer_header(header):
    return {
        "label": header["label"],
        "dimension": header["dimension"],
        "sample_frequency": header["sample_frequency"],
        "physical_min": header["physical_min"],
        "physical_max": header["physical_max"],
        "digital_min": header["digital_min"],
        "digital_max": header["digital_max"],
        "transducer": header["transducer"],
        "prefilter": header["prefilter"],
    }

#%% Function to modify one EDF file and save it to dest_dir
def modify_edf_file(edf_path, parquet_path, dest_path):

    reader = pyedflib.EdfReader(edf_path)
    try:
        n_signals = reader.signals_in_file
        reader_headers = reader.getSignalHeaders()
        signals = [reader.readSignal(i) for i in range(n_signals)]
        patient_name = reader.getPatientName()
        recording_additional = reader.getRecordingAdditional()
        start_datetime = reader.getStartdatetime()
    finally:
        reader.close()

    writer_headers = [reader_header_to_writer_header(h) for h in reader_headers]

    # change Empatica accelerometer channel units to g/64
    for header in writer_headers:
        label_lower = header["label"].lower()
        is_emp_acc = "emp" in label_lower and any(
            axis in label_lower for axis in ["accx", "accy", "accz"]
        )
        if is_emp_acc:
            header["dimension"] = "g/64"

    # rename the manual score channel
    for header in writer_headers:
        label_lower = header["label"].lower()
        if "manual" in label_lower and "score" in label_lower:
            header["label"] = "PSG_Manual_Scor1"

    #  insert ManualScores2 as a new channel, if available
    sub_data = pd.read_parquet(parquet_path, columns=["SleepScores", "SleepScoreEpochs"])
    psg_scores = sub_data.at["PSG", "SleepScores"]

    if "ManualScores2" in psg_scores:
        man_2 = np.asarray(psg_scores["ManualScores2"], dtype="float64")

        new_header = {
            "label": "PSG_Manual_Scor2",
            "dimension": "Unitless",
            "sample_frequency": 1 / 30,
            "physical_min": -1,
            "physical_max": 4,
            "digital_min": -32768,
            "digital_max": 32767,
            "transducer": "Sleep_scores",
            "prefilter": "",
        }

        writer_headers.append(new_header)
        signals.append(man_2)

    #Write the modified EDF
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)

    writer = pyedflib.EdfWriter(dest_path, len(writer_headers), file_type=pyedflib.FILETYPE_EDFPLUS)
    writer.setPatientName(patient_name)
    writer.setRecordingAdditional(recording_additional)
    writer.setStartdatetime(start_datetime)
    writer.setSignalHeaders(writer_headers)
    writer.writeSamples(signals)
    writer.close()
    
#%% Process each EDF file
for edf_path in edf_files:

    sub_folder = os.path.basename(os.path.dirname(os.path.dirname(edf_path)))  # e.g. "sub-001"
    num_id = extract_num_id(sub_folder)
    parquet_path = pq_lookup.get(num_id)

    if parquet_path is None:
        print(f"No matching parquet found for {sub_folder}, skipping.")
        continue

    print(f"Processing {sub_folder}...")

    rel_path = os.path.relpath(edf_path, edf_dir)
    dest_path = os.path.join(dest_dir, rel_path)

    modify_edf_file(edf_path, parquet_path, dest_path)