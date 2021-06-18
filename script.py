#!/usr/bin/env python3
import pandas as pd
import numpy as np
import mne
import mne_nirs
import os
import argparse
from mne_bids import BIDSPath, write_raw_bids, print_dir_tree
from mne_nirs.io.snirf import write_raw_snirf
from glob import glob
import os.path as op
import json

__version__ = "v0.0.1"


parser = argparse.ArgumentParser(description='Scalp coupling index')
parser.add_argument('--bids_dir', default="/bids_dataset", type=str,
                    help='The directory with the input dataset '
                    'formatted according to the BIDS standard.')
parser.add_argument('--events', type=json.loads,
                    help='Event labels.')
parser.add_argument('--duration', type=float, default=1.0,
                    help='Duration of stimulus.')
parser.add_argument('--participant_label',
                    help='The label(s) of the participant(s) that should be '
                    'analyzed. The label corresponds to '
                    'sub-<participant_label> from the BIDS spec (so it does '
                    'not include "sub-"). If this parameter is not provided '
                    'all subjects should be analyzed. Multiple participants '
                    'can be specified with a space separated list.',
                    nargs="+")
parser.add_argument('--task_label',
                    help='The label(s) of the tasks(s) that should be '
                    'analyzed. If this parameter is not provided '
                    'all tasks should be analyzed. Multiple tasks '
                    'can be specified with a space separated list.',
                    nargs="+")
parser.add_argument('-v', '--version', action='version',
                    version='BIDS-App Scalp Coupling Index version '
                    f'{__version__}')
args = parser.parse_args()


########################################
# Extract parameters
########################################

ids = []
if args.participant_label:
    ids = args.participant_label
else:
    subject_dirs = glob(op.join(args.bids_dir, "sourcedata/sub-*"))
    ids = [subject_dir.split("-")[-1] for
           subject_dir in subject_dirs]
    print(f"No participants specified, processing {ids}")


tasks = []
if args.task_label:
    tasks = args.task_label
else:
    raise ValueError(f"You must specify a task label")

events = []
if args.events:
    # Convert to int keys
    _events = args.events
    trial_type = dict()
    event_codes = dict()
    for event in _events:
        trial_type[int(event)] = _events[event]
        event_codes[str(float(event))] = int(event)
    print(f"You specified the events {trial_type}")
    print(f"Which has the corresponding codes {event_codes}")
else:
    raise ValueError(f"You must specify a task label")


########################################
# Main script
########################################

print(" ")
for id in ids:
    for task in tasks:
        b_path = BIDSPath(subject=id, task=task,
                          root="/bids_dataset/sourcedata",
                          datatype="nirs", suffix="nirs",
                          extension=".snirf")
        dname = str(b_path.directory)
        fname = dname + "/" + next(os.walk(dname))[1][0]
        print(f"Reading source directory: {fname}")
        raw = mne.io.read_raw_nirx(fname, preload=False)
        snirf_path = dname + "/" + b_path.basename + ".snirf"
        write_raw_snirf(raw, snirf_path)
        raw = mne.io.read_raw_snirf(snirf_path, preload=False)
        events, event_id = mne.events_from_annotations(raw, event_codes)
        raw.set_annotations(
            mne.annotations_from_events(events, raw.info['sfreq'],
                                        event_desc=trial_type))
        raw.annotations.duration = np.ones(raw.annotations.duration.shape) *\
                                   args.duration
        raw.info['line_freq'] = 50
        bids_path = BIDSPath(subject=id, task=task,
                             datatype='nirs', root='/bids_dataset')
        write_raw_bids(raw, bids_path, overwrite=True)
        os.remove(snirf_path)

# print_dir_tree("/bids_dataset")