# Fetal Brain Segmentation Inference Pipeline

This module contains a streamlined pipeline to run inference using a pre-trained LongiSeg segmentation model. The entire process, from model retrieval to final prediction, is managed by a single shell script, `run_inference_pipeline.sh`.

## Overview

The inference pipeline is automated by a master script that executes a series of steps in a specific order:

1.  **Model Retrieval**: A pre-trained model is downloaded from a remote server and unzipped.
2.  **Data Preparation**: Input images are located and prepared in the format required by LongiSeg.
3.  **Inference Execution**: A Slurm job is submitted to perform segmentation on the prepared data using the CPU.

---

## Main Execution Script (`run_inference_pipeline.sh`)

This is the central script that orchestrates the entire inference workflow. It should be executed from a login node on the cluster.

-   **Functionality**:
    -   Sets up the necessary Conda environment.
    -   Calls the helper Python scripts for model retrieval and data preparation.
    -   Dynamically creates and submits a Slurm job for the inference step, waiting for its completion before finishing.
    -   The inference is configured to run on a CPU, making it flexible for environments without available GPUs.
-   **Usage**:
    ```bash
    ./run_inference_pipeline.sh <zip_server_path> <local_zip_dst> <dataset_id> <dataset_name> <trainer_class>
    ```
    -   `<zip_server_path>`: The full path to the model's `.zip` file on the remote server.
    -   `<local_zip_dst>`: The local path where the `.zip` file will be saved.
    -   `<dataset_id>`: The unique integer ID of the dataset the model was trained on.
    -   `<dataset_name>`: The descriptive name of the dataset.
    -   `<trainer_class>`: The LongiSeg trainer class used during training (e.g., `LongiSegTrainerDiffWeighting`).

---

## Helper Scripts

### 1. Retrieve Model (`01_retrieve_model.py`)

This script handles the download and extraction of the pre-trained model.

-   **Functionality**:
    -   Uses `scp` to securely download a model archive (`.zip`) from a remote server.
    -   Unzips the archive into the correct directory structure for LongiSeg to use.
-   **Called by**: `run_inference_pipeline.sh`

### 2. Prepare Data (`02_prepare_data.py`)

This script organizes the input data for the inference process.

-   **Functionality**:
    -   Copies the target T2w images from the BIDS derivatives directory into a dedicated inference folder.
    -   Renames the images to match the `Subject_Session_0000.nii.gz` format expected by LongiSeg.
    -   Generates a `patientsTs.json` file, which maps subjects to their sessions, a requirement for the longitudinal model.
-   **Called by**: `run_inference_pipeline.sh`
