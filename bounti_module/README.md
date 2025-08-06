# 🧠 BOUNTI Segmentation Pipeline 🧠

Welcome to the BOUNTI Segmentation Pipeline! 🚀 This repository contains scripts to extract a segmentation map using BOUNTI. Some scripts are designed to run on the MESOCENTRE, while others are designed to run on NIOLON.

## Table of Contents
- [About](#about)
- [Setup](#setup)
- [Files](#files)
- [Usage](#usage)

## About
This module is designed for extracting a segmentation map using BOUNTI (https://www.biorxiv.org/content/10.1101/2023.04.18.537347v1). The pipeline consists of multiple scripts that perform various preprocessing, processing, and post-processing steps.

## Setup

1. Clone the repository in your mesocentre account and niolon
2. Ensure all dependencies are installed.
3. Configure the paths and settings according to your environment (MESOCENTRE or NIOLON). To do that, see ```configuration.py``` in the main directory
4. You need to have the 3D reconstruction volume for the subject/session you want to segment

## Files
Here are a short descript of the python files in the module:

### Scripts to run on MESOCENTRE:
- a_prepare_bounti.py: Prepares the data and environment for BOUNTI segmentation for the given subject.
- b_generate_niftymic_brainmask.py: Generates a brain mask using NiftyMIC for the given subject.
- c_meso2niolon.py: Transfers data from the Mesocentre to Niolon for the given subject. You will need to change the *user_id* in the code.

We need to transfer the data to niolon because of the Debias-N4 algorithm only available there

### Scripts to run on NIOLON:
- d_bias_field_correction_3d.py: Corrects bias fields in 3D images for the given subject.
- e_dilate_niftymic_brain_mask.py: Dilates the brain mask generated earlier for the given subject.
- f_bounti_segmentation_preproc_haste.py: Preprocesses data for BOUNTI segmentation, specific to HASTE images for the given subject.
- g_process_label.py: Processes the labels generated from the segmentation for the given subject. Transforms the 19 segmentation's label into a 4 segmentation map
- h_niolon2meso.py: Transfers data back from Niolon to the Mesocentre for the given subject. You will need to change the *user_id* in the code.

## Usage
To use this pipeline, follow these general steps:

1. Run the preparation script on **MESOCENTRE**:
   ```bash
   $ python bounti_module/a_prepare_bounti.py SUBJECT
   ```

2. Generate the brain mask on **MESOCENTRE**:
   ```bash
   $ python bounti_module/b_generate_niftymic_brainmask.py SUBJECT
   ```

3. Transfer data to **NIOLON** using:
   ```bash
   $ python bounti_module/c_meso2niolon.py SUBJECT
   ```

4. Perform bias field correction on **NIOLON**:
   ```bash
   $ python bounti_module/d_bias_field_correction_3d.py SUBJECT
   ```

5. Dilate the brain mask on **NIOLON**:
   ```bash
   $ python bounti_module/e_dilate_niftymic_brain_mask.py SUBJECT
   ```

6. Preprocess the data for BOUNTI segmentation on **NIOLON**:
   ```bash
   $ python bounti_module/f_bounti_segmentation_preproc_haste.py SUBJECT
   ```

7. Run BOUNTI in the correct directory, ie within the bounti directory (root folder should be svrtk_BOUNTI)<br>

   ```bash
   $ module load singularity
   $ singularity run --home /envau/work/meca/users/auzias/svrtk_BOUNTI:/home --bind ${PATH_TO_svrtk_BOUNTI}:/mnt /hpc/shared/apps/x86_64/softs/singularity_images/svrtk_auto.sif
   ### within the image prompt:
   $ bash /home/auto-proc-svrtk/scripts/auto-brain-bounti-segmentation-fetal.sh /mnt/input_SRR_nesvor/haste/${subject}/${session}/ /mnt/output_BOUNTI_seg/haste/${subject}/${session}/ && mv tmp_proc /mnt/output_BOUNTI_seg/haste/${subject}/${session}/
   ```
   Example with **Fabienne ses01**:
   ```bash
   bash /home/auto-proc-svrtk/scripts/auto-brain-bounti-segmentation-fetal.sh /mnt/input_SRR_nesvor/haste/Fabienne/ses01/ /mnt/output_BOUNTI_seg/haste/Fabienne/ses01/ && mv tmp_proc /mnt/output_BOUNTI_seg/haste/Fabienne/ses01/
   ```

8. Process the labels on **NIOLON**:
   ```bash
   $ python bounti_module/g_process_label.py SUBJECT
   ```

9. Transfer data back to MESOCENTRE using on **NIOLON**:
   ```bash
   $ python bounti_module/h_niolon2meso.py SUBJECT
   ```

Automatization should/could be implemented with a bash file. Given a subject, it could run all the script, depending on when you are (Mesocentre ou Niolon)