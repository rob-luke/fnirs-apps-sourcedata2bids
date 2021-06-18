# fNIRS App: Sourcedata to BIDS

[![build](https://github.com/rob-luke/fnirs-apps-sourcedata2bids/actions/workflows/ghregistry.yml/badge.svg)](https://github.com/rob-luke/fnirs-apps-sourcedata2bids/actions/workflows/ghregistry.yml)

Portable fNIRS neuroimaging pipelines that work with BIDS datasets. See http://fnirs-apps.org

This app will convert a directory of source files to a BIDS dataset.

**Feedback is welcome!!** Please let me know your experience by raising an issue above.  
I will help you get this working with your data.

The source data must be formatted using the BIDS directory structure in the `/sourcedata` directory,
see [here for an example of how to format the source data](https://github.com/rob-luke/BIDS-NIRS-Tapping/tree/00-Raw-data).
The app will then convert the data to BIDS format such that the resulting directory [looks like this example](https://github.com/rob-luke/BIDS-NIRS-Tapping/tree/master). See usage instructions below.


#### Current limitations

* Currently only works with NIRx files. However, MNE supports Hitachi, Imagent, Artinis datatypes too. So it will be trivial to extend to these files types.  See [#2](https://github.com/rob-luke/fnirs-apps-sourcedata2bids/issues/2)


## Usage

```bash
docker run -v /path/to/data/:/bids_dataset ghcr.io/rob-luke/fnirs-apps-sourcedata2bids/app --task_label="Example"
```

By default the app will process all subject and tasks.
You can modify the behaviour of the script using the options below.

The source data must be formatted according to the bids folder structure.
It must adhere to the following format.

```text
.
└── sourcedata
    ├── sub-01
    │   └── nirs
    │       └── 2020-01-01_001
    │           ├── NIRS-2020-01-01_001.dat
    │           ├── NIRS-2020-01-01_001.evt
    │           ├── ...
    |
    ├── sub-02
    │   └── nirs
    │       ├── 2020-01-02_002
    │       │   ├── NIRS-2020-01-02_002.dat
    │       │   ├── NIRS-2020-01-02_002.evt
    │       │   ├── ...
    |
    :
    └── sub-XX
        └── nirs
            └── 2020-01-05_005
                ├── NIRS-2020-01-05_005.dat
                ├── NIRS-2020-01-05_005.evt
                ├── ...
                └── NIRS-2020-01-05_005_probeInfo.mat

```


## Arguments

|                   | Required | Default | Note                                                   |
|-------------------|----------|---------|--------------------------------------------------------|
| task_label        | required |         | Task name to use for data.                             |
| events            | optional | 1       | Specifes the naming of different event triggers. i.e. converts a trigger number of 2 to the code "stimulus" and the code 1 to "control"                               |
| duration          | optional | 1       | Duration of stimulus.                                  |
| participant_label | optional | []      | Participants to process. Default is to process all.    |


### Events

To specify events you must pass in a dictionary specifying each code and associated name.
Annoyingly on some operating systems you need to add a backslash before the quotes.
So the command to convert trigger 1 to control, 2 to Tapping/Left, and 3 to Tapping/Right
would be.

```bash
---events="{\"1\":\"Control\", \"2\":\"Tapping/Left\", \"3\":\"Tapping/Right\"}"
```


### Complete example

```bash
docker run -v /path/to/data/:/bids_dataset ghcr.io/rob-luke/fnirs-apps-sourcedata2bids/app --task_label="ListeningTask" --duration=12.5 --events="{\"1\":\"Audio\", \"2\":\"Video\", \"3\":\"Control\"}"
```

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
