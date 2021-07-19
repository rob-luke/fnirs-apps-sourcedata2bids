from mne_bids import get_entity_vals
subs = get_entity_vals("/bids_dataset", 'subject')
print(f"Found subjects: {subs}")
assert len(subs) == 5
sess = get_entity_vals("/bids_dataset", 'session')
print(f"Found sessions: {sess}")
assert len(sess) == 0
tasks = get_entity_vals("/bids_dataset", 'task')
print(f"Found tasks: {tasks}")
# assert len(tasks) == 1