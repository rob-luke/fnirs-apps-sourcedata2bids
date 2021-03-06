FROM ghcr.io/mne-tools/mne-python:main

USER root 

RUN pip install mne-bids==0.10
RUN pip install nilearn==0.9.1
RUN pip install https://github.com/mne-tools/mne-nirs/archive/main.zip
RUN pip install h5py
RUN pip install h5io
RUN pip install seaborn
RUN pip install checksumdir

COPY fnirsapp_sourcedata2bids.py /run.py
RUN chmod +x /run.py

ENTRYPOINT ["/run.py"]
