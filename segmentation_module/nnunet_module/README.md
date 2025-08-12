# 🌟 nnUNet Training and Inference Pipeline 🌟

A pipeline for training and performing inference with the nnUNet model. This project includes scripts for preparing datasets, training models, and making predictions.

## 📁 Files Overview

### 📄 01_prepare_dataset.py

Script to prepare the dataset for training and inference. It includes functionalities to read and manipulate data files, set up file and folder paths, and possibly generate or verify JSON files.

- Manages data preparation tasks including reading and manipulating data files.
- Sets up file and folder paths and handles dataset configuration.
- Accepts arguments for `dataset_id` and `name` to customize the dataset

Usage :
```bash
python segmentation_module/nnunet_module/01_prepare_dataset.py <dataset_id> <name>
```

### 📄 02_train.py

Script for training a nnUNet model. This script generates a SLURM file for submitting a training job on a cluster.

- Generates a SLURM file to submit a training job on a cluster.
- Accepts arguments for `dataset_id` and `trainer` to customize the training process.

Usage :
```bash
python segmentation_module/nnunet_module/02_train.py <dataset_id> <trainer>
```

### 📄 03_inference.py

Script for handling the inference process of a nnUNet model. It generates a SLURM file to submit an inference job on a cluster.

- Generates a SLURM file to submit an inference job on a cluster.
- Configures specific paths for input and output files.
- Executes an nnUNet command to make predictions.

Usage :
```bash
python segmentation_module/nnunet_module/03_inference.py <dataset_id> <name> <trainer>
```

### 📄 nnUNetTrainerBiasField_Xepochs.py

This file is used to create a custom nnUNet trainer using a BiasField Data Augmentation
There are many inherited classes from the nnUNetTrainer base class with the data augmentation for different number of epochs

You can follow the class format to create your own custom class (by adding a new class, or also a new file), then you need to paste it into the nnunetv2 directory.
For example, mine was:
```bash
~/miniconda3/envs/nnunet/lib/python3.9/site-packages/nnunetv2/training/nnUNetTrainer/
```

### 📄 config.json

This file contains all the data you want to use for the training and the inference.

## 📌 Requirements

- Install nnUNet using https://github.com/MIC-DKFZ/nnUNet
- Configure global path (see documentation)

Ensure that your environment is set up with these requirements before running the scripts.

## ✨ Contributing

Contributions, issues, and feature requests are welcome. Feel free to check issues page if you want to contribute.