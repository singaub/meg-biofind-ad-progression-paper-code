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

If using our code, please cite our preprint until our full paper is published.

```
@article{gaubert2024exploring,
  title={Exploring the neuromagnetic signatures of cognitive decline from mild cognitive impairment to Alzheimer's disease dementia},
  author={Gaubert, Sinead and Garces, Pilar and Hipp, J{\"o}rg and Bru{\~n}a, Ricardo and Lop{\'e}z, Maria Eugenia and Maestu, Fernando and Vaghari, Delshad and Henson, Richard and Paquet, Claire and Engemann, Denis},
  journal={medRxiv},
  pages={2024--07},
  year={2024},
  publisher={Cold Spring Harbor Laboratory Press}
}
```

## Overview on order of running scripts and relationship to figures.

### MEG processing

For preprocessing to work, you will need the following files, which borrow from the MNE-BIDS pipeline. As we managed hardware limitations, we did not use the full MNE-BIDS pipeline which at the point of investigation wrote intermediate results onto the disk.

Configuratsion (by site and MEG calibration files to chunk computation into smaller pieces managed by the DPUK server):

- [x] biofind_config_CBU.py
- [x] biofind_config_CTB1.py
- [x] biofind_config_CTB2.py

For producing the MEG outputs we ran the following steps, reusing the older INRIA-based pipeline from Engemann et al 2020 and Sabbagh et al 2020.

- [x] compute-preprocesing.py
- [x] compute-maxfilter.py
- [x] copmute-features-biofind.py

For the ```compute-preprocessing.py``` and ```compute-features.py``` the user must select the config and rerun the script accordingly and repeat the procedure until all subjects are processed.

```python
#cfgs = [('CBU',cfg_CBU), ('CTB', cfg_CTB1), ('CTB', cfg_CTB2)]
cfgs = [('CTB',cfg_CTB2)]
```

Of note, for some of the supplementary analyses we computed results using gradiometers, which led us to memory capacity limits.
We then manually selected the feature of interest and created separate outputfiles which we later merged for visual and statisticaln analyses.

### Figure 1

- [x] fig1_psd_converters.ipynb
- [x] fig1_covs.ipynb

### Figure 2

### Figure 3

### Figure 4

- [x] fig4_dwpli.py
- [x] fig4_rplain.py

### Figure 5

- [x] fig5_classificartion_model_MEG.ipynb
- [x] fig5_classificartion_model_MRI.ipynb
- [x] fig5_big_stacking_model.ipynb

### Supplementary Figures and Tables

#### S1

#### S2

#### S3

#### S4

#### S6

#### S7

#### S8

#### S9

#### S10