FROM continuumio/miniconda3:4.8.2

RUN conda install --yes \
    -c conda-forge \
    python==3.8 \
    tini \
    matplotlib

# TODO: try installing via conda or requirements.txt
RUN pip install mne
RUN pip install https://codeload.github.com/rob-luke/mne-bids/zip/nirs
RUN pip install https://github.com/nilearn/nilearn/archive/main.zip
RUN pip install mne-nirs
RUN pip install h5py
RUN pip install seaborn

COPY fnirsapp_sourcedata2bids.py /run.py
RUN chmod +x /run.py

ENTRYPOINT ["/run.py"]
