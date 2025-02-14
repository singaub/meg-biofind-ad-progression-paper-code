from joblib import Parallel, delayed
import pandas as pd

import os
import mne
from mne_bids import BIDSPath

import biofind_config_CBU as cfg_CBU
import biofind_config_CTB1 as cfg_CTB1
import biofind_config_CTB2 as cfg_CTB2

cfgs = [('CBU',cfg_CBU), ('CTB', cfg_CTB1), ('CTB', cfg_CTB2)]

# main function

def run_subject(subject, cfg, site):
    """
    #using bids root input, not deriv root!
    #file input example:
    sub-CC110187_ses-rest_task-rest_meg.fif
    
    #File output example
    sub-CC110187_ses-rest_task-rest_proc-sss_meg.fif
    """
    bids_root = cfg.bids_root
    deriv_root = cfg.deriv_root
    task = cfg.task
    analyze_channels = cfg.analyze_channels
    data_type = cfg.data_type
    session = cfg.sessions[0]
    if session.startswith('ses-'):
        session = session.lstrip('ses-')
        
    bp_args = dict(root=bids_root,
                   subject=subject,
                   session=session[0],
                   task=task,
                   datatype=data_type,
                   check=False, suffix="meg")
    if session:
        bp_args['session'] = session
    bp = BIDSPath(**bp_args)
    fname = bp.fpath
    if not fname.exists():
        return 'no file'
    raw = mne.io.read_raw_fif(bp)
    renaming_type = {''}
    dev_head_t = raw.info['dev_head_t']
    
    if len(cfg.drop_channels) > 0:
        raw.drop_channels(cfg.drop_channels)
    
    custom_bads = [
        channel for channel in raw.info.ch_names if
        channel.startswith('MISC') or
        channel.startswith('STI')] # creates a list of bad channels
    if len(custom_bads) > 0:
        raw.drop_channels(custom_bads)

    # renaming channel 'EEG061' to 'EOG061' and changing type to EOG channel for
    # site ctb 1 and 2
    if site == 'CTB' and 'EEG061' in raw.info.ch_names:
        raw.rename_channels({'EEG061':'EOG061'})
        raw.set_channel_types({'EOG061':'eog'})

    # renaming channels from EEG to EOG for a list of subjects from CBU site
    subjects_to_rename = [
        'Sub0127','Sub0128','Sub0129','Sub0130','Sub0131','Sub0132','Sub0133',
        'Sub0134','Sub0135','Sub0136','Sub0137','Sub0138','Sub0139','Sub0140',
        'Sub0141','Sub0143','Sub0145', 'Sub0146','Sub0147', 'Sub0148',
        'Sub0149','Sub0150','Sub0151']
    if site == 'CBU' and subject in subjects_to_rename:
        raw.rename_channels({'EEG061':'EOG061','EEG062':'EOG062'})
        raw.set_channel_types({'EOG061':'eog', 'EOG062':'eog'})
        
    common_mf_kws = dict(
        calibration=cfg.mf_cal_fname,
        cross_talk=cfg.mf_ctc_fname,
        st_duration=cfg.mf_st_duration,
        origin=cfg.mf_head_origin,
        coord_frame='head',
        destination=(0, 0, 0.04) #dev_head_t
     )
    
    raw_sss = mne.preprocessing.maxwell_filter(raw, **common_mf_kws)
    bp_args.update(root=deriv_root, processing='sss', suffix='raw.fif')
    bp_out = BIDSPath(**bp_args)
    print(bp_out)
    raw_sss.save(bp_out, overwrite=True)
    ok = 'OK'
    return ok

N_JOBS = 7
DEBUG = False # if True test on one subject
if DEBUG:
    N_JOBS = 1
    cfgs = cfgs [:1]

for site, cfg  in cfgs: #for loop on the 3 config files
    subjects = cfg.subjects
    if DEBUG:
        #subjects = subjects[:1]
        subjects = ['Sub0112', 'Sub0113']
    logging = Parallel(n_jobs=N_JOBS)(
        delayed(run_subject)(sub, cfg, site) for sub in subjects)
    out_log = pd.DataFrame({"ok": logging, "subjects": subjects})
    out_log.to_csv(cfg.deriv_root / 'sss_log.csv')
