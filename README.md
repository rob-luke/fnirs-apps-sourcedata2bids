# fNIRS App: Sourcedata to BIDS

[![build](https://github.com/rob-luke/fnirs-apps-sourcedata2bids/actions/workflows/ghregistry.yml/badge.svg)](https://github.com/rob-luke/fnirs-apps-sourcedata2bids/actions/workflows/ghregistry.yml)

Portable fNIRS neuroimaging pipelines that work with BIDS datasets. See http://fnirs-apps.org

This app will convert a directory of source files to a BIDS dataset.
The source data must be formatted using BIDS directory structure in the `/sourcedata` directory,
see [here for an example of how to format the source data](https://github.com/rob-luke/BIDS-NIRS-Tapping/tree/00-Raw-data).
The app will then convert the data to BIDS format such that the resulting directory [looks like this example](https://github.com/rob-luke/BIDS-NIRS-Tapping/tree/master).


## Usage

```bash
docker run -v /path/to/data/:/bids_dataset ghcr.io/rob-luke/fnirs-apps-sourcedata2bids/app
```

By default the app will process all subject and tasks.
You can modify the behaviour of the script using the options below.


## Arguments

|                   | Required | Default | Note                                                   |
|-------------------|----------|---------|--------------------------------------------------------|
| task_label        | required |         | Task name to use for data.                             |
| participant_label | optional | []      | Participants to process. Default is to process all.    |
| duration          | optional | 1       | Duration of stimulus.                                  |



## Updating

To update to the latest version run.

```bash
docker pull ghcr.io/rob-luke/fnirs-apps-sourcedata2bids/app
```


Acknowledgements
----------------

This package uses MNE-Python, MNE-BIDS, and MNE-NIRS under the hood. Please cite those package accordingly.

MNE-Python: https://mne.tools/dev/overview/cite.html

MNE-BIDS: https://github.com/mne-tools/mne-bids#citing

MNE-NIRS: https://github.com/mne-tools/mne-nirs#acknowledgements
