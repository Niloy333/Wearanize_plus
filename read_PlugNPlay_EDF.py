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
import os
import pyedflib # Tested on Version: 0.1.37

#%%
# Root directory of the PlugNPlay dataset:
data_dir = r"C:\3028005.01_Local\Wearanize+_dataset_v1.0\Wearanize+_PlugNPlay"

#%% Reading single-subject data:
# A sample subject:
sub_id = r'sub-005'
sub_data_dir = os.path.join(data_dir, sub_id, 'eeg', f"{sub_id}_task-sleep_eeg.EDF")

# reading data:
sub_edf = pyedflib.EdfReader(sub_data_dir)
print(f"{sub_data_dir} was read successfully")

# Get the number of channels:
n_channels = sub_edf.signals_in_file
print(f"Number of available channels: {n_channels}")

# Get signal labels:
signal_labels = sub_edf.getSignalLabels()
print("Names of the signals:\n" + "\n".join(signal_labels))

# Get sampling rates:
sampling_rates = sub_edf.getSampleFrequencies()

# Get a sample channel's data:
signal_name = 'PSG_F3'

# Find the index of channel index:
idx = signal_labels.index(signal_name)

# Read the time-series data:
signal_data = sub_edf.readSignal(idx)

# Get the corresponding manual sleep scores:
idx = signal_labels.index('PSG_Manual_score')
psg_scores = sub_edf.readSignal(idx)

# Read all the channels' data and store them in a dictionary:
all_signals = {}
for i, label in enumerate(signal_labels):
    all_signals[label] = sub_edf.readSignal(i)
print("All channels' data has been read.")

# Close the file after processing:
sub_edf.close()

#%% Read data from all subjects:
# Caution: storing all signal data from all subjects will require a lot of memory space

# Listing the directories of all the EDF files in the dataset:
edf_files = []
for root, dirs, files in os.walk(data_dir):
    for file in files:
        if file.lower().endswith(".edf"):
            edf_files.append(os.path.join(root, file))

# Read the 'PSG_F3' and 'PSG_Manual_score' channels from each subject and store them in a dictionary:
all_subs_data = {}

# Looping through the files:
for file_path in edf_files:
    filename = os.path.basename(file_path)
    
    # Getting the subject ID:
    sub_id = filename.split("_")[0] #e.g.: sub-005
    print(f"Reading data from {sub_id}...")
    
    # Reading the EDF:
    edf = pyedflib.EdfReader(file_path)
    
    # Getting signal labels:
    signal_labels = edf.getSignalLabels()
    
    # Reading 'PSG_F3' and 'PSG_Manual_score' channels:
    for ch_name in ['PSG_F3', 'PSG_Manual_score']:
        try:
            idx = signal_labels.index(ch_name)
            all_subs_data[f"{sub_id}_{ch_name}"] = edf.readSignal(idx)
        except:
            print(f"\t{ch_name} was not found in {sub_id}")        
    
    # Closing the file:
    edf.close()
    
print("\nAll subjects' data was read.")
            
#%%

