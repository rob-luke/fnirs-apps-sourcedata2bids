# fNIRS App: Sourcedata to BIDS

[![build](https://github.com/rob-luke/fnirs-apps-sourcedata2bids/actions/workflows/ghregistry.yml/badge.svg)](https://github.com/rob-luke/fnirs-apps-sourcedata2bids/actions/workflows/ghregistry.yml)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.4999341.svg)](https://doi.org/10.5281/zenodo.4999341)


This [*fNIRS App*](http://fnirs-apps.org) will convert a directory of fNIRS files to a correctly fomatted BIDS dataset.

To use this app the original measurement files (source data) must be organised according to the file structure specified below.
The app will then convert the raw data to a BIDS dataset, including conversion to SNIRF and creation of all metadata files.

#### Current limitations

* Only works with NIRx files. However due to support in MNE, it will be trivial to extend to Hitachi, Imagent, Artinis datatypes too.

**Feedback is welcome!!** Please let me know your experience with this app by raising an issue.  


## Usage

To run the app you must have [docker installed](https://docs.docker.com/get-docker/). See here for details about [installing fNIRS Apps](http://fnirs-apps.org/overview//). You do NOT need to have MATLAB or python installed, and you do not need any scripts. See this [tutorial for an introduction to fNIRS Apps](http://fnirs-apps.org/tutorial/).

To run the app you must inform it where the `bids_dataset` to be formatted resides.
This is done by passing the location of the dataset using the `-v` command to the app.
You must also specify the task label you wish to use.
A minimal example of how to run this app is:

```bash
docker run -v /data/path/:/bids_dataset ghcr.io/rob-luke/fnirs-apps-sourcedata2bids/app --task-label exampletask
```

You can also specify additional parameters by passing arguments to the app. A complete list of arguments is provided below.
A more complete example that also specifies the event duration and names is:

```bash
docker run -v /path/to/data/:/bids_dataset ghcr.io/rob-luke/fnirs-apps-sourcedata2bids/app \
    --task-label audiovisual \
    --duration 12.5 \
    --events "{\"1\":\"Audio\", \"2\":\"Video\", \"3\":\"Control\"}"
```

#### Source data organisation

The source data must be organised in a specific structure to use this app.
The data must reside within a `sourcedata` subdirectory at the top level of the `bids_dataset` directory.
A schematic of the required structure is shown below.
You can also view an [example source dataset that is ready for conversion here](https://github.com/rob-luke/BIDS-NIRS-Tapping/tree/00-Raw-data).


```text
.
└── sourcedata
    ├── sub-01
    │   └── nirs
    │       └── 2020-01-01_001     (the naming of this directory and included files is optional)
    │           ├── NIRS-2020-01-01_001.dat
    │           ├── NIRS-2020-01-01_001.evt
    │           ├── ...
    │
    ├── sub-02
    │   └── nirs
    │       └── 2020-01-02_002     (use the vendor exported format for these directories)
    │           ├── NIRS-2020-01-02_002.dat
    │           ├── NIRS-2020-01-02_002.evt
    │           ├── ...
    :
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
| task-label        | required |         | Task name to use for data.                             |
| events            | optional | []      | Specifes the naming of different event triggers. i.e. converts a trigger number of 2 to the code "stimulus" and the code 1 to "control"                               |
| duration          | optional | 1       | Duration of stimulus.                                  |
| subject-label     | optional | []      | Subjects to process. Default is to process all.        |


### Events

To specify events you must pass in a dictionary specifying each code and associated name.
Annoyingly on some operating systems you need to add a backslash before the quotes.
So the command to convert trigger 1 to control, 2 to Tapping/Left, and 3 to Tapping/Right
would be.

```bash
--events "{\"1\":\"Control\", \"2\":\"Tapping/Left\", \"3\":\"Tapping/Right\"}"
```


## Updating and running specific versions

To update to the latest version run.

```bash
docker pull ghcr.io/rob-luke/fnirs-apps-sourcedata2bids/app
```

Or to run a specific version:

```bash
docker run -v /path/:/bids_dataset ghcr.io/rob-luke/fnirs-apps-sourcedata2bids/app:v1.4.2
```

## Additional information

#### Boutiques

This app is [boutiques compatible](https://boutiques.github.io).
In addition to the methods described above, this app can also be run using [boutiques bosh command](https://boutiques.github.io/doc/index.html).


Acknowledgements
----------------

This app is directly based on BIDS Apps and BIDS Execution. Please cite those projects when using this app.

BIDS Apps: https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1005209

BIDS Execution: https://github.com/bids-standard/bids-specification/issues/313

This app uses MNE-Python, MNE-BIDS, and MNE-NIRS under the hood. Please cite those package accordingly.

MNE-Python: https://mne.tools/dev/overview/cite.html

MNE-BIDS: https://github.com/mne-tools/mne-bids#citing

MNE-NIRS: https://github.com/mne-tools/mne-nirs#acknowledgements
