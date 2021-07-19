from mne_bids import get_entity_vals
subs = get_entity_vals("/bids_dataset", 'subject')
print(f"Found subjects: {subs}")
assert len(subs) == 5
print(f"Found subjects: {subs}")
sess = get_entity_vals("/bids_dataset", 'session')
assert len(sess) == 0
print(f"Found sessions: {sess}")
tasks = get_entity_vals("/bids_dataset", 'task')
assert len(tasks) == 1
print(f"Found tasks: {tasks}")