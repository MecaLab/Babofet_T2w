# NiftyMIC Pipeline

This module provides a pipeline for fetal brain MRI reconstruction using [NiftyMIC](https://github.com/gift-surg/NiftyMIC). It processes raw T2-weighted MRI stacks to produce a high-resolution, motion-corrected, and reconstructed volume.

## Pipeline Overview

The pipeline consists of four main steps, executed sequentially via the `run_pipeline.slurm` script.

1.  **Denoising**: Applies denoising to the raw input stacks.
2.  **Image Reconstruction**: Performs slice-to-volume reconstruction (SVR) using NiftyMIC.
3.  **Subject Template Brainmask Generation**: Generates a brain mask for the reconstructed subject template.
4.  **Debias**: Applies N4 bias field correction to the reconstructed volume.

## Usage

The pipeline is designed to be run on a Slurm cluster.

```bash
sbatch run_pipeline_niftymic.slurm <subject> <session>
```

**Arguments:**

*   `<subject>`: The subject ID (e.g., `sub-Aziza`).
*   `<session>`: The session ID (e.g., `ses-01`).

**Example:**

```bash
sbatch run_pipeline_niftymic.slurm sub-Aziza ses-01
```

## Detailed Steps

### 1. Denoising (`01_denoising.py`)

*   **Input**: Raw T2w NIfTI files from `sourcedata/raw/<subject>/<session>/anat`.
*   **Output**: Denoised NIfTI files in `derivatives/intermediate/niftymic/<subject>/<session>`.
*   **Process**: Uses the `DenoiseImage` executable (from ANTs or similar) to denoise each T2w stack found in the input directory.
*   **Naming Convention**: Output files are suffixed with `_denoised.nii.gz`.

### 2. Image Reconstruction (`02_image_reconstruction.py`)

*   **Input**:
    *   Denoised T2w stacks from the previous step.
    *   Brain masks corresponding to the input stacks (expected in `derivatives/niftymic/<subject>/<session>/anat`).
    *   Gestational age information from the subject's sessions TSV file.
    *   Fetal brain atlas template (selected based on gestational age).
*   **Output**: Reconstructed volume in `derivatives/intermediate/niftymic/<subject>/<session>/reconstruction_niftymic`.
*   **Process**:
    *   Retrieves gestational age to select the appropriate atlas template.
    *   Pairs denoised stacks with their corresponding brain masks.
    *   Runs `niftymic_run_reconstruction_pipeline` inside a Singularity container.
    *   Performs motion correction and reconstruction.

### 3. Generate Subject Template Brainmask (`03_generate_subj_template_brainmask.py`)

*   **Input**:
    *   Brain masks from `derivatives/niftymic/<subject>/<session>/anat`.
    *   Motion correction transformations generated in Step 2.
    *   Reconstructed template from Step 2.
*   **Output**: `srr_template_mask.nii.gz` in the reconstruction directory.
*   **Process**:
    *   Maps transformation files (.tfm) to match the naming convention of the mask stacks.
    *   Runs `niftymic_reconstruct_volume_from_slices` to reconstruct the brain mask in the template space.

### 4. Debias (`04_debias.py`)

*   **Input**:
    *   Reconstructed volume (`srr_template.nii.gz`).
    *   Reconstructed brain mask (`srr_template_mask.nii.gz`).
*   **Output**:
    *   `srr_template_debiased.nii.gz` in the reconstruction directory.
    *   Final output copied to `derivatives/niftymic/<subject>/<session>/anat` with BIDS-compliant naming (e.g., `..._rec-niftymic_desc-brainbg_T2w.nii.gz`).
*   **Process**:
    *   Applies N4 bias field correction using `N4BiasFieldCorrection`.

## Prerequisites & Configuration

*   **Configuration**: The scripts rely on a `configuration.py` module (located in the parent directory) to define paths such as `SOURCEDATA_BIDS_PATH`, `DERIVATIVES_BIDS_PATH`, `SOFTS_PATH`, and `FETAL_RESUS_ATLAS`.
*   **Software**:
    *   Singularity (for running NiftyMIC container).
    *   ANTs (Advanced Normalization Tools) for denoising and bias correction.
    *   Python environment with `nibabel`, `pandas`, `numpy`.
*   **NiftyMIC Container**: The pipeline expects the NiftyMIC Singularity image (`niftymic.multifact_latest.sif`) to be present in the configured software path.
