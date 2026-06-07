[![Dataset DOI](https://img.shields.io/badge/Dataset%20DOI-10.34973%2Fj6jf--9e62-blue)](https://doi.org/10.34973/j6jf-9e62)
[![Paper DOI](https://img.shields.io/badge/Paper_DOI-10.1093/sleepadvances/zpaf094-blue)](https://doi.org/10.1093/sleepadvances/zpaf094)
[![Repository DOI](https://img.shields.io/badge/Repository_DOI-10.5281%2Fzenodo.14892764-blue)](https://doi.org/10.5281/zenodo.14892764)
<!-- [![DOI](https://zenodo.org/badge/925334641.svg)](https://doi.org/10.5281/zenodo.14892764)-->
![Repo size](https://img.shields.io/github/repo-size/Niloy333/Wearanize_plus)
![Last commit](https://img.shields.io/github/last-commit/Niloy333/Wearanize_plus)
<!--[![Repository size](https://img.shields.io/github/repo-size/Niloy333/Wearanize_plus?cacheSeconds=3600)](https://github.com/Niloy333/Wearanize_plus)
[![Last commit](https://img.shields.io/github/last-commit/Niloy333/Wearanize_plus?cacheSeconds=3600)](https://github.com/Niloy333/Wearanize_plus/commits) -->

# Wearanize plus (*Wearanize+*)

**—A multimodal dataset with wearable-based overnight sleep recordings**

Table of Contents: [Overview](#overview) | [Access Instructions](#access-instructions) | [Devices and Modalities](#devices-and-modalities) | [Dataset Versions](#dataset-versions) | [Script Descriptions](#script-descriptions) | [PlugNPlay Channel Descriptions](#plugnplay-channel-descriptions) | [Ethical Statements](#ethical-statements) | [Funding](#funding) | [Reference Paper](#reference-paper) | [Citation](#citation) | [People](#people)

## Overview

The Wearanize+ dataset comprises overnight sleep recordings from 130 healthy participants (one night each) aged between 18 and 39 years (mean = 23.16 years; SD = 4.34; 89F & 41M). Each participant's sleep was recorded simultaneously using three wearable devices—a [*Zmax* EEG headband](https://hypnodynecorp.com/), an [*Empatica E4* wristband](https://empatica.com/en-eu/research/e4/), and an [*ActivPAL* leg patch](https://kb.palt.com/articles/palpatch/)—alongside full polysomnography (PSG) using [*SOMNOscreen plus*](https://somnomedics.de/en/solutions/sleep_diagnostics/stationary_sleep_lab_psg/somnoscreen-plus/) or [*Mentalab Explore Pro*](https://mentalab.com/products/) (for a few participants). It also includes the responses to three widely used questionnaires—the *Pittsburgh Sleep Quality Index* (PSQI), the *Mannheim Dream Questionnaire* (MADRE), and the *Patient Health Questionnaire* (PHQ-9)—providing information on the participants' sleep, dreams, and overall health. The PSG data has been manually sleep-scored by an expert sleep scorer and automatically sleep-scored by [*USleep v2.0*](https://sleep.ai.ku.dk/). Both sets of scores are included in the dataset. For more details, see the [reference paper](#reference-paper). 

See [Access Instructions](#access-instructions) for a step-by-step guide to obtaining access to the dataset. This repository also contains the scripts used to preprocess, synchronize, and prepare the dataset. See [Script Descriptions](#script-descriptions) for more details.

The dataset is the outcome of a research project bearing the same name, carried out at the [Trigon Building](https://www.ru.nl/en/about-us/the-campus/buildings-and-spaces/trigon) of the [Donders Centre for Cognitive Neuroimaging](https://www.ru.nl/en/departments/institutes/donders-centre-for-cognitive-neuroimaging), Radboud University (Nijmegen, The Netherlands). The study was conducted by members of [Donders Sleep & Memory Lab](https://dreslerlab.org/), in collaboration with Radboud University Medical Center (Radboudumc, Nijmegen, The Netherlands) and Hochschule Rhein-Waal (Kleve, Germany), between October 2023 and August 2024.

The dataset can facilitate a range of applications, including device-specific validations of the three wearables, development of (device-specific) automatic sleep-stage scorers (autoscorers) based on the provided PSG-based sleep scores, methods for handling missing or corrupted data, and evaluation of alternative (as well as compound) sensor modalities for sleep scoring. It has already been used for developing Zmax-based autoscorers, such as [*ezscore*](https://github.com/coonwg1/ezscore) and [*u-sleep-w*](https://github.com/alitsaberi/zmax-datasets), and validating [an automatic Zmax–Somnoscreen synchronization method](https://github.com/Niloy333/Wearanize_plus/blob/base/automatic_synchronization/Zmax-Somnoscreen_auto_sync.m). One of our key objectives behind creating this dataset is to leverage these multimodal recordings to build robust, multi-wearable sleep-scoring models that approach PSG-grade performance while minimizing the impact of EEG artifacts.

## Access Instructions

The Wearanize+ dataset is hosted on the <i>Radboud Data Repository</i> (RDR) and is available for research use upon signing a <i>Data Use Agreement</i> (DUA). To request access:

- Download the DUA template: for countries [in the European Economic Area (EEA)](https://github.com/Niloy333/Wearanize_plus/raw/refs/heads/base/DUA_forms/Wearanize+_Radboudumc_DUA_v2.0.docx), [outside the EEA](https://github.com/Niloy333/Wearanize_plus/blob/base/DUA_forms/DTA_Wearanize_nonEU_v1.docx).
- Complete the recipient information section and clearly describe your research plan.
- Send the completed form to [Dr. Martin Dresler](https://www.radboudumc.nl/en/people/martin-dresler) via [email](mailto:martin.dresler@donders.ru.nl).
- Create an [ORCID account](https://orcid.org/) using the same email address you provided in the DUA. If you use an existing ORCID account, please include the intended email address and make it visible.
- Visit the [Wearanize+ collection](https://data.ru.nl/collections/di/dcmn/DSC_wearanize_t0000657a_579).
- Log in to RDR via ORCID.
- Click “Request access” to the collection.

This registers your credentials in RDR and makes it easier to grant access once the DUA has been approved by Radboudumc. If multiple researchers need access under the same DUA, each person should submit an access request in RDR using their own ORCID account following the same procedure.

> [!IMPORTANT]
> **We are currently working on releasing an open-access version of the Wearanize+ dataset, containing all physiological data (excluding the questionnaires), which will be available to users without a formal DUA. Please stay tuned for updates.**

## Devices and Modalities

The following image shows the positions of the mentioned devices and their recording modalities. <br>
**Recordings from the experimental devices are not a part of the dataset.**

<img src="https://github.com/Niloy333/Wearanize_plus/blob/base/figures/Figure%202.jpg" alt="device modalities" width="500">

## Dataset Versions

For transparency and ease of use, the dataset has been released in two versions: [Wearanize+ Raw v1.0](#wearanize-raw-v10) and [Wearanize+ PlugNPlay v1.0](#wearanize-plugnplay-v10). PlugNPlay would be the ideal version for most projects, while the Raw version allows tracing back to the original data and may provide the opportunity for further analysis. Here are the differences in their contents:

### *Wearanize+ Raw v1.0*

This version/file contains the raw, unfiltered data collected from the participants of the project. See the "Wearanize+ raw dataset" section and Appendix 2 of the [reference paper](#reference-paper) for more details.

### *Wearanize+ PlugNPlay v1.0*

This version/file contains a processed, synchronized, and truncated version of the raw data. To streamline usability and avoid repeating the extensive preprocessing steps, data for each participant was consolidated into a single file and stored in European Data Format (EDF), preserving all metadata and signal properties. PSG-based Manual and automatic sleep scores were also integrated into the EDF files as 'PSG_Manual_score' and 'PSG_USleep_score' at a sampling rate of 1/30 Hz. Time-series signals were labeled according to the convention *[device_ID]_[channel_name]* and stored with the Float32 datatype (if they are read in Float64, convert them back to Float32 to save space). The PlugNPlay version includes data from 100 participants (out of the total 130) for whom both PSG and Zmax data were available, and manual sleep scoring could be performed.

In most cases, the channel names were kept consistent with the names provided by the associated device. However, they were sometimes modified for clarity or broader compatibility. See [PlugNPlay Channel Descriptions](#plugnplay-channel-descriptions) or the subject-wise *sub-nnn_task-sleep_channels.tsv* files for detailed information on specific channels. *[device_name]_[channel_a]:[channel_b]* indicates that *channel_a* was referenced to *channel_b*.

Since EDF is a widely used format in Neuroscience, the data should be readable across different platforms and environments. The PlugNPlay version has been formatted according to the *EEG-Brain Imaging Data Structure* ([EEG-BIDS v1.10.0](https://bids-specification.readthedocs.io/en/v1.10.0/)) specifications. The usability of the EEG signals has been checked with [*eegFloss*](https://github.com/Niloy333/eegFloss), and the outputs have been added to the corresponding file. See the "Wearanize+ PlugNPlay" section of the [reference paper](#reference-paper) for more details.

> [!IMPORTANT]
> **Please note that PSG data for Sub115, Sub124, Sub129, and Sub130 were collected with Mentalab, and their channel names differ from those collected with Somnoscreen (used for all other participants). See [PlugNPlay Channel Descriptions](#plugnplay-channel-descriptions) for the exact channel mappings.**

## Script Descriptions

### `read_PlugNPlay_EDF.py`

- Provides example code to read individual EDF files and extract information from multiple EDF files of the PlugNPlay version using Python.
- Note: Storing raw signals from all EDF files simultaneously requires substantial memory.

### `read_PlugNPlay_EDF.m`

- Provides example code to read individual EDF files and extract information from multiple EDF files of the PlugNPlay version using MATLAB.
- Note: Storing raw signals from all EDF files simultaneously requires substantial memory.

### `PlugNPlay_preparation//create_PlugNPlay_parquet.py`

- Contains the codes used to create the PlugNPlay version from the raw version of the dataset.
- The PlugNPlay version was first generated in Parquet format, storing data as Pandas DataFrames for efficient processing.
- The Parquet files are also available in the data repository as *Wearanize+_PlugNPlay_Parquet_v1.0.zip*. If needed, they can serve as alternatives to the EDF files in *Wearanize+_PlugNPlay_v1.0.zip*. More information and usage instructions of these files are available in `extra_scripts//read_PlugNPlay.py` and `extra_scripts//read_PlugNPlay.m`.

### `PlugNPlay_preparation//parquet_to_EDF.py`

- Contains the scripts used to convert the Parquet files into EDF format while preserving all relevant signal information and metadata.

### `EEG-BIDS_preparation//BIDS_derivative.py`

- Prepares the EEG-BIDS–compatible derivative dataset containing global metadata and structure definitions.

### `EEG-BIDS_preparation//BIDS_info_1.py`

- Prepares the EEG-BIDS–compatible dataset with local (file-specific) metadata and participant-level information.

### `automatic_synchronization//Zmax-Somnoscreen_auto_sync.m`

- Provides MATLAB code to automatically synchronize simultaneously recorded overnight sleep data using the Zmax headband and SOMNOscreen plus PSG devices.
- To apply this script to new data, organize the input files (Zmax recording, SOMNOscreen plus recording, and Lights Out/Lights On moments from Zmax) in the same structure as in **Wearanize+ Raw v1.0**, and update the input–output directories at the beginning of the script.
- See Appendix 1 of the [reference paper](#reference-paper) for more details.

### `manual_synchronization//Zmax-Somnoscreen_manual_sync.m`

- Contains MATLAB code for manual/visual synchronization of Zmax and SOMNOscreen plus recordings based on their respective accelerometer and movement signals.
- See the "Synchronization" section of the [reference paper](#reference-paper) for more details.

### `manual_synchronization//Zmax-Empatica-Activpal_manual_sync.m`

- Contains MATLAB code for manual/visual synchronization of Zmax recordings with Empatica E4 and ActivPAL data, based on their respective accelerometer outputs.


## PlugNPlay Channel Descriptions

| Channel Name | Description<sup>$</sup> | Unit | Device | Sampling<br>Frequency (Hz) |
|---|---|---:|---|---|
| ActivPal_ACCX | Accelerometer X axis | ⓖ | ActivPAL | 20 |
| ActivPal_ACCY | Accelerometer Y axis | ⓖ | ActivPAL | 20 |
| ActivPal_ACCZ | Accelerometer Z axis | ⓖ | ActivPAL | 20 |
| Emp_ACCX | Accelerometer X axis | ⓖ/64&#8205;<sup>⚠️</sup>  | Empatica E4 | 32 |
| Emp_ACCY | Accelerometer Y axis | ⓖ/64&#8205;<sup>⚠️</sup>  | Empatica E4 | 32 |
| Emp_ACCZ | Accelerometer Z axis | ⓖ/64&#8205;<sup>⚠️</sup> | Empatica E4 | 32 |
| Emp_BVP | PPG | Unitless | Empatica E4 | 64 |
| Emp_EDA | Electrodermal activity | μS | Empatica E4 | 4 |
| Emp_HR | Mean heart rate derived from BVP | bpm | Empatica E4 | 1 |
| Emp_TEMP | Skin temperature | °C | Empatica E4 | 4 |
| PSG_A1 | EEG channel A1 | µV | SOMNOscreen | 256 |
| PSG_A2 | EEG channel A2 | µV | SOMNOscreen | 256 |
| PSG_ACCX | Accelerometer X axis | mⓖ | Mentalab | 20 |
| PSG_ACCY | Accelerometer Y axis | mⓖ | Mentalab | 20 |
| PSG_ACCZ | Accelerometer Z axis | mⓖ | Mentalab | 20 |
| PSG_C3 | EEG channel C3 | µV | SOMNOscreen,<br>Mentalab | 256,<br>250 |
| PSG_C3:A2 | EEG channel C3 referenced to A2 | µV | SOMNOscreen | 256 |
| PSG_C4 | EEG channel C4 | µV | SOMNOscreen,<br>Mentalab | 256,<br>250 |
| PSG_C4:A1 | EEG channel C4 referenced to A1 | µV | SOMNOscreen | 256 |
| PSG_CP1 | EEG channel CP1 | µV | Mentalab | 250 |
| PSG_CP2 | EEG channel CP2 | µV | Mentalab | 250 |
| PSG_CP5 | EEG channel CP5 | µV | Mentalab | 250 |
| PSG_CP6 | EEG channel CP6 | µV | Mentalab | 250 |
| PSG_Cz | EEG channel Cz | µV | Mentalab | 250 |
| PSG_ECG 2 | ECG channel 2 | µV | SOMNOscreen | 256 |
| PSG_ECG1 | ECG channel 1 | µV | Mentalab | 250 |
| PSG_ECG2 | ECG channel 2 | µV | Mentalab | 250 |
| PSG_EMG | EMG channel reference | µV | SOMNOscreen | 256 |
| PSG_EMG_minus | EMG channel 1 | µV | SOMNOscreen | 256 |
| PSG_EMG_plus | EMG channel 2 | µV | SOMNOscreen | 256 |
| PSG_EMG1 | EMG channel 1 | µV | Mentalab | 250 |
| PSG_EMG2 | EMG channel 2 | µV | Mentalab | 250 |
| PSG_EOG1 | EOG channel 1 | µV | SOMNOscreen,<br>Mentalab | 256,<br>250 |
| PSG_EOG1:A1 | EOG channel 1 referenced to A1 | µV | SOMNOscreen | 256 |
| PSG_EOG1:A2 | EOG channel 1 referenced to A2 | µV | SOMNOscreen | 256 |
| PSG_EOG2 | EOG channel 2 | µV | SOMNOscreen,<br>Mentalab | 256,<br>250 |
| PSG_EOG2:A1 | EOG channel 2 referenced to A1 | µV | SOMNOscreen | 256 |
| PSG_EOG2:A2 | EOG channel 2 referenced to A2 | µV | SOMNOscreen | 256 |
| PSG_F3 | EEG channel F3 | µV | SOMNOscreen | 256 |
| PSG_F3:A2 | EEG channel F3 referenced to A2 | µV | SOMNOscreen | 256 |
| PSG_F4 | EEG channel F4 | µV | SOMNOscreen | 256 |
| PSG_F4:A1 | EEG channel F4 referenced to A1 | µV | SOMNOscreen | 256 |
| PSG_F7 | EEG channel F7 | µV | Mentalab | 250 |
| PSG_F8 | EEG channel F8 | µV | Mentalab | 250 |
| PSG_FC1 | EEG channel FC1 | µV | Mentalab | 250 |
| PSG_FC2 | EEG channel FC2 | µV | Mentalab | 250 |
| PSG_FC5 | EEG channel FC5 | µV | Mentalab | 250 |
| PSG_FC6 | EEG channel FC6 | µV | Mentalab | 250 |
| PSG_FCz | EEG channel FCz | µV | Mentalab | 250 |
| PSG_FT10 | EEG channel FT10 | µV | Mentalab | 250 |
| PSG_FT9 | EEG channel FT9 | µV | Mentalab | 250 |
| PSG_GYRX | Gyroscope X axis | mdps | Mentalab | 20 |
| PSG_GYRY | Gyroscope Y axis | mdps | Mentalab | 20 |
| PSG_GYRZ | Gyroscope Z axis | mdps | Mentalab | 20 |
| PSG_MAGX | Magnetometer X axis | µT | Mentalab | 20 |
| PSG_MAGY | Magnetometer Y axis | µT | Mentalab | 20 |
| PSG_MAGZ | Magnetometer Z axis | µT | Mentalab | 20 |
| PSG_Move. | Movement info | mⓖ | SOMNOscreen | 4 |
| PSG_O1 | EEG channel O1 | µV | SOMNOscreen,<br>Mentalab | 256,<br>250 |
| PSG_O1:A2 | EEG channel O1 referenced to A2 | µV | SOMNOscreen | 256 |
| PSG_O2 | EEG channel O2 | µV | SOMNOscreen,<br>Mentalab | 256,<br>250 |
| PSG_O2:A1 | EEG channel O2 referenced to A1 | µV | SOMNOscreen | 256 |
| PSG_Oz | EEG channel Oz | µV | Mentalab | 250 |
| PSG_P3 | EEG channel P3 | µV | Mentalab | 250 |
| PSG_P4 | EEG channel P4 | µV | Mentalab | 250 |
| PSG_P7 | EEG channel P7 | µV | Mentalab | 250 |
| PSG_P8 | EEG channel P8 | µV | Mentalab | 250 |
| PSG_Pos. | Body position info<sup>ⓟ</sup> | Unitless | SOMNOscreen | 4 |
| PSG_Pz | EEG channel Pz | µV | Mentalab | 250 |
| PSG_T7 | EEG channel T7 | µV | Mentalab | 250 |
| PSG_T8 | EEG channel T8 | µV | Mentalab | 250 |
| PSG_Manual_score | Manually-identified sleep scores<sup>ⓢ</sup> from PSG data | Unitless | N/A | 1/30 |
| PSG_USleep_score | Automatic sleep scores<sup>ⓢ</sup> identified by Usleep v2.0 | Unitless | N/A | 1/30 |
| Zmax_ACCX | Accelerometer X axis | ⓖ | Zmax | 256 |
| Zmax_ACCY | Accelerometer Y axis | ⓖ | Zmax | 256 |
| Zmax_ACCZ | Accelerometer Z axis | ⓖ | Zmax | 256 |
| Zmax_EEGL | Forehead EEG Left channel | µV | Zmax | 256 |
| Zmax_EEGR | Forehead EEG Right channel | µV | Zmax | 256 |
| Zmax_NOISE | Noise channel | Unitless | Zmax | 256 |
| Zmax_OXY_IR_AC | Forehead PPG | Unitless | Zmax | 256 |
| Zmax_OXY_IR_DC | Oximetry IR DC component | Unitless | Zmax | 256 |

> <sup>$</sup>Electrode placement: SOMNOscreen: [10–20 system](https://en.wikipedia.org/wiki/10%E2%80%9320_system_(EEG)), Mentalab: [10–10 system](https://en.wikipedia.org/wiki/10%E2%80%9320_system_(EEG)#/media/File:EEG_10-10_system_with_additional_information.svg).<br>
ⓖ: Gravity (m/s<sup>2</sup>).<br>
<sup>ⓟ</sup>Labels: 1: Prone, 2: Upright, 3: Left, 4: Right, 5: Upright (head), 6: Supine.<br>
<sup>ⓢ</sup>Labels: -1: Unscorable, 0: Wake, 1: N1, 2: N2, 3: N3, 4: REM.<br>
<sup>⚠️</sup>**Files in the dataset state this unit as ⓖ/16. However, the actual unit is ⓖ/64 (same as the source).**

## Ethical Statements

This study was conducted in accordance with the Donders Centre for Cognitive Neuroimaging (DCCN) blanket approval, protocol ‘Imaging Human Cognition’ (NL45659.091.14), approved by METC Oost-Nederland (2014/288).

## Funding

This work was supported by the Swiss National Science Foundation (SNF), a Vici Fellowship from the Dutch Research Council (NWO), and the European Union’s Horizon Europe Programme (HORIZON-MSCA-2021-PF-01-01) through a Marie Skłodowska-Curie Postdoctoral Fellowship (Grant No. 101066123, GlymphoSleep).

## Reference Paper

Sikder, N., Verkaar, L., Paltarzhytskaya, A., Acan, S., Bovy, L., Almazova, T., Krugliakova, E., Rosenblum, Y., Krauledat, M., Dresler, M., & Zerr, P. (2025). Wearanize+: a multimodal dataset for evaluating wearable technologies in sleep research. SLEEP Advances, 7(1). https://doi.org/10.1093/sleepadvances/zpaf094

## Citation

If you use the Wearanize+ dataset, please cite the reference paper as:

```bibtex
@article{sikder2025wearanize+,
  title    = {Wearanize+: A multimodal dataset for evaluating wearable technologies in sleep research},
  author   = {Sikder, Niloy and Verkaar, Lieuwe and Paltarzhytskaya, Anastasiya and Acan, Selin and Bovy, Leonore and Almazova, Tatiana and Krugliakova, Elena and Rosenblum, Yevgenia and Krauledat, Matthias and Dresler, Martin and others},
  journal  = {SLEEP Advances},
  pages    = {1-15},
  year     = {2025},
  publisher= {Oxford University Press},
  doi      = {10.1093/sleepadvances/zpaf094},
  url      = {https://academic.oup.com/sleepadvances/article/7/1/zpaf094/8405700}
}
```

and the dataset as:

```bibtex
@dataset{niloy_sikder_2025_wearanize_a_multim,
  author    = {Sikder, N.S. and Verkaar, Lieuwe and Paltarzhytskaya, A. (Anastasiya) and Acan, S. (Selin) and Bovy, L. and Tatiana Almazova and Krugliakova, E. (Elena) and Rozenblum, Y.R. and Krauledat, M. and Dresler, M. and Zerr, P.},
  title     = {{Wearanize+: A multimodal dataset (N=130) with wearable-based at-home overnight sleep recordings}},
  year      = {2025},
  publisher = {Radboud University},
  version   = {1},
  doi       = {10.34973/j6jf-9e62},
  url       = {https://doi.org/10.34973/j6jf-9e62}
}
```

If you use the provided scripts, please cite the GitHub repository as:

```bibtex
@software{sikder2025wearanizeplus,
  author    = {Sikder, Niloy},
  title     = {Wearanize_plus},
  year      = {2025},
  publisher = {Zenodo},
  doi       = {10.5281/zenodo.14892764},
  url       = {https://doi.org/10.5281/zenodo.14892764},
}
```

## People

**Principal investigator**: [Martin Dresler](https://scholar.google.com/citations?hl=en&user=Y-hAEQYAAAAJ&view_op=list_works&sortby=pubdate)<br>
**Data collection**: [Niloy Sikder](https://scholar.google.com/citations?hl=en&user=0ALk5j4AAAAJ&view_op=list_works&sortby=pubdate), Lieuwe Verkaar, [Anastasiya Paltarzhytskaya](https://scholar.google.com/citations?user=Tso2IDgAAAAJ&hl=en), Selin Acan, [Elena Krugliakova](https://scholar.google.com/citations?hl=en&user=fT12wToAAAAJ&view_op=list_works&sortby=pubdate)<br>
**Sleep-scoring**: [Leonore Bovy](https://scholar.google.com/citations?hl=en&user=ucXKHGsAAAAJ&view_op=list_works&sortby=pubdate)<br>
**Data preparation**: Niloy Sikder<br>
**Supervision**: [Matthias Krauledat](https://scholar.google.com/citations?hl=en&user=n9q-wxgAAAAJ&view_op=list_works&sortby=pubdate), [Paul Zerr](https://scholar.google.com/citations?hl=en&user=9CldqFoAAAAJ&view_op=list_works&sortby=pubdate), [Yevgenia Rosenblum](https://scholar.google.com/citations?hl=en&user=9pl_iyMAAAAJ&view_op=list_works&sortby=pubdate)

**For questions, comments, queries regarding data access, or interest in collaboration, please [contact Martin Dresler](mailto:martin.dresler@donders.ru.nl).**
