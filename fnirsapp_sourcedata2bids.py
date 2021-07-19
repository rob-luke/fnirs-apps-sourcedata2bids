#!/usr/bin/env python3
import pandas as pd
import numpy as np
import mne
import mne_nirs
import os
import argparse
from mne_bids import BIDSPath, write_raw_bids, print_dir_tree, get_entity_vals
from mne_nirs.io.snirf import write_raw_snirf
from mne.utils import logger
from glob import glob
import os.path as op
import json
import subprocess

__version__ = "v0.2.1"


def fnirsapp_sourcedata2bids(command, env={}):
    merged_env = os.environ
    merged_env.update(env)
    process = subprocess.Popen(command, stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT, shell=True,
                               env=merged_env)
    while True:
        line = process.stdout.readline()
        line = str(line, 'utf-8')[:-1]
        print(line)
        if line == '' and process.poll() != None:
            break
    if process.returncode != 0:
        raise Exception("Non zero return code: %d" % process.returncode)


parser = argparse.ArgumentParser(description='Scalp coupling index')
parser.add_argument('--input-datasets', default="/bids_dataset", type=str,
                    help='The directory with the input dataset '
                    'formatted according to the BIDS standard.')
parser.add_argument('--events', type=json.loads,
                    help='Event labels.')
parser.add_argument('--duration', type=float, default=1.0,
                    help='Duration of stimulus.')
parser.add_argument('--subject-label',
                    help='The label(s) of the participant(s) that should be '
                    'analyzed. The label corresponds to '
                    'sub-<subject-label> from the BIDS spec (so it does '
                    'not include "sub-"). If this parameter is not provided '
                    'all subjects should be analyzed. Multiple participants '
                    'can be specified with a space separated list.',
                    nargs="+")
parser.add_argument('--session-label',
                    help='The label(s) of the session(s) that should be '
                    'analyzed. The label corresponds to '
                    'ses-<session-label> from the BIDS spec (so it does '
                    'not include "ses-"). If this parameter is not provided '
                    'all sessions should be analyzed. Multiple sessions '
                    'can be specified with a space separated list.',
                    nargs="+")
parser.add_argument('--task-label',
                    help='The label(s) of the tasks(s) that should be '
                    'analyzed. If this parameter is not provided '
                    'all tasks should be analyzed. Multiple tasks '
                    'can be specified with a space separated list.',
                    nargs="+")
parser.add_argument('-v', '--version', action='version',
                    version='BIDS-App Scalp Coupling Index version '
                    f'{__version__}')
args = parser.parse_args()

mne.set_log_level("INFO")
logger.info("\n")


########################################
# Extract parameters
########################################

logger.info("Extracting subject metadata.")
subs = []
if args.subject_label:
    logger.info("    Subject data provided as input argument.")
    subs = args.subject_label
else:
    logger.info("    Subject data will be extracted from data.")
    subject_dirs = glob(op.join(args.input_datasets, "sourcedata/sub-*"))
    subs = [subject_dir.split("-")[-1] for
            subject_dir in subject_dirs]
logger.info(f"        Subjects: {subs}")


logger.info("Extracting session metadata.")
sess = []
if args.session_label:
    logger.info("    Session data provided as input argument.")
    sess = args.session_label
else:
    logger.info("    Session data will be extracted from data.")
    session_dirs = glob(op.join(args.input_datasets, "sourcedata/sub-*/ses-*/"))
    sess = [session_dir.split("-")[-1].replace("/", "") for
            session_dir in session_dirs]
    sess = np.unique(sess)
if len(sess) == 0:
    sess = [None]
logger.info(f"        Sessions: {sess}")


logger.info("Extracting tasks metadata.")
tasks = []
if args.task_label:
    logger.info("    Task data provided as input argument.")
    tasks = args.task_label
else:
    raise ValueError(f"You must specify a task label, received {args.task_label}")
logger.info(f"        Tasks: {tasks}")


logger.info("Extracting event metadata.")
events = []
if args.events:
    logger.info("    Event data provided as input argument.")
    # Convert to int keys
    _events = args.events
    trial_type = dict()
    event_codes = dict()
    for event in _events:
        trial_type[int(event)] = _events[event]
        event_codes[str(float(event))] = int(event)
    logger.info(f"        Events: {trial_type}")
    logger.info(f"        Codes:  {event_codes}")
else:
    logger.info("    No event data provided, using default coding.")


########################################
# Main script
########################################

print(" ")
for sub in subs:
    for task in tasks:
        for ses in sess:
            logger.info(f"Processing: sub-{sub}/ses-{ses}")

            b_path = BIDSPath(subject=sub, task=task, session=ses,
                              root=f"{args.input_datasets}/sourcedata",
                              datatype="nirs", suffix="nirs",
                              extension=".snirf")
            dname = str(b_path.directory)
            logger.debug(f"    Using sourcedata directory: {dname}")
            fname = []
            try:
                fname = dname + "/" + next(os.walk(dname))[1][0]
            except IndexError:
                logger.info(f"    Unable to locate data file: {dname}")
            except StopIteration:
                logger.info(f"    Unable to locate data file: {dname}")
            except StopIteration:
                logger.warn(f"    Unknown error for file: {dname}")

            if len(fname) > 0:
                logger.debug(f"    Found sourcedata measurement: {fname}")
                raw = mne.io.read_raw_nirx(fname, preload=False)
                snirf_path = dname + "/" + b_path.basename + ".snirf"
                logger.debug(f"    Writing SNIRF to: {snirf_path}")
                write_raw_snirf(raw, snirf_path)

                raw = mne.io.read_raw_snirf(snirf_path, preload=False)
                if args.events:
                    events, event_id = mne.events_from_annotations(raw, event_codes)
                    raw.set_annotations(
                        mne.annotations_from_events(events, raw.info['sfreq'],
                                                    event_desc=trial_type))
                raw.annotations.duration = np.ones(raw.annotations.duration.shape) *\
                                           args.duration
                raw.info['line_freq'] = 50
                bids_path = BIDSPath(subject=sub, task=task, session=ses,
                                     datatype='nirs', root=f"{args.input_datasets}")
                write_raw_bids(raw, bids_path, overwrite=True)
                os.remove(snirf_path)

# print_dir_tree("/bids_dataset")
