"""
https://github.com/Niloy333/Wearanize_plus
Created by Niloy Sikder (scholar.google.com/citations?user=0ALk5j4AAAAJ&hl=en)
Affiliations: PhD Candidate, Radboud University Medical Center, Donders Institute for Brain, Cognition and Behaviour, Nijmegen, The Netherlands &
Scientific Assistant, Faculty of Technology and Bionics, Rhine-Waal University of Applied Sciences, Kleve, Germany.
Contact: niloy.sikder@donders.ru.nl, niloy.sikder@hochschule-rhein-waal.de.
Project Supervision: Matthias Krauledat, Paul Zerr, and Martin Dresler.
Copyright (c) 2025 Niloy Sikder
"""

#%% csv to tsv BIDS

import os
import pandas as pd

data_dir = r"C:\Sciebo_files\_24. Wrnzp_data_paper\eegfloss_plugnplay\PlugNPlay_EEG_usability"
out_dir = r"C:\3028005.01_Local\Wearanize+_dataset_v1.0\Wearanize+_PlugNPlay\derivatives\eegfloss-v1.0"

# List all CSV files
csv_files = [f for f in os.listdir(data_dir) if f.endswith(".csv")]
print("Found CSV files:", csv_files)

for file in csv_files:
    file_path = os.path.join(data_dir, file)
    df = pd.read_csv(file_path, comment="#")

    # Rename columns according to BIDS
    df = df.rename(columns={
        "Start_time_sec": "onset",
        "End_time_sec": "offset"
    })

    # Add duration column (set to 10 for all rows)
    df["duration"] = 10

    # Reorder columns: onset, duration, offset, then others
    cols = ["onset", "duration", "offset"] + [c for c in df.columns if c not in ["onset", "duration", "offset"]]
    df = df[cols]

    # Extract subject number from filename (e.g., Sub001s1_... → sub-001)
    subj_num = file.split("s")[0].replace("Sub", "").zfill(3)  # "001"
    subj_label = f"sub-{subj_num}"

    # Create output folder: out_dir/sub-XXX/eeg/
    out_subdir = os.path.join(out_dir, subj_label, "eeg")
    os.makedirs(out_subdir, exist_ok=True)

    # Define output file name
    out_file = os.path.join(out_subdir, f"{subj_label}_task-sleep_proc-artifacts.tsv")

    # Save as TSV
    df.to_csv(out_file, sep="\t", index=False)
    print(f"Saved: {out_file}")

#%% .json:
import os
import json

data_dir = r"C:\3028005.01_Local\Wearanize+_dataset_v1.0\Wearanize+_PlugNPlay\derivatives\eegfloss-v1.0"

# Base dictionary template
base_dict = {
    "Name": None,  # will be filled per file
    "Columns": {
        "onset": {
            "Description": "Start time of the epoch in seconds from the beginning of the recording."
        },
        "duration": {
            "Description": "Duration of the epoch in seconds."
        },
        "offset": {
            "Description": "End time of the epoch in seconds from the beginning of the recording."
        },
        "channel": {
            "Description": "Name of the EEG channel (same as the corresponding EDF)."
        },
        "artifact_score": {
            "Description": "Numeric artifact/usability score produced by eegUsability v1.0.",
            "Units": "unitless",
            "Range": [0, 4]
        },
        "artifact_label": {
            "0": "usable/good data",
            "1": "no data",
            "2": "high noise",
            "3": "spiky noise",
            "4": "M-shaped noise"
        }
    },
    "Computation": {
        "PipelineName": "eegFloss",
        "PipelineVersion": "v1.0",
        "Model": "eegUsability (default v1.0)",
        "Description": (
            "Epoch-wise artifact / usability detection applied to synchronized EDF signals. "
            "The algorithm computes per-channel usability/artifact scores on fixed-length epochs "
            "and assigns class labels."
        ),
        "CodeURL": "https://github.com/Niloy333/eegFloss"
    },
    "EpochLength": 10,
    "Contact": {
        "Name": "Niloy Sikder",
        "Email": "niloy.sikder@hochschule-rhein-waal.de"
    }
}

