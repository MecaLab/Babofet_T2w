# Fetal Brain Segmentation Inference Pipeline

This module provides a pipeline for running inference with a pre-trained LongiSeg segmentation model. It handles model retrieval, data preparation, and execution of the prediction and post-processing steps.

## Overview

The inference process is broken down into three sequential scripts:

1.  **Model Retrieval**: `01_retrieve_model.py`
2.  **Data Preparation**: `02_prepare_data.py`
3.  **Inference Execution**: `03_inference.py`

---

## Pipeline Scripts

### 1. Retrieve Model (`01_retrieve_model.py`)

This script is responsible for fetching and unpacking the trained model archive from a remote server.

-   **Functionality**:
    -   Uses `scp` to securely copy a zipped model archive from a remote server (e.g., a high-performance computing cluster) to a local destination.
    -   Unzips the downloaded archive into the appropriate results directory required by the LongiSeg framework.
-   **Usage**:
    ```bash
    python 01_retrieve_model.py <remote_zip_path> <local_destination_path>
    ```
    -   `<remote_zip_path>`: The full path to the model's `.zip` file on the remote server.
    -   `<local_destination_path>`: The local path where the `.zip` file will be saved.

### 2. Prepare Data (`02_prepare_data.py`)

This script prepares the input data for inference by organizing it into the format expected by the LongiSeg prediction script.

-   **Functionality**:
    -   Identifies the 3D reconstructed T2w images (`rec-niftymic_desc-brainbg_T2w.nii.gz`) from the BIDS derivatives directory.
    -   Copies and renames these images into a dedicated inference folder, following the `Subject_Session_0000.nii.gz` naming convention required by nnU-Net/LongiSeg.
-   **Usage**:
    The script is configured internally with a dictionary of subjects and sessions to process. Modify the `subj_sess` dictionary within the script to target different data.
    ```bash
    python 02_prepare_data.py
    ```

### 3. Run Inference (`03_inference.py`)

This script orchestrates the main inference process on a Slurm cluster.

-   **Functionality**:
    -   Generates a `patientsTs.json` file that maps subjects to their corresponding sessions, which is necessary for the longitudinal prediction model.
    -   Creates a Slurm submission script (`longiseg_prediction.slurm`) to run the prediction and post-processing steps.
    -   Executes `LongiSeg_predict` to generate raw segmentation probabilities for the prepared input data using the specified pre-trained model.
    -   Runs `LongiSeg_apply_postprocessing` to refine the raw predictions and produce the final segmentation masks.
-   **Usage**:
    ```bash
    python 03_inference.py <dataset_id> <dataset_name> <trainer_class>
    ```
    -   `<dataset_id>`: The unique integer ID of the dataset the model was trained on.
    -   `<dataset_name>`: The descriptive name of the dataset.
    -   `<trainer_class>`: The nnU-Net trainer class used during training (e.g., `LongiSegTrainerDiffWeighting`).
