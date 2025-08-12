# 🌟 LongiSeg Training and Inference Pipeline 🌟

A pipeline for training and performing inference with the nnUNet model. This project includes scripts for preparing datasets, training models, and making predictions.

## 📌 Requirements

- Install LongiSeg using https://github.com/MIC-DKFZ/LongiSeg
- Configure global path (see documentation)

Ensure that your environment is set up with these requirements before running the scripts.

## 📁 Files Overview

### 📄 01_prepare_dataset.py

Script to prepare the dataset for training and inference. It includes functionalities to read and manipulate data files, set up file and folder paths, and possibly generate or verify JSON files.

- Manages data preparation tasks including reading and manipulating data files.
- Sets up file and folder paths and handles dataset configuration.
- Due to this model, the script will also generate 2 json files: patientsTr (training) and patientsTs (inference)
- Accepts arguments for `dataset_id` and `name` to customize the dataset

Usage :
```bash
python segmentation_module/longiseg_module/01_prepare_dataset.py <dataset_id> <name>
```

### 📄 02_train.py

Script for training a LongiSeg model. This script generates a SLURM file for submitting a training job on a cluster.

- Generates a SLURM file to submit a training job on a cluster.
- Accepts arguments for `dataset_id` and `trainer` to customize the training process.

Usage :
```bash
python segmentation_module/longiseg_module/02_train.py <dataset_id> <trainer>
```

### 📄 03_inference.py

Script for handling the inference process of a LongiSeg model. It generates a SLURM file to submit an inference job on a cluster.

- Generates a SLURM file to submit an inference job on a cluster.
- Configures specific paths for input and output files.
- Executes an LongiSeg command to make predictions.

Usage :
```bash
python segmentation_module/longiseg_module/03_inference.py <dataset_id> <name> <trainer>
```

### 📄 config.json

This file contains all the data you want to use for the training and the inference.

## ✨ Contributing

Contributions, issues, and feature requests are welcome. Feel free to check issues page if you want to contribute.