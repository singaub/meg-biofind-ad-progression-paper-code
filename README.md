# Research code from Gaubert et al 2025

This repository contains the research code on which results in Gaubert et al 2025 are based.

In this work we re-analyzed MEG and MRI data from the BioFind dataset accessible through the [Dementia Platform UK (DPUK)](https://portal.dementiasplatform.uk/)

A few highlights / gotchas:

- As the dataset cannot be downloaded, one has to request access to BioFind on DPUK via a research proposal.
- We curated the code here to document the analyses we performed.
- Specific filet paths are turned into placeholders and will have to be substituted.
- The code was run on the DPUK virtual server without access to the internet, preventing the use of GitHub alongside the project.
- The code was run interactively, requiring some changes of flags or specific lines to produce different sets of outputs.
- Some refinements were performed offline on the figures which are not documented by the code.

## Citation

If using our code, please cite our [preprint](https://www.medrxiv.org/content/10.1101/2024.07.06.24310016v1) until our full paper is published.

```
@article{gaubert2025,
	author = {Gaubert, Sinead and Garces, Pilar and Hipp, J{\"o}rg and Bru{\~n}a, Ricardo and Lop{\'e}z, Maria Eugenia and Maestu, Fernando and Vaghari, Delshad and Henson, Richard and Paquet, Claire and Engemann, Denis-Alexander},
	doi = {10.1016/j.ebiom.2025.105659},
	isbn = {2352-3964},
	journal = {eBioMedicine},
	title = {Exploring the neuromagnetic signatures of cognitive decline from mild cognitive impairment to Alzheimer's disease dementia},
	type = {doi: 10.1016/j.ebiom.2025.105659},
	url = {https://doi.org/10.1016/j.ebiom.2025.105659},
	volume = {114},
	year = {2025}
}
```

## Overview on order of running scripts and relationship to figures.

### MEG processing

For preprocessing to work, you will need the following files, which borrow from the MNE-BIDS pipeline. As we managed hardware limitations, we did not use the full MNE-BIDS pipeline which at the point of investigation wrote intermediate results onto the disk.

Configuratsion (by site and MEG calibration files to chunk computation into smaller pieces managed by the DPUK server):

- biofind_config_CBU.py
- biofind_config_CTB1.py
- biofind_config_CTB2.py

For producing the MEG outputs we ran the following steps, reusing the older INRIA-based pipeline from Engemann et al 2020 and Sabbagh et al 2020.

- compute-preprocesing.py
- compute-maxfilter.py
- copmute-features-biofind.py

For the ```compute-preprocessing.py``` and ```compute-features.py``` the user must select the config and rerun the script accordingly and repeat the procedure until all subjects are processed.

```python
#cfgs = [('CBU',cfg_CBU), ('CTB', cfg_CTB1), ('CTB', cfg_CTB2)]
cfgs = [('CTB',cfg_CTB2)]
```

Of note, for some of the supplementary analyses we computed results using gradiometers, which led us to memory capacity limits.
We then manually selected the feature of interest and created separate outputfiles which we later merged for visual and statisticaln analyses.

### Figure 1

- fig1_psd_converters.ipynb
- fig1_covs.ipynb

### Figure 2

- fig2_log_reg_meg_cluster_adj.R
- fig2_log_reg.ipynb

### Figure 3

- fig3_sensor_stats.py
- fig3_manova.py


### Figure 4

- fig4_sensor_stats.py 
- fig4_manova.py

### Figure 5

- fig5_classificartion_model_MEG.ipynb
- fig5_classificartion_model_MRI.ipynb
- fig5_big_stacking_model.ipynb

### Supplementary Figures and Tables

#### S1

- figS1.ipynb

#### S2

- figS2_mod1.ipynb
- figS2_mod2.ipynb
- figS2_mod3.ipynb

#### S3

- figS3_log_reg.ipynb
- figS3_log_reg_meg_cluster_ave.R

#### S4

- figS4.ipynb

#### S5

- figS5.ipynb

#### S6

- figS6.ipynb

#### S7

- figS7.ipynb

#### S8

- figS8.ipynb

#### S9

- figS9.ipynb

#### S10

- figS10.ipynb

#### Table S1

- table_S1.R
