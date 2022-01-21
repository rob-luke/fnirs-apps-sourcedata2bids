#!/usr/bin/env python3
import pandas as pd
import numpy as np
import mne
import mne_nirs
import os
import argparse
from mne_bids import BIDSPath, write_raw_bids, stats
from mne_nirs.io.snirf import write_raw_snirf
from mne.utils import logger
from glob import glob
import os.path as op
import json
import subprocess
from pathlib import Path
from datetime import datetime
import json
import hashlib
from checksumdir import dirhash
from pprint import pprint

__version__ = "v0.4.3"


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
parser.add_argument('--optode-frame', type=str, default="",
                    help='Coordinate frame used for the optode positions.')
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


def create_report(app_name=None, pargs=None):

    exec_rep = dict()
    exec_rep["ExecutionStart"] = datetime.now().isoformat()
    exec_rep["ApplicationName"] = app_name
    exec_rep["ApplicationVersion"] = __version__
    exec_rep["Arguments"] = vars(pargs)

    return exec_rep

exec_files = dict()
exec_rep = create_report(app_name="fNIRS-Apps: Sourcedata 2 BIDS", pargs=args)
pprint(exec_rep)

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


reader_kwargs = dict()
if args.optode_frame != '':
    logger.info(f"Using {args.optode_frame} optode frame.")
    reader_kwargs["optode_frame"] = args.optode_frame


########################################
# Handle different inputs
########################################

def find_sourcedata(dir):
    """
    Return path to preferred datatype, reader function, and hash of data.

    Will return type in this preference order.
    1. SNIRF files
    2. Directories

    In the future more options should be added.
    """

    filenames_to_ignore = ['.DS_Store']
    sourcedata_types = [".snirf"]
    sourcedata_readers = [mne.io.read_raw_snirf]

    all_data = os.listdir(dir.directory)
    for bad in filenames_to_ignore:
        if bad in all_data:
            all_data.remove(bad)

    for type, reader in zip(sourcedata_types, sourcedata_readers):
        if any([a.endswith(type) for a in all_data]):
            idx = np.where([a.endswith(type) for a in all_data])[0][0]
            dpath = os.path.join(dir.directory, all_data[idx])
            return dpath, reader, hashlib.md5(open(dpath, 'rb').read()).hexdigest()

    if any([os.path.isdir(os.path.join(dir.directory, a)) for a in all_data]):
        idx = np.where([os.path.isdir(os.path.join(dir.directory, a)) for a in all_data])[0][0]
        dpath = os.path.join(dir.directory, all_data[idx])
        return dpath, mne.io.read_raw_nirx, dirhash(dpath, 'md5')

    logger.warn(f"Unknown error for file: {dir.directory}")

    return 0, 0, 0


########################################
# Main script
########################################

print(" ")
for sub in subs:
    for task in tasks:
        for ses in sess:

            # Present information
            logger.info(f"Processing: sub-{sub}/ses-{ses}")
            exec_files[f"sub-{sub}_ses-{ses}_task-{task}"] = dict()

            # Locate files
            b_path = BIDSPath(subject=sub, task=task, session=ses,
                              root=f"{args.input_datasets}/sourcedata",
                              datatype="nirs", suffix="nirs",
                              extension=".snirf")
            # Determine the data type of file and appropriate reader
            data_path, readfn, hash = find_sourcedata(b_path)

            # Present information
            logger.debug(f"    Using sourcedata: {data_path}")
            exec_files[f"sub-{sub}_ses-{ses}_task-{task}"]["InputName"] = str(data_path)
            exec_files[f"sub-{sub}_ses-{ses}_task-{task}"]["InputHash"] = hash

            # Read data
            raw = readfn(data_path, preload=False, **reader_kwargs)

            # Rewrite as SNIRF
            snirf_path = os.path.join(b_path.directory, b_path.basename)
            logger.debug(f"    Writing SNIRF to: {snirf_path}")
            write_raw_snirf(raw, snirf_path)

            # Reread SNIRF
            raw = mne.io.read_raw_snirf(snirf_path, preload=False)

            # Handle renaming and duration of events
            if args.events:
                try:
                    # NIRx use floats as key values
                    events, event_id = mne.events_from_annotations(raw, event_codes)
                except ValueError:
                    try:
                        # SNIRF Files use integer values as keys
                        int_ev_codes = {str(int(float(k))): event_codes[k] for k in event_codes.keys()}
                        events, event_id = mne.events_from_annotations(raw, int_ev_codes)
                    except ValueError:
                        events, event_id = mne.events_from_annotations(raw)
                raw.set_annotations(
                    mne.annotations_from_events(events, raw.info['sfreq'],
                                                event_desc=trial_type))
            raw.annotations.duration = np.ones(raw.annotations.duration.shape) *\
                                       args.duration

            # Add additional info
            raw.info['line_freq'] = 50

            # Final write as BIDS format
            bids_path = BIDSPath(subject=sub, task=task, session=ses,
                                 datatype='nirs', root=f"{args.input_datasets}")
            bids_path = write_raw_bids(raw, bids_path, overwrite=True)
            os.remove(snirf_path)

            exec_files[f"sub-{sub}_ses-{ses}_task-{task}"]["OutputFileHash"] = \
                hashlib.md5(open(bids_path.fpath, 'rb').read()).hexdigest()


exec_rep["Files"] = exec_files
exec_path = f"{args.input_datasets}/execution"
exec_rep["ExecutionEnd"] = datetime.now().isoformat()
pprint(exec_rep)
Path(exec_path).mkdir(parents=True, exist_ok=True)
with open(f"{exec_path}/{exec_rep['ExecutionStart'].replace(':', '-')}-sourcedata2bids.json", "w") as fp:
    json.dump(exec_rep, fp)

pprint(stats.count_events(args.input_datasets))
