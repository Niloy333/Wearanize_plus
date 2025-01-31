# Wearanize Plus (Wearanize+)

Wearanize+ represents a sleep research project carried out at the Donders Centre for Cognitive Neuroimaging, Radboud University, Nijmegen, The Netherlands, and its resultant dataset.

## Overview

This repository contains scripts to preprocess the raw data and perform preliminary analysis.
For more details on the project, see [Wearanize+ Dataset v1.0 Publication](https://doi.org/10.31219/osf.io/dth8y_v1)

## Accessing the Dataset

The Wearanize+ dataset is publicly available on the Radboud Repository.  
To [access the data](https://data.ru.nl/collections/di/dccn/DAC_3028005.01_352), please open an [ORCID account](https://orcid.org/) and follow [these instructions](https://data.ru.nl/doc/help/helppages/visitor-manual/vm-request-access.html?14=). Please see the [FAQ section](https://data.ru.nl/doc/help/helppages/faq.html?20=) to solve common issues.
The published dataset version is titled *Wearanize+_v1.0.zip*, and the synchronized version is titled *Wearanize+_PlugNPlay_v1.0.zip*.

## Dataset Contents (PlugNPlay)
**Column descriptions:**
1. 'SubjectID': Unique identifier for the subject.
2. 'Device': Name of the recording device. (Devices: Zmax, PSG, Empatica, ActivPAL; keys: Zmax, PSG, Emp, Activpal).
3. 'NumOfSignals': Number of signals recorded in 'SignalData'.
4. 'SignalLabel': List of signal names recorded by the device. Example: 'EEGL', 'EEGR', 'ACCX', etc..
5. 'SignalStartDateTime': Start date and time of each signal's recording (%Y-%m-%d %H:%M:%S). Usually the same for all signals of a device. For Zmax and Mentalab, the start times are unreliable.
6. 'SamplingRate': Sampling rate of each signal.
7. 'SignalDurationSec': Duration of each signal in seconds.
8. 'SignalLength': Length of each signal in data points.
9. 'SignalMin': Minimum value of signals associated signal.
10. 'SignalMax': Maximum value of signals associated signal.
11. 'SignalType': Signal modalities (e.g., EEG, EMG).
12. 'SignalUnit': Signal measurement unit.
13. 'SignalData': Actual recorded data for each signal.
14. 'SleepScoreEpochs': Number of 30-second epochs in associated sleep scores.
15. 'SleepScores': Available sleep scores identified from the associated device's data.

## Reference

Sikder, N., Verkaar, L., Paltarzhytskaya, A., Acan, S., Krugliakova, E., Rosenblum, Y., Krauledat, M., Dresler, M., & Zerr, P. (2025). *Wearanize+: A Multimodal Dataset for Evaluating Wearable Technologies in Sleep Research*. Center for Open Science. DOI: 10.31219/osf.io/dth8y_v1
