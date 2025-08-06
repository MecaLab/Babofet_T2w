# 🧠 BOUNTI Segmentation Pipeline 🧠

Welcome to the BOUNTI Segmentation Pipeline! 🚀 This repository contains scripts to extract a segmentation map using BOUNTI. Some scripts are designed to run on the MESOCENTRE, while others are designed to run on NIOLON.

## Table of Contents
- [About](#about)
- [Setup](#setup)
- [Files](#files)
- [Usage](#usage)
- [Acknowledgments](#acknowledgments)

## About
This module is designed for extracting a segmentation map using BOUNTI (https://www.biorxiv.org/content/10.1101/2023.04.18.537347v1). The pipeline consists of multiple scripts that perform various preprocessing, processing, and post-processing steps.

## Setup
To set up the project, follow these steps:

1. Clone the repository to your local machine.
2. Ensure all dependencies are installed.
3. Configure the paths and settings according to your environment (MESOCENTRE or NIOLON).

## Files
Here are the main Python files in the project:

### Scripts to run on MESOCENTRE:
- a_prepare_bounti.py: Prepares the data or environment for BOUNTI segmentation.
- b_generate_niftymic_brainmask.py: Generates a brain mask using NiftyMIC.
- c_meso2niolon.py: Transfers data from the mesocentre to NIOLON.

### Scripts to run on NIOLON:
- d_bias_field_correction_3d.py: Corrects bias fields in 3D images.
- e_dilate_niftymic_brain_mask.py: Dilates the brain mask generated earlier.
- f_bounti_segmentation_preproc_haste.py: Preprocesses data for BOUNTI segmentation, specific to HASTE images.
- g_process_label.py: Processes the labels generated from the segmentation.
- h_niolon2meso.py: Transfers data back from NIOLON to the mesocentre.

## Usage
To use this pipeline, follow these general steps:

1. Run the preparation script on MESOCENTRE:
   python a_prepare_bounti.py

2. Generate the brain mask on MESOCENTRE:
   python b_generate_niftymic_brainmask.py

3. Transfer data to NIOLON using:
   python c_meso2niolon.py

4. Perform bias field correction on NIOLON:
   python d_bias_field_correction_3d.py

5. Dilate the brain mask on NIOLON:
   python e_dilate_niftymic_brain_mask.py

6. Preprocess the data for BOUNTI segmentation on NIOLON:
   python f_bounti_segmentation_preproc_haste.py

7. Process the labels on NIOLON:
   python g_process_label.py

8. Transfer data back to MESOCENTRE using:
   python h_niolon2meso.py

## Acknowledgments
This project utilizes BOUNTI for segmentation. For more details on BOUNTI, check out the [paper](https://www.biorxiv.org/content/10.1101/2023.04.18.537347v1).
