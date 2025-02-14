import pandas as pd
import numpy as np
import pathlib

# General settings
site = 'CTB'
study_name = '<ADD YOUR STUDY NAME>'
bids_root = pathlib.Path('<ADD YOUR BIDS ROOT PATH>')
deriv_root = pathlib.Path('<ADD YOUR DERIVATIVE PATH>')
subjects_dir = None

# read text file and add a name for the column
df = pd.read_csv('CTBcal.txt', names=['site'])
# create a column with order from 1 to 324
df['order'] = np.arange(df.shape [0]) + 1
# create a third column with the subject ID
df['sub_id'] = 'Sub' + df["order"].astype(str).str.zfill(4)
# filtering site 2 for CTB2 and selecting only the subj_id and
# transforming df to a list
subjects = df.query("site == 2")["sub_id"].tolist()

task_is_rest = True
task = 'rest'
conditions = None
ch_types = ['meg']
data_type = 'meg'
sessions = ['meg1']

# Preprocessing
meg_reference = []
eog_channel = []
find_breaks = False
find_flat_channels_meg = True
find_noisy_channels_meg = True
analyze_channels = 'all'
drop_channels = []

mf_cal_fname = deriv_root / 'sss_cal_CTB_2.dat'
mf_ctc_fname = deriv_root / 'ct_sparse_CTB.fif'

use_maxwell_filter = True
mf_st_duration = 10.
decim = 5

n_proj_eog = 1
reject = None
on_rename_missing_events = "warn"
N_JOBS = 16

epochs_tmin = 0.
epochs_tmax = 10.
rest_epochs_overlap = 0.
rest_epochs_duration = 10.
baseline = None

# filter eog and ecg
spatial_filter = 'ssp'
n_proj_eog = dict(n_mag=1, n_grad=1)
n_proj_ecg = dict(n_mag = 1, n_grad=1)
ssp_meg = 'auto'
ssp_reject_eog = {'grad':10e-10, 'mag': 20e-12}
ssp_reject_ecg = {'grad':10e-10, 'mag': 20e-12}
eog_proj_from_average = True
ecg_proj_from_average = True

# source level analysis
mf_head_origin = 'auto'
run_souce_estimation = True
use_template_mri = "faverage_small"