# Walk through all subfolders
for root, _, files in os.walk(data_dir):
    for file in files:
        if file.endswith(".tsv"):
            tsv_path = os.path.join(root, file)
            json_path = tsv_path.replace(".tsv", ".json")
            
            # Copy base dict and update Name field
            dict_der = base_dict.copy()
            dict_der["Name"] = f"{os.path.basename(json_path)} (sidecar for proc-artifacts TSV)"
            
            # Save as JSON
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(dict_der, f, indent=4)
            
            print(f"Saved: {json_path}")

#%% copying pngs

import os
import shutil
import re

data_dir = r"C:\Sciebo_files\_24. Wrnzp_data_paper\eegfloss_plugnplay\PlugNPlay_EEG_usability"
out_dir = r"C:\3028005.01_Local\Wearanize+_dataset_v1.0\Wearanize+_PlugNPlay\derivatives\eegfloss-v1.0"

# Regex to extract subject ID (e.g., "005" from "Sub005s1_usability_graph.png")
pattern = re.compile(r"Sub(\d+)s\d+_usability_graph\.png", re.IGNORECASE)

for root, _, files in os.walk(data_dir):
    for file in files:
        if file.lower().endswith(".png"):
            match = pattern.match(file)
            if match:
                sub_id = match.group(1).zfill(3)  # pad to 3 digits
                src = os.path.join(root, file)

                # Construct output path
                sub_dir = os.path.join(out_dir, f"sub-{sub_id}", "eeg")
                dst = os.path.join(sub_dir, f"sub-{sub_id}_task-sleep_proc-artifacts.png")

                # Copy file
                shutil.copy2(src, dst)
                print(f"Copied {src} -> {dst}")

#%% dataset desc:
    
eegfloss_dataset_description = {
    "Name": "Wearanize+ eegFloss derivatives (PlugNPlay subset)",
    "BIDSVersion": "1.10.0",
    "DatasetType": "derivative",
    "GeneratedBy": [
        {
            "Name": "eegFloss",
            "Version": "v1.0",
            "CodeURL": "https://github.com/Niloy333/eegFloss",
            "Parameters": {
                "Model": "eegUsability (default v1.0)",
                "EpochLengthSeconds": 10,
                "InputSamplingRateHz": 256
            },
            "Description": (
                "Epoch-wise artifact/usability detection producing per-epoch, "
                "per-channel artifact labels. See per-subject sidecars "
                "(e.g. sub-005_task-sleep_proc-artifacts.json) for column "
                "definitions and interpretation."
            )
        }
    ],
    "ArtifactLabels": {
        "0": "usable/good data",
        "1": "no data",
        "2": "high noise",
        "3": "spiky noise",
        "4": "M-shaped noise"
    },
    "EpochLength": 10,
    "SourceDatasets": [
        {
            "URL": "https://data.ru.nl/collections/di/dccn/DSC_3028005.01_077",
            "Description": "Wearanize+ PlugNPlay."
        }
    ],
    "HowToAcknowledge": (
        "Sikder, N., Zerr, P., Esfahani, M. J., Dresler, M., & Krauledat, M. (2025). "
        "eegFloss: A Python package for refining sleep EEG recordings using machine "
        "learning models (Version 1). arXiv. https://doi.org/10.48550/ARXIV.2507.06433"
    ),
    "License": "MIT",
    "ReferencesAndLinks": [
        "https://github.com/Niloy333/eegFloss"
    ],
    "Contact": {
        "Name": "Niloy Sikder",
        "Email": "niloy.sikder@hochschule-rhein-waal.de"
    }
}

import pathlib
out_path = Path(r"C:\3028005.01_Local\Wearanize+_dataset_v1.0\Wearanize+_PlugNPlay\derivatives\dataset_description.json")
out_path.parent.mkdir(parents=True, exist_ok=True)
out_path.write_text(json.dumps(eegfloss_dataset_description, indent=2, ensure_ascii=False), encoding="utf-8")

print("Wrote:", out_path)
