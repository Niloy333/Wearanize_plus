"""
Script to read and process subject data from the PlugNPlay version of the Wearanize+ dataset.

Author: Niloy Sikder
Affiliations:
- Radboud University Medical Center, Donders Institute for Brain, Cognition and Behaviour, Nijmegen, The Netherlands
- Faculty of Technology and Bionics, Rhine-Waal University of Applied Sciences, Kleve, Germany
Contact: niloy.sikder@donders.ru.nl, niloy.sikder@hochschule-rhein-waal.de
Google Scholar: https://scholar.google.com/citations?user=0ALk5j4AAAAJ&hl=en
ORCID: 0000-0002-9016-6105
"""

#%% Required Libraries
import pandas as pd
import pyarrow as pa #necessary
from datetime import datetime
import os
import glob

#%% Load a Subject's Data

# Define the root directory where the dataset is stored
data_dir = r"C:\3028005.01_Local\Wearanize+_dataset_v1.0\7.PlugNPlay_version"  # Update this path as needed

# Define a sample subject ID (e.g., 'Sub005')
sub_1 = 'Sub005s1'

# Construct the path to the subject's Parquet file
sub_dir = os.path.join(data_dir, sub_1 + '.parquet')

# Read the subject's data from the Parquet file
sub_data = pd.read_parquet(sub_dir)

# Print the columns available in the dataset
print("Available columns:")
print(sub_data.columns)

# If you only need specific columns, use the `columns` parameter to save memory
sub_scores = pd.read_parquet(sub_dir, columns=["SubjectID", "SleepScores"])

#%% Dataset Description
"""
Column Overview:
1. 'SubjectID': Unique identifier for the subject (dtype: string).
2. 'Device': Name of the recording device (dtype: string).
   Devices: Zmax, PSG, Empatica, ActivPAL; keys: Zmax, PSG, Emp, Activpal.
3. 'NumOfSignals': Number of signals recorded in 'SignalData' (dtype: int).
4. 'SignalLabel': List of signal names recorded by the device (dtype: object).
   Example: ['EEGL', 'EEGR', 'ACCX', etc.].
5. 'SignalStartDateTime': Start date and time of each signal's recording (%Y-%m-%d %H:%M:%S). 
   Usually the same for all signals of a device. For Zmax and Mentalab, the start times are unreliable.
6. 'SamplingRate': Sampling rate of each signal (dtype: float).
7. 'SignalDurationSec': Duration of each signal in seconds (dtype: float).
8. 'SignalLength': Length of each signal in data points (dtype: float).
9. 'SignalMin'/'SignalMax': Minimum and maximum values of signals (dtype: float).
10. 'SignalType'/'SignalUnit': Signal modalities (e.g., EEG, EMG) and units.
11. 'SignalData': Actual recorded data for each signal (dtype: float).
12. 'SleepScoreEpochs': Number of 30-second epochs in associated sleep scores.
13. 'SleepScores': Available sleep scores identified from associated device's data.

Notes:
- Some Pandas versions standardize the dictionary structure by aggregating keys across rows.
- Use 'SignalLabel' as the definitive keys to fetch data from each column after 'SignalLabel'. To extract data from columns (from 'SignalStartDateTime' to 'SignalData'), use only the keys present in the 'SignalLabel' column for that specific device, disregarding any empty or aggregated keys.
- In the 'SleepScores' column, PSG has two sets of scores:
    - 'Manual': Manual sleep stages identified from PSG data.
    - 'Usleep': Autoscores from the U-Sleep v2.0 model.
- PSG scores (manual or Usleep) may not always be present. Always check before reading.
"""

#%% Example Usage

# Extract subject and device details
subject_id = sub_data['SubjectID']['Zmax']  # Subject ID from Zmax device
device_name = sub_data['Device']['Zmax']  # Device name from Zmax device
print(f"Subject ID: {subject_id}, Device: {device_name}")

# Extract signal information
num_signals = sub_data['NumOfSignals']['Zmax']  # Number of signals for Zmax device
signal_labels = sub_data['SignalLabel']['Zmax'].tolist()  # List of signal labels for Zmax device
print(f"Number of Signals: {num_signals}, Labels: {signal_labels}")

# Extract PSG signal start times
signal_start_times = []
for label in sub_data['SignalLabel']['PSG']:
    time_str = sub_data['SignalStartDateTime']['PSG'][label]  # Get the start time string
    start_time = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")  # Convert to datetime object
    signal_start_times.append(start_time)  # Append to the list
print("PSG Signal Start Times:", signal_start_times)

# Extract sampling rates, durations, and lengths of signals
sampling_rates = [sub_data['SamplingRate']['Zmax'][label] for label in signal_labels]
signal_durations = [sub_data['SignalDurationSec']['Zmax'][label] for label in signal_labels]
signal_lengths = [sub_data['SignalLength']['Zmax'][label] for label in signal_labels]
print(f"Sampling Rates: {sampling_rates}, \nDurations: {signal_durations}, \nLengths: {signal_lengths}")

# Check signal data consistency
is_consistent = all(
    sub_data['SignalDurationSec']['Zmax'][label] * sub_data['SamplingRate']['Zmax'][label]
    == sub_data['SignalLength']['Zmax'][label]
    for label in signal_labels
)
print(f"Signal data consistency: {is_consistent}")

# Read specific signal data
signal_data_zmax_eegl = sub_data['SignalData']['Zmax']['EEGL']  # EEGL signal from Zmax device
signal_data_psg_f3 = sub_data['SignalData']['PSG']['F3']  # F3 signal from PSG device
signal_data_zmax_accx = sub_data['SignalData']['Zmax'].get('ACCX')  # ACCX signal from Zmax device (safe access)
signal_data_psg_eog1 = sub_data['SignalData']['PSG'].get('EOG1')  # EOG1 signal from PSG device (safe access)

# Read sleep scores (if available)
if "Manual" in sub_data["SleepScores"]["PSG"]:
    manual_scores = sub_data['SleepScores']['PSG']['Manual']  # Manual sleep scores
if "Usleep" in sub_data["SleepScores"]["PSG"]:
    usleep_scores = sub_data['SleepScores']['PSG'].get('Usleep')  # U-Sleep autoscores

#%% Read All Subjects' Data
# Note: Reading all raw signals at once may consume significant memory. Please check system memory first.

# Find all Parquet files in the data directory
pq_files = glob.glob(os.path.join(data_dir, "*.parquet"))

# Initialize a DataFrame to store manual sleep scores for all subjects
all_sub_manual_scores = pd.DataFrame(columns=["ManualScores"])

# Iterate through each subject's file
for sub_dir in pq_files:
    # Read the subject's data (only SubjectID and SleepScores columns to save memory)
    sub1 = pd.read_parquet(sub_dir, columns=["SubjectID", "SleepScores"])
    sub_id = sub1['SubjectID']['PSG']  # Extract subject ID

    # Check if manual scores are available for the subject
    if "Manual" in sub1["SleepScores"]["PSG"]:
        man_score = sub1["SleepScores"]['PSG']['Manual']  # Extract manual scores
        sub_score = pd.DataFrame([[man_score]], index=[sub_id], columns=["ManualScores"])  # Create a DataFrame row
        all_sub_manual_scores = pd.concat([all_sub_manual_scores, sub_score])  # Append to the main DataFrame

# Print the collected manual scores
print("Manual Sleep Scores for All Subjects:")
print(all_sub_manual_scores)

#%%