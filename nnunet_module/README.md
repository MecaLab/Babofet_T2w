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
python nnunet_module/01_prepare_dataset.py <dataset_id> <name>
```

### 📄 02_train.py

Script for training a nnUNet model. This script generates a SLURM file for submitting a training job on a cluster.

- Generates a SLURM file to submit a training job on a cluster.
- Accepts arguments for `dataset_id` and `trainer` to customize the training process.

Usage :
```bash
python nnunet_module/02_train.py <dataset_id> <trainer>
```

### 📄 03_inference.py

Script for handling the inference process of a nnUNet model. It generates a SLURM file to submit an inference job on a cluster.

- Generates a SLURM file to submit an inference job on a cluster.
- Configures specific paths for input and output files.
- Executes an nnUNet command to make predictions.

Usage :
```bash
python nnunet_module/03_inference.py <dataset_id> <name> <trainer>
```

### 📄 04_dice_per_session.py

Script to calculate the Dice score for each session, a common metric for evaluating segmentation performance.

- Compares predictions with ground truths and calculates scores for different label classes.

Usage :
```bash
python 04_dice_per_session.py <session>
```

### 📄 05_fusion.py

Script related to the fusion of different results or models, improving prediction accuracy by combining multiple outputs.

- Merges outputs from multiple models to make a final prediction using the probabilities given by the previous script.
- You can choose which fusion methods you want from [max_prob, mean_prob, entropy, staple]
- STAPLE is described here: https://pubmed.ncbi.nlm.nih.gov/15250643/
- You can also implement your own method

Usage :
```bash
python 05_fusion.py <method> <dataset_1> <dataset_2> [<dataset_3>]
# dataset_3 is required when using STAPLE method
```

### 📄 06_volume.py

Script to analyze volumes of different segmented structures. Used to quantify segmented regions in medical images.

- Computes volumes for segmented regions, aiding in the evaluation of model performance in terms of spatial accuracy.
- The argument `model_id` should be either `fusion` or one model's ID 

Usage :
```bash
python 06_volume.py <subject> <model_id>
```

### 📄 07_histo_diff.py

Script to generate histograms of differences between two datasets. Useful to visualize how predictions differ between two models or configurations.

- Creates histograms showing the distribution of differences between model predictions on the same dataset.
- Creates confusion matrix

Usage :
```bash
python 07_histo_diff.py <dataset_id_1> <dataset_id_2>
```

### 📄 nnUNetTrainerBiasField_Xepochs.py

This file is used to create a custom nnUNet trainer using a BiasField Data Augmentation
There are many inherited classes from the nnUNetTrainer base class with the data augmentation for different number of epochs

You can follow the class format to create your own custom class (by adding a new class, or also a new file), then you need to paste it into the nnunetv2 directory.
For example, mine was:
```bash
~/miniconda3/envs/nnunet/lib/python3.9/site-packages/nnunetv2/training/nnUNetTrainer/
```

## 📌 Requirements

- Install nnUNet using https://github.com/MIC-DKFZ/nnUNet
- Configure global path (see documentation)

Ensure that your environment is set up with these requirements before running the scripts.

## ✨ Contributing

Contributions, issues, and feature requests are welcome. Feel free to check issues page if you want to contribute.
