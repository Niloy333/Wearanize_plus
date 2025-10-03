"""
https://github.com/Niloy333/Wearanize_plus
Created by Niloy Sikder (scholar.google.com/citations?user=0ALk5j4AAAAJ&hl=en)
Affiliations: PhD Candidate, Radboud University Medical Center, Donders Institute for Brain, Cognition and Behaviour, Nijmegen, The Netherlands &
Scientific Assistant, Faculty of Technology and Bionics, Rhine-Waal University of Applied Sciences, Kleve, Germany.
Contact: niloy.sikder@donders.ru.nl, niloy.sikder@hochschule-rhein-waal.de.
Project Supervision: Matthias Krauledat, Paul Zerr, and Martin Dresler.
Copyright (c) 2025 Niloy Sikder
"""

#%% move EDF to dedicated folder

import os
import shutil

# base directory with EDF files
data_dir = r'C:\3028005.01_Local\Wearanize+_dataset_v1.0\7.PlugNPlay_version_with_autoscores\EDF'

# loop over files in data_dir
for fname in os.listdir(data_dir):
    if fname.endswith(".edf"):
        # example: Sub001s1.edf
        base, ext = os.path.splitext(fname)
        
        # remove 's1' part at the end
        if base.endswith("s1"):
            sub_id = base[:-2]   # keep Sub001, Sub002, etc.
        else:
            sub_id = base
        
        # make subject folder path
        sub_dir = os.path.join(data_dir, sub_id)
        os.makedirs(sub_dir, exist_ok=True)
        
        # destination file name
        new_name = f"{sub_id}_synced{ext}"
        dest_path = os.path.join(sub_dir, new_name)
        
        # move and rename
        src_path = os.path.join(data_dir, fname)
        shutil.move(src_path, dest_path)
        print(f"Moved {src_path} -> {dest_path}")

#%% generate file tree of the dataset

import os
from pathlib import Path

# set these paths exactly as requested
data_dir = Path(r'C:\3028005.01_Local\Wearanize+_dataset_v1.0\Wearanize+_PlugNPlay')
output_file = Path(r'C:\3028005.01_Local\Wearanize+_dataset_v1.0\file_tree.txt')

