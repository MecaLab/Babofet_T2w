# Babofet_T2w: Fetal Brain MRI Processing Pipeline

This project provides a complete, end-to-end pipeline for processing fetal rhesus macaque T2-weighted (T2w) MRI scans. The workflow starts with raw, multi-slice MRI data and produces high-resolution 3D brain volumes, tissue segmentations, and finally, 3D cortical surface models.

## Pipeline Overview

The project is organized into three main modules that are designed to be run in sequence. The output of one module serves as the input for the next.

**Workflow:**

1.  🧠 **`nifty_module/`**
    -   **Input**: Raw, multi-slice T2w NIfTI files.
    -   **Process**: Reconstructs the slices into a single, high-resolution, motion-corrected 3D brain volume using **NiftyMIC**.
    -   **Output**: A 3D brain volume (`..._rec-niftymic_desc-brainbg_T2w.nii.gz`).

2.  🎨 **`segmentation_module/`**
    -   **Input**: The 3D reconstructed brain volume from the `nifty_module`.
    -   **Process**: Segments the brain volume into different tissue types (Gray Matter, White Matter, CSF, etc.) using a deep learning model based on **LongiSeg**.
    -   **Output**: A 3D segmentation mask (`..._desc-longiseg_dseg.nii.gz`).

3.  ✨ **`extraction_module/`**
    -   **Input**: The 3D segmentation mask from the `segmentation_module`.
    -   **Process**: Registers an atlas to the subject, splits the brain into hemispheres, and extracts the inner cortical surface (white matter).
    -   **Output**: 3D surface files for each hemisphere (`..._hemi-L_white.surf.gii` and `..._hemi-R_white.surf.gii`).

---

## How to Use

Each module contains its own set of scripts and a detailed `README.md` file with specific instructions on how to run its pipeline.

To process data from start to finish, run the modules in the following order:

1.  **Navigate to `nifty_module/`** and follow its README to reconstruct your raw MRI data.
2.  **Navigate to `segmentation_module/`** and follow its README to segment the reconstructed volumes.
3.  **Navigate to `extraction_module/`** and follow its README to extract the cortical surfaces from the segmentations.
