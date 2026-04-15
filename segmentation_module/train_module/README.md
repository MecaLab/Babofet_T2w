# Fetal Brain Segmentation Training Pipeline

This module contains a comprehensive pipeline for training, evaluating, and exporting a fetal brain tissue segmentation model using the LongiSeg framework. The entire process is orchestrated by a single shell script, `run_train_pipeline.sh`, which ensures a seamless workflow from data preparation to model deployment.

## Overview

The pipeline is managed by a main execution script that calls a series of helper scripts in sequence. The process is as follows:

1.  **Data Preparation**: Raw and ground truth data are organized for LongiSeg.
2.  **Model Training**: A 5-fold cross-validation training is submitted as a Slurm job.
3.  **Inference**: The trained model is used to predict segmentations on the test set.
4.  **Evaluation**: Performance metrics are calculated by comparing predictions to ground truth.
5.  **Export**: The final trained model is packaged into a ZIP archive.

---

## Main Execution Script (`run_train_pipeline.sh`)

-   **Functionality**:
    -   Sets up the necessary environment, including modules and Conda environment.
    -   Calls the Python helper scripts in the correct order.
    -   Submits and waits for Slurm jobs for the training and prediction steps, ensuring the pipeline proceeds only after these computationally intensive tasks are complete.
-   **Usage**:
    ```bash
    ./run_train_pipeline.sh <dataset_id> <dataset_name> <trainer_class> [train_partition] [pred_partition]
    ```
    -   `<dataset_id>`: A unique integer ID for the dataset (e.g., `1`).
    -   `<dataset_name>`: A descriptive name for the dataset (e.g., `FetalBrainSeg`).
    -   `<trainer_class>`: The LongiSeg trainer to use (e.g., `LongiSegTrainerDiffWeighting`).
    -   `[train_partition]` / `[pred_partition]`: Optional Slurm partitions for training and prediction jobs (e.g, `volta`).



---

## Helper Scripts & Configuration

### `config.json`

This file defines the allocation of subjects and sessions to the training and testing datasets, which is critical for a valid model evaluation.

-   `train_subject_sessions`: Specifies data for the training set.
-   `test_subject_sessions`: Specifies data for the hold-out test set.

### 1. Prepare Dataset (`01_prepare_dataset.py`)

This script formats the data into the structure required by LongiSeg.

-   **Functionality**:
    -   Reads `config.json` to split data.
    -   Copies and renames T2w images and segmentation masks into the appropriate `imagesTr`, `labelsTr`, and `imagesTs` directories.
    -   Generates `dataset.json`, `patientsTr.json`, and `patientsTs.json` to provide metadata for the LongiSeg framework.
    -   Runs `LongiSeg_plan_and_preprocess` to finalize data preparation.
-   **Called by**: `run_train_pipeline.sh`

### 2. Calculate Metrics (`02_metrics.py`)

This script evaluates the model's performance after inference is complete.

-   **Functionality**:
    -   Compares predicted segmentations against ground truth labels.
    -   Calculates Dice Score, Intersection over Union (IoU), and Hausdorff Distance.
    -   Aggregates results into a summary CSV file (`resultats_segmentation.csv`).
    -   Generates and saves plots to visualize performance metrics across different models and labels.
-   **Called by**: `run_train_pipeline.sh`

### 3. Export Model (`03_export_model.py`)

A utility to package the trained model for archiving or deployment.

-   **Functionality**:
    -   Compresses the entire trained model directory into a single `.zip` archive.
-   **Called by**: `run_train_pipeline.sh`
