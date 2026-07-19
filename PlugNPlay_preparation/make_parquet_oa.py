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
import glob
import pandas as pd
import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq

#%% Paths and setup
data_dir = r"D:\wnzp_oa\Wearanize+_PlugNPlay_Parquet_v1.0\Wearanize+_PlugNPlay_Parquet_v1.0"
dest_dir = r"C:\Users\BlueWin\Downloads\Wearanize+_PlugNPlay_Parquet_v1.1"

os.makedirs(dest_dir, exist_ok=True)

pq_files = glob.glob(os.path.join(data_dir, "*.parquet"))

all_manual_scores = pd.read_parquet(r"D:\wnzp_oa\Wearanize+_manual_scores_Tania\scores_both_set.parquet")

#%% Index all_manual_scores by sub_id for quick lookup
manual_scores_lookup = all_manual_scores.set_index("sub_id")

#%% Process each parquet file
for sub_dir in pq_files:
    #sub_dir = pq_files[3]
    sub_data = pd.read_parquet(sub_dir)  # read the full table, all fields intact
    sub_id = sub_data.at["PSG", "SubjectID"]

    print(f"Processing subject: {sub_id}")

    # Change Empatica accelerometer units from g/16 to g/64
    if "Emp" in sub_data.index:
        emp_units = dict(sub_data.at["Emp", "SignalUnit"])
        for acc_key in ["ACCX", "ACCY", "ACCZ"]:
            if acc_key in emp_units:
                emp_units[acc_key] = "g/64"
        sub_data.at["Emp", "SignalUnit"] = emp_units

    # Task 2a: copy 'Manual' scores into a new 'ManualScores1' key in PSG
    psg_scores = dict(sub_data.at["PSG", "SleepScores"])
    if "Manual" in psg_scores:
        psg_scores["ManualScores1"] = psg_scores["Manual"]  # copy, original key stays for now
    sub_data.at["PSG", "SleepScores"] = psg_scores

    #delete 'Manual' key from every device row's SleepScores
    for device in sub_data.index:
        device_scores = sub_data.at[device, "SleepScores"]
        if isinstance(device_scores, dict) and "Manual" in device_scores:
            device_scores = dict(device_scores)  # copy
            device_scores.pop("Manual")
            sub_data.at[device, "SleepScores"] = device_scores

    #insert ManualScores2 if available for this subject
    if sub_id in manual_scores_lookup.index:
        score_row = manual_scores_lookup.loc[sub_id]
        if pd.notna(score_row["Scores2_epoch"]):
            psg_scores = dict(sub_data.at["PSG", "SleepScores"])
            psg_scores["ManualScores2"] = score_row["ManualScores_2"].astype("int8")
            sub_data.at["PSG", "SleepScores"] = psg_scores

    #Save to dest_dir with the same file name, gzip-compressed
    out_file_dir = os.path.join(dest_dir, os.path.basename(sub_dir))
    sub_data2 = pa.Table.from_pandas(sub_data)
    pq.write_table(sub_data2, out_file_dir, compression="gzip")

    del sub_data, sub_data2



#%% Sanity check:

from sklearn.metrics import confusion_matrix, accuracy_score, f1_score

#%% Paths
dest_dir = r"D:\wnzp_oa\Wearanize+_OA\Wearanize+_OA_PlugNPlay_Parquet_v1.1"
pq_files_v1_1 = glob.glob(os.path.join(dest_dir, "*.parquet"))

#%% Read ManualScores1 and ManualScores2 from each subject's saved parquet file
scores_1_list = []
scores_2_list = []

for sub_dir in pq_files_v1_1:

    sub_data = pd.read_parquet(sub_dir, columns=["SubjectID", "SleepScores"])
    sub_id = sub_data.at["PSG", "SubjectID"]

    psg_scores = sub_data.at["PSG", "SleepScores"]

    if "ManualScores1" in psg_scores and "ManualScores2" in psg_scores:
        man_1 = psg_scores["ManualScores1"]
        man_2 = psg_scores["ManualScores2"]

        if len(man_1) == len(man_2):
            scores_1_list.append(man_1)
            scores_2_list.append(man_2)
        else:
            print(f"Skipping {sub_id}: length mismatch ({len(man_1)} vs. {len(man_2)})")

#%% Flatten both score sets across all included subjects
scores_1_flat = np.concatenate(scores_1_list)
scores_2_flat = np.concatenate(scores_2_list)

#%% Confusion matrix, accuracy, and F1 score
conf_mat = confusion_matrix(scores_1_flat, scores_2_flat)
accuracy = accuracy_score(scores_1_flat, scores_2_flat)
f1 = f1_score(scores_1_flat, scores_2_flat, average="weighted")

print("Confusion matrix:\n", conf_mat)
print("Accuracy:", accuracy)
print("F1 score (weighted):", f1)

#%%