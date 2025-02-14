import importlib
from types import SimpleNamespace
import pandas as pd

def prepare_dataset(dataset):
    # dataset configuration of the bids pipeline config file,
    # mapping dataset to each config
    config_map = {'biofind_CBU': "biofind-config-CBU",
                  'biofind_CTB1': "biofind-config-CTB1",
                  'biofind_CTB2': "biofind-config-CTB1",
                  }
    if dataset not in config_map:
        raise ValueError(
            f"We don't know the dataset '{dataset}' you requested.")

    cfg_in = importlib.import_module(config_map[dataset])
    cfg_out = SimpleNamespace(
        bids_root=cfg_in.bids_root,
        deriv_root=cfg_in.deriv_root,
        task=cfg_in.task,
        analyze_channels=cfg_in.analyze_channels,
        data_type=cfg_in.data_type,
        subjects_dir=cfg_in.subjects_dir
    )
    cfg_out.conditions = {  # use for epoching
        'biofind_CBU': ('rest'),
        'biofind_CTB1': ('rest'),
        'biofind_CTB2': ('rest',)
    }[dataset]
    cfg_out.feature_conditions = {  # use for selecting data for features
        'biofind_CBU': ('rest'),
        'biofind_CTB1': ('rest'),
        'biofind_CTB2': ('rest',)
    }[dataset]

    cfg_out.session = ''
    sessions = cfg_in.sessions
    if dataset in ('biofind_CBU', 'biofind_CTB1', 'biofind_CTB2'):
         #changed names of dataset
        cfg_out.session = 'ses-' + sessions[0]

    subjects_df = pd.read_csv(cfg_out.bids_root / "participants.tsv", sep='\t')
    subjects = sorted(sub for sub in subjects_df.participant_id if
                      (cfg_out.deriv_root / sub / cfg_out.session /
                       cfg_out.data_type).exists())

    return cfg_out, subjects
