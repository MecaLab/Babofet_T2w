# Fetal Brain Segmentation Training Pipeline

This module contains a set of scripts to train, evaluate, and manage a deep learning model for fetal brain tissue segmentation using the LongiSeg framework. The pipeline is designed to work with BIDS-formatted data and is executed as a series of sequential steps.

## Overview

The pipeline is organized into five main scripts, each responsible for a specific stage of the machine learning lifecycle:

1.  **Dataset Preparation**: `01_prepare_dataset.py`
2.  **Model Training**: `02_train.py`
3.  **Inference on Test Set**: `03_pred_test.py`
4.  **Performance Evaluation**: `04_metrics.py`
5.  **Model Exporting**: `05_export_model.py`

A `config.json` file is used to define the subject and session splits for training and testing.

Make sure to have your data located, based on the scripts or update the code.

---

## Configuration (`config.json`)

This JSON file specifies which subjects and sessions are allocated to the training and testing datasets. This separation is crucial for ensuring that the model is evaluated on unseen data.

-   `train_subject_sessions`: A dictionary mapping subject identifiers to a list of session IDs for training.
-   `test_subject_sessions`: A dictionary mapping subject identifiers to a list of session IDs for testing.

---

## Pipeline Scripts

### 1. Prepare Dataset (`01_prepare_dataset.py`)

This script organizes the raw and ground truth data into the specific directory structure required by the LongiSeg framework.

-   **Functionality**:
    -   Reads the `config.json` to determine the training/testing split.
    -   Copies the T2w images and their corresponding segmentation masks into `imagesTr`, `labelsTr`, and `imagesTs` folders.
    -   Generates a `dataset.json` file, which contains metadata about the dataset (e.g., channel names, labels, number of training examples).
    -   Generates a `patientsTr.json` to map subjects to their respective timepoints, which is essential for longitudinal analysis.
    -   Runs `LongiSeg_plan_and_preprocess` to verify dataset integrity and prepare the data for training.
-   **Usage**:
    ```bash
    python 01_prepare_dataset.py <dataset_id> <dataset_name>
    ```
    -   `<dataset_id>`: A unique integer ID for the dataset (e.g., `1`).
    -   `<dataset_name>`: A descriptive name for the dataset (e.g., `FetalBrainSeg`).

### 2. Train Model (`02_train.py`)

This script initiates the model training process on a Slurm cluster.

-   **Functionality**:
    -   Generates a Slurm submission script (`longiseg_train.slurm`).
    -   The script uses a 5-fold cross-validation strategy, submitted as a job array.
    -   It activates the appropriate Conda environment and executes the `LongiSeg_train` command.
-   **Usage**:
    ```bash
    python 02_train.py <dataset_id> <trainer_class>
    ```
    -   `<dataset_id>`: The ID of the dataset to train on.
    -   `<trainer_class>`: The nnU-Net trainer class to use (e.g., `LongiSegTrainerDiffWeighting`).

### 3. Predict on Test Set (`03_pred_test.py`)

After training, this script runs inference on the test set.

-   **Functionality**:
    -   Generates a Slurm submission script (`longiseg_prediction.slurm`).
    -   Uses `LongiSeg_find_best_configuration` to determine the optimal model from the cross-validation folds.
    -   Executes `LongiSeg_predict` to generate segmentations for the test images.
    -   Applies post-processing to the predictions using `LongiSeg_apply_postprocessing`.
-   **Usage**:
    ```bash
    python 03_pred_test.py <dataset_id> <dataset_name> <trainer_class> [partition]
    ```
    -   Arguments match those from previous steps.
    -   `[partition]`: Optional Slurm partition (defaults to `volta`).

### 4. Calculate Metrics (`04_metrics.py`)

This script evaluates the model's performance by comparing its predictions against the ground truth labels.

-   **Functionality**:
    -   Calculates key segmentation metrics: Dice Score, Intersection over Union (IoU), and Hausdorff Distance.
    -   Computes mean and standard deviation for each metric across all test subjects and for each tissue label (CSF, WM, GM, Ventricle).
    -   Saves the aggregated results to a CSV file (`resultats_segmentation.csv`).
    -   Generates and saves boxplots and point plots to visualize the performance metrics, allowing for easy comparison between different models.
-   **Usage**:
    ```bash
    python 03_metrics.py <model_ids>
    ```
    -   `<model_ids>`: A comma-separated list of model IDs to evaluate (e.g., `1,2,3`).

### 5. Export Model (`05_export_model.py`)

A utility script to package a trained model or any specified directory into a ZIP archive.

-   **Functionality**:
    -   Compresses the specified file or directory into a `.zip` file. This is useful for archiving, sharing, or deploying a trained model.
-   **Usage**:
    ```bash
    python 04_export_model.py <path_to_zip>
    ```
    -   `<path_to_zip>`: The absolute or relative path to the file or directory you want to compress.