def write_tree(root: Path, file_obj, prefix: str = ''):
    """
    Recursively write a tree view of `root` into `file_obj`.
    Directories are listed with a trailing '/' and contents are indented.
    """
    try:
        entries = sorted(root.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
    except PermissionError:
        file_obj.write(f"{prefix}{root.name}/ [PermissionError]\n")
        return

    for entry in entries:
        if entry.is_dir():
            file_obj.write(f"{prefix}{entry.name}/\n")
            write_tree(entry, file_obj, prefix + '    ')
        else:
            file_obj.write(f"{prefix}{entry.name}\n")

# ensure the parent for the output exists
output_file.parent.mkdir(parents=True, exist_ok=True)

with output_file.open('w', encoding='utf-8') as f:
    # header: show the top-level folder name (matches example style)
    f.write(f"{data_dir.name}/\n")
    write_tree(data_dir, f, prefix='    ')

print(f"File tree saved to: {output_file}")

#%%
# Extract only the fields you listed from an EDF using pyedflib.
# Uses only pyedflib (no MNE). Does not load full signal arrays by default.
# Adjust `load_signal_data` to True if you want the actual SignalData included
# (may be very large).

from pathlib import Path
import json
import csv
from datetime import datetime
import pyedflib

sub_path = Path(r"C:\3028005.01_Local\Wearanize+_dataset_v1.0\Wearanize+_PlugNPlay\Sub005\Sub005_synced.edf")
dest_dir = Path(r"C:\3028005.01_Local\Wearanize+_dataset_v1.0\output files")
dest_dir.mkdir(parents=True, exist_ok=True)

meta_json = dest_dir / f"{sub_path.stem}_metadata_compact.json"
channels_csv = dest_dir / f"{sub_path.stem}_channels_compact.csv"
signaldata_npz = dest_dir / f"{sub_path.stem}_signaldata.npz"  # only used if load_signal_data=True

# If True, loads each channel's data into memory and saves a .npz with arrays.
# Default False to avoid heavy memory use.
load_signal_data = False

def infer_device_from_path_or_header(path: Path, header: dict) -> str:
    p = str(path).lower()
    # check common folder/name hints
    if "zmax" in p or "zmax" in header.get("patientcode", "").lower() or "zmax" in header.get("recording_additional", "").lower():
        return "Zmax"
    if "empatica" in p or "emp" in p or "empatica" in header.get("patientcode", "").lower():
        return "Empatica"
    if "activpal" in p or "activpal" in header.get("patientcode", "").lower():
        return "ActivPAL"
    # PSG/mentalab/other heuristics
    if "psg" in p or "psg" in header.get("recording_additional", "").lower():
        return "PSG"
    # fallback: unknown
    return "unknown"

def infer_signal_type(label: str) -> str:
    if not label:
        return "unknown"
    s = label.lower()
    if any(k in s for k in ("eeg", "eg", "cz", "fz", "oz", "pz", "fp")):
        return "EEG"
    if "emg" in s:
        return "EMG"
    if any(k in s for k in ("ecg", "ekg")):
        return "ECG"
    if any(k in s for k in ("acc", "ax", "ay", "az")):
        return "ACC"
    if "eog" in s:
        return "EOG"
    if any(k in s for k in ("eda", "gsr")):
        return "EDA"
    if "temp" in s:
        return "TEMP"
    if any(k in s for k in ("oxy", "sp02", "spo2", "o2")):
        return "OXY"
    return "unknown"

# open EDF
f = pyedflib.EdfReader(str(sub_path))

try:
    header = f.getHeader() or {}
    n_signals = int(f.signals_in_file)
    nsamples_per_record = f.getNSamples()  # list; interpreted as samples-per-datarecord for each signal in many EDFs
    datarecord_duration = header.get("datarecord_duration")  # seconds
    datarecords_in_file = header.get("datarecords_in_file")  # integer or None
    startdatetime = header.get("startdatetime")  # may be datetime or None

    # top-level fields mapped to your schema
    top_level = {
        "SubjectID": header.get("patientcode") or sub_path.parent.name or sub_path.stem,
        "Device": infer_device_from_path_or_header(sub_path, header),
        "NumOfSignals": n_signals,
        "SignalStartDateTime": startdatetime.isoformat() if isinstance(startdatetime, datetime) else (str(startdatetime) if startdatetime else None)
    }

    channels = []
    signal_data_store = {}  # only filled if load_signal_data True

    for ch_idx in range(n_signals):
        ch_hdr = f.getSignalHeader(ch_idx) or {}
        label = ch_hdr.get("label") or f"ch{ch_idx}"
        # attempt to determine sampling rate:
        sampling_rate = None
        total_samples = None
        duration_sec = None

        # If we have samples-per-datarecord and datarecord duration -> sample rate can be computed
        try:
            ns_per_rec = int(nsamples_per_record[ch_idx]) if nsamples_per_record is not None else None
        except Exception:
            ns_per_rec = None

        if ns_per_rec and datarecord_duration:
            sampling_rate = ns_per_rec / float(datarecord_duration)
            if datarecords_in_file:
                total_samples = int(ns_per_rec * int(datarecords_in_file))
                duration_sec = float(datarecord_duration) * int(datarecords_in_file)
        else:
            # fallback: if load_signal_data enabled, read whole channel to infer lengths and compute sample rate
            if load_signal_data:
                sig = f.readSignal(ch_idx)  # numpy array
                signal_data_store[label] = sig
                total_samples = int(sig.shape[0])
                # if we have datarecords_in_file and datarecord_duration maybe compute sampling_rate else unknown
                if datarecords_in_file and datarecord_duration:
                    duration_sec = float(datarecord_duration) * int(datarecords_in_file)
                    sampling_rate = total_samples / duration_sec if duration_sec else None

        # physical min/max are per-channel limits from header
        phys_min = ch_hdr.get("physical_min")
        phys_max = ch_hdr.get("physical_max")
        unit = ch_hdr.get("dimension") or ch_hdr.get("physical_dimension") or None  # pyedflib may use 'dimension' key

        ch_dict = {
            "SubjectID": top_level["SubjectID"],
            "Device": top_level["Device"],
            "SignalIndex": ch_idx,
            "SignalLabel": label,
            "SamplingRate": float(sampling_rate) if sampling_rate is not None else None,
            "SignalDurationSec": float(duration_sec) if duration_sec is not None else None,
            "SignalLength": int(total_samples) if total_samples is not None else None,
            "SignalMin": phys_min,
            "SignalMax": phys_max,
            "SignalType": infer_signal_type(label),
            "SignalUnit": unit,
            # we avoid embedding huge SignalData by default; store reference to NPZ when written
            "SignalData": None
        }

        channels.append(ch_dict)

    # Sleep score fields: not typically in EDF header — set to None (user can fill if available)
    top_level["SleepScoreEpochs"] = None
    top_level["SleepScores"] = None

finally:
    f.close()

# Optionally save signal arrays to .npz if loaded
if load_signal_data and signal_data_store:
    import numpy as np
    np.savez_compressed(signaldata_npz, **signal_data_store)
    # update channel entries to point to items in NPZ
    for ch in channels:
        ch["SignalData"] = f"{signaldata_npz.name}::{ch['SignalLabel']}"

# Save JSON (top-level + channels)
out_obj = {"file_header": top_level, "channels": channels}
meta_json.write_text(json.dumps(out_obj, indent=2, ensure_ascii=False), encoding="utf-8")

# Save channels CSV for easy viewing
if channels:
    with channels_csv.open("w", newline="", encoding="utf-8") as csvf:
        fieldnames = list(channels[0].keys())
        writer = csv.DictWriter(csvf, fieldnames=fieldnames)
        writer.writeheader()
        for ch in channels:
            writer.writerow(ch)

print("Wrote compact metadata JSON to:", meta_json)
print("Wrote channel CSV to:", channels_csv)
if load_signal_data and signal_data_store:
    print("Saved signal arrays to:", signaldata_npz)

#%% dataset_description.json (plugnplay)

from pathlib import Path
import json

dataset_description = {
    "Name": "Wearanize+_PlugNPLay",
    "BIDSVersion": "1.10.0",
    "DatasetType": "raw",
	"_comment": "The time-series signals are raw, but they have been synced and trimmed.",
    "License": "Open access for registered users of the Radboud Data Repository (RDR)",
    "Authors": [
        "Niloy Sikder",
        "Lieuwe Verkaar",
        "Anastasiya Paltarzhytskaya",
        "Selin Acan",
        "Leonore Bovy",
        "Tatiana Almazova",
        "Elena Krugliakova",
        "Yevgenia Rosenblum",
        "Matthias Krauledat",
        "Martin Dresler",
        "Paul Zerr"
    ],
    "Acknowledgements": "Donders Centre for Cognitive Neuroimaging (DCCN), Radboud University",
    "HowToAcknowledge": "Sikder N., Verkaar L., Paltarzhytskaya A., Acan S., Bovy L., Almazova T., Krugliakova E., Rosenblum Y., Krauledat M., Dresler M., & Zerr P. (2025). Wearanize+: A Multimodal Dataset for Evaluating Wearable Technologies in Sleep Research. Center for Open Science. https://doi.org/10.31219/osf.io/dth8y_v2",
    "EthicsApprovals": ["Donders Centre for Cognitive Neuroimaging (DCCN) blanket approval", "Protocol 'Imaging Human Cognition' (NL45659.091.14), approved by METC Oost-Nederland (2014/288)"],
    "ReferencesAndLinks": [
        "https://doi.org/10.31219/osf.io/dth8y_v2",
        "https://github.com/Niloy333/Wearanize_plus"
    ],
	"SourceDatasets": [
		{
		"URL": "https://data.ru.nl/collections/di/dccn/DSC_3028005.01_077",
		"DOI": "https://doi.org/10.34973/5nn8-mg45",
		"Version": "v1"
		},
		],
    "DatasetDOI": "10.31219/osf.io/dth8y_v2",
    "GeneratedBy": [
        {
			"Name": "Wearanize+ sync pipeline",
			"Version": "v1.0",
            "Description": "Raw wearable recordings of each subject were time-synchronized and consolidated into a single EDF file.Segments not related to the sleep period were trimmed from the start and end of the recorded night. PSG recordings were manually scored by an experienced scorer and additionally auto-scored with U-Sleep 2.0. For each subject, all time-synchronized raw signals and sleep scores were stored together in a single EDF file."
        }
    ]
}

# Minimal save (adjust path as needed)
out_path = Path(r"dataset_description.json")
out_path.parent.mkdir(parents=True, exist_ok=True)
out_path.write_text(json.dumps(dataset_description, indent=4, ensure_ascii=False), encoding="utf-8")

print("Saved dataset_description.json to:", out_path)

#%%participants.tsv plugnplay:

import pandas as pd

df = pd.read_excel(r"C:\3028005.01_Local\Wearanize+_dataset_v1.0\6.Questionnaires\Wearanize+_questionnaire_responses.xlsx", sheet_name=0)

df = df.drop(df.columns[[0, 1, 3]], axis=1)
df.columns = ["participant_id", "age", "gender", "handedness"]
df["gender"] = df["gender"].map({1: "M", 2: "F"})
df["handedness"] = df["handedness"].map({1: "R", 2: "L", 3: "A"})
df["participant_id"] = df["participant_id"].str.replace("s1", "", regex=False)
df["participant_id"] = df["participant_id"].str.replace("sub", "sub-", regex=False)
df["participant_id"] = df["participant_id"].str.replace("Sub", "sub-", regex=False)

df.to_csv("participants.tsv", sep="\t", index=False)

#%% participants.json plugnplay

participants_json = {
    "participant_id": {
        "Description": "Unique numerical identifier assigned to the participant; also known as subject ID; Expressed as 'sub'+'unique_numerical_id'.",
        "LongName": "Participant identifier"
    },
    "age": {
        "Description": "Age of the participant at the time of recording.",
        "Units": "years",
        "LongName": "Age"
    },
    "gender": {
        "Description": "Gender reported by the participant.",
        "Levels": {
            "M": "male",
            "F": "female",
            "O": "other / unknown / not reported"
        },
        "LongName": "Self-reported gender"
    },
    "handedness": {
        "Description": "Participant's dominant hand.",
        "Levels": {
            "R": "right",
            "L": "left",
            "A": "ambidextrous"
        },
        "LongName": "Handedness"
    }
}

out_path = Path(r'participants.json')
out_path.write_text(json.dumps(participants_json , indent=4, ensure_ascii=False), encoding="utf-8")

#%% Sub001>>sub-001

data_dir = r"C:\3028005.01_Local\Wearanize+_dataset_v1.0\Wearanize+_PlugNPlay"

for folder in os.listdir(data_dir):
    old_path = os.path.join(data_dir, folder)
    if os.path.isdir(old_path) and folder.lower().startswith("sub"):
        # Extract numeric part
        num = folder[3:]
        new_name = f"sub-{num}"
        new_path = os.path.join(data_dir, new_name)
        os.rename(old_path, new_path)
        print(f"Renamed: {folder} -> {new_name}")

#%% sub-001/Sub001_synced >> sub-001/eeg/sub-001_task-sleep_desc-synced_eeg.edf

import os
import shutil

data_dir = r"C:\3028005.01_Local\Wearanize+_dataset_v1.0\Wearanize+_PlugNPlay"

for root, dirs, files in os.walk(data_dir):
    for file in files:
        if file.lower().endswith(".edf"):
            old_path = os.path.join(root, file)

            # get subject id from parent folder (e.g., sub-001)
            parent_folder = os.path.basename(root).lower()

            if parent_folder.startswith("sub-"):
                # define eeg folder
                eeg_folder = os.path.join(root, "eeg")
                os.makedirs(eeg_folder, exist_ok=True)

                # construct new filename
                new_filename = f"{parent_folder}_task-sleep_eeg_synced.edf"
                new_path = os.path.join(eeg_folder, new_filename)

                # move & rename
                shutil.move(old_path, new_path)
                print(f"Moved & renamed: {old_path} -> {new_path}")

for root, dirs, files in os.walk(data_dir):
    for file in files:
        if file.lower().endswith(".edf"):
            old_path = os.path.join(root, file)

            # insert "desc-" before "synced"
            if "synced" in file.lower():
                new_file = file.lower().replace("synced", "desc-synced")
                new_path = os.path.join(root, new_file)

                os.rename(old_path, new_path)
                print(f"Renamed: {file} -> {new_file}")
                
for root, dirs, files in os.walk(data_dir):
    for file in files:
        if file.lower().endswith(".edf"):
            old_path = os.path.join(root, file)
            filename = file.lower()

            if "_eeg_" in filename:  
                # move `_eeg_` to just before extension
                new_filename = filename.replace("_eeg_", "_").replace(".edf", "_eeg.edf")
                new_path = os.path.join(root, new_filename)

                os.rename(old_path, new_path)
                print(f"Renamed: {file} -> {new_filename}")

#%% removing extra subjects from participants.tsv

from pathlib import Path
data_dir = r'C:\3028005.01_Local\Wearanize+_dataset_v1.0\Wearanize+_PlugNPlay'
subfolders = sorted([p.name for p in Path(data_dir).iterdir() if p.is_dir()])

df2 = pd.read_csv(r"C:\3028005.01_Local\Wearanize+_dataset_v1.0\Wearanize+_PlugNPlay\participants.tsv", sep="\t")

df3 = df2[df2['participant_id'].astype(str).isin(subfolders)].copy()

df3.to_csv("participants.tsv", sep="\t", index=False)


#%% sub-001_task-sleep_desc-synced_eeg.json:
import json
dict2 = {
    "TaskName": "sleep",
    "RecordingType": "continuous",
    "Manufacturer": "Somnomedics",
    "ManufacturersModelName": "SOMNOscreen",
    "OtherDevices": [
        {
            "Name": "Zmax",
            "Manufacturer": "Hypnodyne",
            "Placement": "forehead"
        },
        {
            "Name": "Empatica E4",
            "Manufacturer": "Empatica",
            "Placement": "wrist of the non-dominant hand"
        },
        {
            "Name": "ActivPAL",
            "Manufacturer": "PAL Technologies",
            "Placement": "right thigh"
        }
    ],
    "TaskDescription": (
        "Overnight sleep recording collected at home. Participants were prepared in "
        "the sleep lab and then instructed to sleep at home as usual; no experimental "
        "stimuli were presented."
    ),
    "Instructions": "See the associated publication: https://doi.org/10.31219/osf.io/dth8y_v2",
    "SamplingFrequency": 256,
    "PowerLineFrequency": 50,
    "SleepScoreEpochLength": 30,
    "SleepScoreLabels": {
        "-1": "Artifact",
        "0": "Wake",
        "1": "N1",
        "2": "N2",
        "3": "N3",
        "4": "REM"
    },
    "PSGPosLabels": {
        "1": "Prone",
        "2": "Upright",
        "3": "Left",
        "4": "Right",
        "5": "Upright (Head)",
        "6": "Supine"
    },
    "InstitutionName": "Donders Centre for Cognitive Neuroimaging",
    "InstitutionAddress": "Kapittelweg 29, 6525 EN Nijmegen, the Netherlands",
    "EEGPlacementScheme": "10-20 system",
    "EEGPlacementSchemeByDevice": {
        "SOMNOscreen": "10-20 system",
        "Mentalab": "10-20 system"
    },
    "EEGGround": "Cz of 10-20 system",
    "EEGReference": (
        "A1/A2 mastoid notation present in channel names (e.g., 'F3:A2'); "
        "otherwise, the reference channel."
    ),
    "SoftwareVersions": "DOMINO 2.8.0; Hypnodyne 20220811_153338; E4 Connect 2.0.3.5119; PALconnect 9.1.2.168; PALanalysis 9.1.0.102; MATLAB R2023b; Python 3.10",
    "SoftwareFilters": "n/a",
    "RecordingNotes": (
        "Signals from PSG (SomnoScreen), Zmax, Empatica E4 and ActivPAL were "
        "time-synchronized and consolidated. Non-sleep segments at the beginning/end "
        "of the night were trimmed. PSG was manually scored by an expert and also "
        "auto-scored with U-Sleep 2.0."
    ),
    "Version": "PlugNPlay v1.0"
}

dict3 = {
    "min_val": {
        "Description": "Minimum measurable value of this channel",
        "Units": "µV"
    },
    "max_val": {
        "Description": "Maximum measurable value of this channel",
        "Units": "µV"
    },
    "duration": {
        "Description": "Length of the recorded time segment for this channel",
        "Units": "s"
    }
}

dict3 = {
  "min_val": {
    "Description": "Minimum measurable value of this channel",
    "Units": "µV"
  },
  "max_val": {
    "Description": "Maximum measurable value of this channel",
    "Units": "µV"
  },
  "duration": {
    "Description": "Length of the recorded time segment for this channel",
    "Units": "s"
  }
  }


#%% channels.tsv plugnplay

data_dir = r'D:\Wearanize+_PlugNPlay_BIDS_v1.0'

import os
import math
import pyedflib
import pandas as pd

def _safe(callable_obj, *args, default=None):
    """Call callable_obj(*args) and return default on any Exception."""
    try:
        return callable_obj(*args)
    except Exception:
        return default
    
edf_files = []
for root, dirs, files in os.walk(data_dir):
    for file in files:
        if file.lower().endswith(".edf"):
            edf_files.append(os.path.join(root, file))

edf_files = sorted(edf_files)

for fp in edf_files:
    print(os.path.basename(fp))
    sub_id = os.path.basename(fp).split('_')[0].split('-')[1]
    rows = []
    try:
        edf = pyedflib.EdfReader(fp)
    except Exception as e:
        print(f"Skipping file (cannot open): {fp}  —  {e}")
        continue

    try:
        # number of signals (channels)
        n_signals = int(getattr(edf, "signals_in_file", 0) or 0)

        # labels: convert to list of strings (fallback to empty strings)
        labels_res = _safe(edf.getSignalLabels, default=None)
        if labels_res is None:
            labels = ["" for _ in range(n_signals)]
        else:
            labels = [("" if x is None else str(x)) for x in labels_res]

        # nsamples: convert array-like to list of ints (fallback to zeros)
        nsamples_res = _safe(edf.getNSamples, default=None)
        if nsamples_res is None:
            nsamples_list = [0 for _ in range(n_signals)]
        else:
            try:
                nsamples_list = [int(x) for x in nsamples_res]
            except Exception:
                nsamples_list = [0 for _ in range(n_signals)]

        # iterate channels
        for i in range(n_signals):
            label = labels[i] if i < len(labels) else ""

            transducer = _safe(edf.getTransducer, i, default="")
            if transducer is None:
                transducer = ""
            if isinstance(transducer, bytes):
                transducer = transducer.decode("utf-8", errors="replace")
            transducer = str(transducer)

            dimension = _safe(edf.getPhysicalDimension, i, default="")
            if dimension is None:
                dimension = ""
            if isinstance(dimension, bytes):
                dimension = dimension.decode("utf-8", errors="replace")
            dimension = str(dimension)

            sample_rate = _safe(edf.getSampleFrequency, i, default=float("nan"))
            try:
                sample_rate = float(sample_rate)
                if math.isfinite(sample_rate) is False:
                    sample_rate = float("nan")
            except Exception:
                sample_rate = float("nan")

            phys_min = _safe(edf.getPhysicalMinimum, i, default=float("nan"))
            try:
                phys_min = float(phys_min)
            except Exception:
                phys_min = float("nan")

            phys_max = _safe(edf.getPhysicalMaximum, i, default=float("nan"))
            try:
                phys_max = float(phys_max)
            except Exception:
                phys_max = float("nan")

            n_samples = nsamples_list[i] if i < len(nsamples_list) else 0
            try:
                n_samples = int(n_samples)
            except Exception:
                n_samples = 0

            # duration in seconds (safe division)
            if sample_rate and not math.isnan(sample_rate) and sample_rate > 0:
                duration = float(n_samples) / float(sample_rate)
            else:
                duration = float("nan")

            
            if dimension == 'uV':
                dimension = 'µV'
            elif dimension == 'MicroSie':
                dimension = 'µS'
            elif dimension == 'degC':
                dimension = '°C'
            elif dimension == 'g/16':
                dimension = 'g/64'
                
            if label.startswith('Zmax'):
                desc = "Device: Zmax headband (Hypnodyne)"
            elif label.startswith('PSG'):
                if sub_id in ['115', '124', '129', '130']:
                    desc = "Device: Mentalab Explore Pro (Mentalab GmbH)"
                else:
                    desc = "Device: SOMNOscreen plus (Somnomedics)"
            elif label.startswith('Emp'):
                desc = "Device: Empatica E4 wristband (Empatica)"
            elif label.startswith('ActivPal'):
                desc = "Device: ActivPAL leg patch (PAL Technologies)"
            
            
            if transducer in ['ACC', 'ACC (aggregated)', 'Accelerometer']:
                transducer = 'ACCEL'
            elif transducer == 'Gyroscope':
                transducer = 'GYRO'
            elif transducer == 'Magnetometer':
                transducer = 'MAGN'
            elif transducer == 'EDA':
                transducer = 'GSR'
            elif transducer == 'BVP':
                transducer = 'PPG'
            elif transducer == 'HR':
                transducer = 'MISC'
            elif transducer == 'Sleep_scores':
                transducer = 'MISC'
            elif transducer == 'Body Position':
                transducer = 'POS'
            elif transducer == 'Noise':
                transducer = 'MISC'                    
            
            rows.append({
                "name": label,
                "type": transducer,
                "units": dimension,
                "sampling_frequency": sample_rate,
                "max_val": phys_max,
                "min_val": phys_min,
                "duration": duration,
                "description": desc,
            })
    finally:
        try:
            edf.close()
        except Exception:
            pass

    # create dataframe with exact column ordering requested
    cols = ["name", "type", "units", "sampling_frequency", "max_val", "min_val", "duration", "description"]
    df = pd.DataFrame(rows, columns=cols)
    
    out_dir = fp.replace("_eeg.edf", "_channels.tsv")    
    df.to_csv(out_dir, sep='\t', index=False)
    del df, rows
    
    json_dir = fp.replace(".edf", ".json")
    with open(json_dir, "w", encoding="utf-8") as f:
        json.dump(dict2, f, indent=4, ensure_ascii=False)
    
    json_dir2 = fp.replace("_eeg.edf", "_channels.json")
    with open(json_dir2, "w", encoding="utf-8") as f:
        json.dump(dict3, f, indent=4, ensure_ascii=False)

#%%

eegfloss_derivative = {
    "Name": "Wearanize+ eegFloss derivatives (PlugNPlay subset)",
    "BIDSVersion": "1.10.0",
    "DatasetType": "derivative",
    "GeneratedBy": [
        {
            "Name": "eegFloss",
            "Version": "v1.0.0",
            "CodeURL": "https://github.com/Niloy333/eegFloss",
            "Parameters": {
                "model": "eegUsability (default v1.0)",
                "epoch_length_seconds": 10,
                "input_sampling_rate_hz": 256,
                "quality_metric": "usability_index",
                "notes": "See per-subject sidecars for column definitions and any post-processing thresholds."
            },
            "Description": (
                "Epoch-wise EEG usability/quality scores produced by eegFloss v1.0.0. "
                "Scores were computed on 10-second epochs (start/end times provided in per-subject TSVs). "
                "For mixed-rate recordings, per-channel sampling rates are taken from the raw channels.tsv."
            )
        }
    ],
    "SourceDatasets": [
        {
            "URL": "doi:10.31219/osf.io/dth8y_v2",
            "Description": "Original Wearanize+ raw dataset used to generate these derivatives."
        }
    ],
    "HowToAcknowledge": (
        "Sikder N., Verkaar L., Paltarzhytskaya A., Acan S., Bovy L., Almazova T., "
        "Krugliakova E., Rosenblum Y., Krauledat M., Dresler M., & Zerr P. (2025). "
        "Wearanize+: A Multimodal Dataset for Evaluating Wearable Technologies in Sleep Research. "
        "Center for Open Science. https://doi.org/10.31219/osf.io/dth8y_v2. "
        "Derivatives generated with eegFloss v1.0.0 (https://github.com/Niloy333/eegFloss)."
    ),
    "License": "Open Access for registered users of Radboud Data Repository (RDR)",
    "ReferencesAndLinks": [
        "https://doi.org/10.31219/osf.io/dth8y_v2",
        "https://github.com/Niloy333/eegFloss"
    ]
}

#%%
import os
import glob

data_dir = r"C:\3028005.01_Local\Wearanize+_dataset_v1.0\Wearanize+_PlugNPlay"

# File types of interest
extensions = ("*.edf", "*.tsv", "*.json")

# Collect files
files = []
for ext in extensions:
    files.extend(glob.glob(os.path.join(data_dir, "**", ext), recursive=True))

# Rename files by replacing "proc" with "desc"
for f in files:
    dirname, fname = os.path.split(f)
    if "proc" in fname:
        new_fname = fname.replace("proc", "desc")
        new_path = os.path.join(dirname, new_fname)
        print(f'Renaming:\n{f}\n -> {new_path}\n')
        os.rename(f, new_path)

#%%
import os
import glob

data_dir = r"C:\3028005.01_Local\Wearanize+_dataset_v1.0\Wearanize+_PlugNPlay"

# File types of interest
extensions = ("*.edf", "*.tsv", "*.json")

# Collect files
files = []
for ext in extensions:
    files.extend(glob.glob(os.path.join(data_dir, "**", ext), recursive=True))

# Rename files by removing "_desc-synced"
for f in files:
    dirname, fname = os.path.split(f)
    if "_desc-synced" in fname:
        new_fname = fname.replace("_desc-synced", "")
        new_path = os.path.join(dirname, new_fname)
        print(f'Renaming:\n{f}\n -> {new_path}\n')
        os.rename(f, new_path)


#%%
