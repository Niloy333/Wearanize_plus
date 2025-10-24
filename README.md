[![DOI](https://zenodo.org/badge/925334641.svg)](https://doi.org/10.5281/zenodo.14892764)

# Wearanize plus (*Wearanize+*)

**— A multimodal dataset with wearable-based overnight sleep recordings**

## Overview

The Wearanize+ dataset comprises overnight sleep recordings from 130 healthy participants (one night each) aged between 18 and 39 years (mean = 23.16 years, SD = 4.34; 89 females). Each participant’s sleep was recorded simultaneously using three wearable devices—a [Zmax EEG headband](https://hypnodynecorp.com/), an [Empatica E4 wristband](empatica.com/en-eu/research/e4/), and an [ActivPAL leg patch](https://kb.palt.com/articles/palpatch/)—alongside full polysomnography (PSG) using [SOMNOscreen plus](https://somnomedics.de/en/solutions/sleep_diagnostics/stationary_sleep_lab_psg/somnoscreen-plus/) or [Mentalab Explore Pro](https://mentalab.com/products/) (for a few participants). It also includes the responses to three widely used questionnaires—the Pittsburgh Sleep Quality Index (PSQI), the Mannheim Dream Questionnaire (MADRE), and the Patient Health Questionnaire (PHQ-9)—providing information on the participants' sleep, dreams, and overall health. The PSG data has been manually sleep-scored by an expert sleep scorer, and the scores are included in the dataset. For more details, see the [associated paper]((#reference-paper).

The dataset is the outcome of a research project bearing the same name, carried out at the [Trigon Building](https://www.ru.nl/en/about-us/the-campus/buildings-and-spaces/trigon) of the [Donders Centre for Cognitive Neuroimaging](https://www.ru.nl/en/departments/institutes/donders-centre-for-cognitive-neuroimaging), Radboud University (Nijmegen, The Netherlands). The study was conducted by members of [Donders Sleep & Memory Lab](https://dreslerlab.org/), in collaboration with Radboud University Medical Center (Nijmegen, The Netherlands) and Hochschule Rhein-Waal (Kleve, Germany), between October 2023 and August 2024.

For transparency and ease of use, the dataset has been released in two versions: [Wearanize+_Raw_v1.0](#wearanize+_raw_v1.0), which contains the raw, unfiltered data collected from participants, and [Wearanize+_PlugNPlay_v1.0](wearanize+_plugnplay_v1.0), which contains a curated, streamlined version after initial preprocessing of the raw data and manual synchronization of different wearables. See [Access Instructions](#access_instructions) for a step-by-step guide to obtaining access to the dataset. This repository contains the scripts used to preprocess, synchronize, and create the PlugNPlay version. See [Script Descriptions](#script_descriptions) for more details.

## Wearanize+_Raw_v1.0

## Wearanize+_PlugNPlay_v1.0

This repository contains scripts to preprocess the raw data and perform preliminary analysis on the Wearanize+ dataset v1.0.
For more details on the project, see [Wearanize+ Dataset v1.0 Publication](https://doi.org/10.31219/osf.io/dth8y_v3)

## Access Instructions

**Some recent changes in institutional policies have delayed the release of the dataset. Please be assured that we are actively working to publish it as soon as possible, while adhering to proper regulations and ensuring public access. We are amazed by the number of responses and requests we have received. As soon as things are settled on our end, we will outline the procedure for accessing the dataset on this page. In the meantime, we kindly request your patience.**

~~To access the data, please open an [ORCID account](https://orcid.org/) and follow [these instructions](https://data.ru.nl/doc/help/helppages/visitor-manual/vm-request-access.html?14=). Please see the [FAQ section](https://data.ru.nl/doc/help/helppages/faq.html?20=) to solve common issues.
The published dataset version is titled *Wearanize+_v1.0.zip*, and the synchronized version is titled *Wearanize+_PlugNPlay_v1.0.zip*. If you still have trouble accessing the dataset (or have questions), please contact Niloy Sikder at niloy.sikder@donders.ru.nl, mentioning your ORCID ID.~~

## Script Descriptions

## Dataset Contents (PlugNPlay)
**Column descriptions:**
1. 'SubjectID': Unique identifier for the subject.
2. 'Device': Name of the recording device. (Devices: Zmax, PSG, Empatica, ActivPAL; keys: Zmax, PSG, Emp, Activpal).
3. 'NumOfSignals': Number of signals recorded in 'SignalData'.
4. 'SignalLabel': List of signal names recorded by the device. Example: 'EEGL', 'EEGR', 'ACCX', etc..
5. 'SignalStartDateTime': Start date and time of each signal's recording (%Y-%m-%d %H:%M:%S). Usually, the same for all signals of a device. For Zmax and Mentalab, the start times are unreliable.
6. 'SamplingRate': Sampling rate of each signal.
7. 'SignalDurationSec': Duration of each signal in seconds.
8. 'SignalLength': Length of each signal in data points.
9. 'SignalMin': Minimum value of the associated signal.
10. 'SignalMax': Maximum value of the associated signal.
11. 'SignalType': Signal modalities (e.g., EEG, EMG).
12. 'SignalUnit': Signal measurement unit.
13. 'SignalData': Actual recorded data for each signal.
14. 'SleepScoreEpochs': Number of 30-second epochs in associated sleep scores.
15. 'SleepScores': Available sleep scores identified from the associated device's data.

## Reference Paper

Sikder, N., Verkaar, L., Paltarzhytskaya, A., Acan, S., Bovy, L., Almazova, T., Krugliakova, E., Rosenblum, Y., Krauledat, M., Dresler, M., & Zerr, P. (2025). ***Wearanize+*: A Multimodal Dataset for Evaluating Wearable Technologies in Sleep Research**. Center for Open Science. https://doi.org/10.31219/osf.io/dth8y_v3

If you use the dataset or the associated scripts in your work, please cite the reference paper using the **DOI: 10.31219/osf.io/dth8y_v3** and the package using the **DOI: 10.5281/zenodo.14892764**.

## Ethical Statements
This study was conducted in accordance with the Donders Centre for Cognitive Neuroimaging (DCCN) blanket approval, protocol ‘Imaging Human Cognition’ (NL45659.091.14), approved by METC Oost-Nederland (2014/288).

## Funding
This work was supported by the Swiss National Science Foundation (SNF), a Vici Fellowship from the Dutch Research Council (NWO), and the European Union’s Horizon Europe Programme (HORIZON-MSCA-2021-PF-01-01) through a Marie Skłodowska-Curie Postdoctoral Fellowship (Grant No. 101066123, GlymphoSleep).

## People
**Principal investigator**: [Martin Dresler](https://scholar.google.com/citations?hl=en&user=Y-hAEQYAAAAJ&view_op=list_works&sortby=pubdate)<br>
**Data collection**: [Niloy Sikder](https://scholar.google.com/citations?hl=en&user=0ALk5j4AAAAJ&view_op=list_works&sortby=pubdate), Lieuwe Verkaar, [Anastasiya Paltarzhytskaya](https://scholar.google.com/citations?user=Tso2IDgAAAAJ&hl=en), Selin Acan, [Elena Krugliakova](https://scholar.google.com/citations?hl=en&user=fT12wToAAAAJ&view_op=list_works&sortby=pubdate)<br>
**Sleep-scoring**: [Leonore Bovy](https://scholar.google.com/citations?hl=en&user=ucXKHGsAAAAJ&view_op=list_works&sortby=pubdate)<br>
**Data preparation**: Niloy Sikder<br>
**Supervision**: [Matthias Krauledat](https://scholar.google.com/citations?hl=en&user=n9q-wxgAAAAJ&view_op=list_works&sortby=pubdate), [Yevgenia Rosenblum](https://scholar.google.com/citations?hl=en&user=9pl_iyMAAAAJ&view_op=list_works&sortby=pubdate), [Paul Zerr](https://scholar.google.com/citations?hl=en&user=9CldqFoAAAAJ&view_op=list_works&sortby=pubdate)

**For questions, comments, queries regarding data access, and interest in collaboration, please [contact Martin Dresler](mailto:martin.dresler@donders.ru.nl).**

