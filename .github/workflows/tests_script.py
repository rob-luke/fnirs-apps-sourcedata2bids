from mne_bids import get_entity_vals
subs = get_entity_vals("/bids_dataset", 'subject')
assert len(subs) == 5
