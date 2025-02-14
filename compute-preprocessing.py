from joblib import Parallel, delayed
import pandas as pd

import os
import mne
import autoreject

from mne_bids import BIDSPath
import numpy as np

import os.path as op
import pandas as pd

from joblib import Parallel, delayed
from autoreject import get_rejection_threshold


import biofind_config_CBU as cfg_CBU
import biofind_config_CTB1 as cfg_CTB1
import biofind_config_CTB2 as cfg_CTB2

#cfgs = [('CBU',cfg_CBU), ('CTB', cfg_CTB1), ('CTB', cfg_CTB2)]
cfgs = [('CTB',cfg_CTB2)]

# main function

def run_subject(subject, cfg, site):
    """
    #using bids root input, not deriv root!
    #file input example:
    sub-CC110187_ses-rest_task-rest_meg.fif
    
    #File output example
    sub-CC110187_ses-rest_task-rest_proc-sss_meg.fif
    """
    print(subject) 
    bids_root = cfg.bids_root
    deriv_root = cfg.deriv_root
    task = cfg.task
    analyze_channels = cfg.analyze_channels
    data_type = cfg.data_type
    session = cfg.sessions[0]
    if session.startswith('ses-'):
        session = session.lstrip('ses-')
        
    bp_args = dict(root=deriv_root,
                   subject=subject,
                   session=session[0],
                   task=task,
                   datatype=data_type,
                   check=False, suffix="raw.fif", processing='sss')
    if session:
        bp_args['session'] = session
    bp = BIDSPath(**bp_args)
    fname = bp.fpath
    if not fname.exists():
        return 'no file'
    raw = mne.io.read_raw_fif(bp, preload = True) # load raw
    try:
        if site == 'CBU':
            # supresses EEG channels (no need for analysis)
            eeg_channels = [channel for channel in raw.info.ch_names
                            if channel.startswith('EEG')]
            if len(eeg_channels) > 0:
                raw.drop_channels(eeg_channels)
            
      
        raw.crop(0, 120) # cfrop first 120 sec
        raw.resample(250)
        raw.filter(l_freq=0.5, h_freq=100, method='iir')
        raw.notch_filter(freqs = [50])
        # filtering data, 4th order butterworth filter and notch

        _compute_add_ssp_exg(raw, subject) #  ssp to reject eog ecg artefacts

        reject = None

        duration=10.
        events = mne.make_fixed_length_events(
            raw, id=3000, start=0, duration=duration
        )

        epochs = mne.Epochs(  # decoupe en epoques
            raw, events, event_id=3000, tmin=0, tmax=duration, proj=True,
            baseline=None, reject=reject, preload=True, decim=1)
            
        ar = autoreject.AutoReject(n_jobs=1, cv=5)
        epochs = ar.fit_transform(epochs)
        
        bp_args.update(processing='epoch', suffix='epo.fif')
        bp_out = BIDSPath(**bp_args)
        print(bp_out)
        epochs.save(bp_out, overwrite=True)
        ok = 'OK'
        return ok
    except Exception as e:
        message = f"an error has occured for subject {subject}: {e}"
        raise Exception(message)
    
def _get_global_reject_ssp(raw, subject):
    reject_eog = None
    no_eog = [  # at time of first usage EOG was not available in some subjects
        'Sub0124',
        'Sub0043',
        'Sub0317',
        'Sub0267',
        'Sub0272',
        'Sub0323'
    ]
    if subject not in no_eog:
        eog_epochs = mne.preprocessing.create_eog_epochs(raw)
        if len(eog_epochs) >= 5:
            reject_eog = get_rejection_threshold(eog_epochs, decim=8)
            del reject_eog['eog']
    
    ecg_epochs = mne.preprocessing.create_ecg_epochs(raw)
    if len(ecg_epochs) >= 5:
        reject_ecg = get_rejection_threshold(ecg_epochs, decim=8)
    else:
        reject_ecg = None

    return reject_eog, reject_ecg
    
def _compute_add_ssp_exg(raw, subject):
    reject_eog, reject_ecg = _get_global_reject_ssp(raw, subject)
    
    if reject_eog is not None:
        proj_eog = mne.preprocessing.compute_proj_eog(
            raw, average=True, reject=reject_eog, n_mag=1, n_grad=1, n_eeg=1)
        raw.add_proj(proj_eog[0])
        
    proj_ecg = mne.preprocessing.compute_proj_ecg(
        raw, average=True, reject=reject_ecg, n_mag=1, n_grad=1, n_eeg=1)

    raw.add_proj(proj_ecg[0])


def _get_global_reject_epochs(raw):
    duration = 3.
    events = mne.make_fixed_length_events(
        raw, id=3000, start=0, duration=duration)
    epochs = mne.Epochs(
        raw, events, event_id=3000, tmin=0, tmax=duration, proj=False,
        baseline=None, reject=None)
    epochs.apply_proj()
    epochs.load_data()
    epochs.pick_types(meg=True)
    reject = get_rejection_threshold(epochs, decim=8)
    return reject


N_JOBS = 10
DEBUG = False
if DEBUG:
    N_JOBS = 1
    cfgs = cfgs [:1]

for site, cfg  in cfgs: #for loop on the 3 config files
    subjects = cfg.subjects
    if DEBUG:
        subjects = ['Sub0127']
    logging = Parallel(n_jobs=N_JOBS)(
        delayed(run_subject)(sub, cfg, site) for sub in subjects)
    out_log = pd.DataFrame({"ok": logging, "subjects": subjects})
    out_log.to_csv(cfg.deriv_root / f'epo_log_{site}.csv')
