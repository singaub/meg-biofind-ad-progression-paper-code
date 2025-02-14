from joblib import Parallel, delayed
import pandas as pd
from datetime import datetime

import os
import mne
from mne_bids import BIDSPath

import os.path as op
import pandas as pd

from joblib import Parallel, delayed
import h5io


import biofind_config_CBU as cfg_CBU
import biofind_config_CTB1 as cfg_CTB1
import biofind_config_CTB2 as cfg_CTB2

#cfgs = [('CBU',cfg_CBU), ('CTB', cfg_CTB1), ('CTB', cfg_CTB2)]
cfgs = [('CBU',cfg_CBU)]

from meeglet import compute_spectral_features, spectrum_from_features

def extract_meeglet(epochs):
    out = dict()
    for pick in ['mag']:  # add or change for 'grad' for gradiometers
        features, info = compute_spectral_features( 
            epochs.copy().pick_types(meg=pick), 
            foi_start=1, foi_end=64, bw_oct=0.35, delta_oct=0.05, density='Hz',
            features=(
                'cov',
                'pow',
                'dwpli',
                'r_plain'
            )
        )
        out[pick] = (
            features.cov,
            features.pow,
            features.dwpli,
            features.r_plain
        )
    return out

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
                   check=False, suffix="epo.fif", processing='epoch')
    if session:
        bp_args['session'] = session
    bp = BIDSPath(**bp_args)

    fname = bp.fpath
    print(fname)
    
    if not fname.exists():
        return 'no file'
    
    epochs = mne.read_epochs(bp, proj=False, preload=True)
    epochs = epochs.pick_types(
        meg=True, eeg=False, eog=False, ecg=False, stim=False,
        exclude=epochs.info['bads']).load_data()
    out = None 
    
    # make sure that no EOG/ECG made it into the selection
    epochs.pick_types(**{data_type: True})
    try:
        out = extract_meeglet(epochs)
    except Exception as err:
        raise err
        return repr(err)

    return out
   
    
N_JOBS = 1
DEBUG = False
if DEBUG:
    N_JOBS = 6
    cfgs = cfgs [:1]

for site, cfg  in cfgs: #for loop on the 3 config files
    subjects = cfg.subjects
    if DEBUG:
        subjects = ['Sub0100']
    features = Parallel(n_jobs=N_JOBS)(
        delayed(run_subject)(sub, cfg, site) for sub in subjects)
        
    date = datetime.now().strftime('%Y-%m-%d_%I-%M')
    # dictionary links subject to corresponding features
    out = {sub: ff for sub, ff in zip(subjects, features)
           if not isinstance(ff, str)}

    # added name of site in name of h5 file
    out_fname = cfg.deriv_root / f'meeglet_{site}_{date}.h5'
    # define the path of the output h5 file
    log_out_fname = (cfg.deriv_root / f'meeglet_{site}_{date}-log.csv')

    h5io.write_hdf5 (out_fname,out, overwrite=True) # save dict in hdf5
    print(f'Features saved under {out_fname}.')

    logging = ['OK' if not isinstance(ff, str) else ff for sub, ff in
                   zip(subjects, features)]
    out_log = pd.DataFrame({"ok": logging, "subject": subjects})
    out_log.to_csv(log_out_fname)
    print(f'Log saved under {log_out_fname}.')
