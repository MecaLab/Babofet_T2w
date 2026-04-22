# Fetal Brain Segmentation Module

This module provides a complete solution for fetal brain tissue segmentation using the [LongiSeg](https://github.com/MIC-DKFZ/LongiSeg/tree/master) framework. It is organized into two main sub-modules: one for training a new model and one for running inference with a pre-trained model.

---

## Sub-Modules

### 🏋️ `train_module/`

This module contains the complete pipeline to train a new segmentation model from scratch. It handles data preparation, model training (using 5-fold cross-validation), performance evaluation, and exporting the final model.

**For detailed instructions on how to run the full training pipeline, please see the [train_module/README.md](./train_module/README.md).**

### 🧠 `inference_module/`

This module is used to run inference with a pre-trained model. It manages model retrieval from a server, prepares the input data, and runs the segmentation process to generate prediction masks.

**For detailed instructions on how to run the inference pipeline, please see the [inference_module/README.md](./inference_module/README.md).**
