# 🌟 nnUNet Training and Inference Pipeline 🌟

A pipeline for training and performing inference with the nnUNet model. This project includes scripts for preparing datasets, training models, and making predictions.

## 📁 Files Overview

### 📄 01_prepare_dataset.py

Script to prepare the dataset for training or inference. It includes functionalities to read and manipulate data files, set up file and folder paths, and possibly generate or verify JSON files.

- Manages data preparation tasks including reading and manipulating data files.
- Sets up file and folder paths and handles dataset configuration.
- Accepts arguments for `dataset_id` and `name` to customize the dataset

Usage example :
```bash
python nnunet_module/01_prepare_dataset.py <dataset_id> <trainer>
```

### 📄 02_train.py

Script for training a nnUNet model. This script generates a SLURM file for submitting a training job on a cluster.

- Generates a SLURM file to submit a training job on a cluster.
- Accepts arguments for `dataset_id` and `trainer` to customize the training process.

Usage example :
```bash
python nnunet_module/02_train.py <dataset_id> <trainer>
```

### 📄 03_inference.py

Script for handling the inference process of a nnUNet model. It generates a SLURM file to submit an inference job on a cluster.

- Generates a SLURM file to submit an inference job on a cluster.
- Configures specific paths for input and output files.
- Executes an nnUNet command to make predictions.

Usage example :
```bash
python nnunet_module/03_inference.py <dataset_id> <name> <trainer>
```

## 📌 Requirements

- Python 3.x
- Access to a SLURM cluster for job submission
- nnUNet installed and configured, see https://github.com/MIC-DKFZ/nnUNet/tree/master
- Necessary modules and dependencies (e.g., CUDA for GPU support)

Ensure that your environment is set up with these requirements before running the scripts.

## ✨ Contributing

Contributions, issues, and feature requests are welcome. Feel free to check issues page if you want to contribute.
