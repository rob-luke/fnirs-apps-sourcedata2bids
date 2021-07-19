from mne_bids import get_entity_vals, BIDSPath, read_raw_bids
subs = get_entity_vals("/bids_dataset", 'subject')
print(f"Found subjects: {subs}")
assert len(subs) == 5
sess = get_entity_vals("/bids_dataset", 'session')
print(f"Found sessions: {sess}")
assert len(sess) == 0
tasks = get_entity_vals("/bids_dataset", 'task')
print(f"Found tasks: {tasks}")
assert len(tasks) == 1

for sub in subs:
    for task in tasks:
        for ses in sess:
            b_path = BIDSPath(subject=sub, task=task, session=ses,
                              root="/bids_dataset",
                              datatype="nirs", suffix="nirs",
                              extension=".snirf")
            raw = read_raw_bids(b_path, verbose=True)
            assert "fnirs_cw_amplitude" in raw
            assert len(raw) > 10