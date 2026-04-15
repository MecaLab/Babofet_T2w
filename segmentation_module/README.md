# Fetal Brain Segmentation Module

This module provides a complete solution for fetal brain tissue segmentation using the [LongiSeg](https://github.com/MIC-DKFZ/LongiSeg/tree/master) framework. It is organized into two main sub-modules: one for training a new model and one for running inference with a pre-trained model.

---

## 1. Installation of LongiSeg

Both pipelines depend on the LongiSeg framework. Before running any scripts, you must install it by following these steps. It is highly recommended to do this within a dedicated Conda or Python virtual environment.

```bash
# 1. Create virtual env using conda
conda create -n longiseg python=3.12
conda activate longiseg

# 2. Install PyTorch (https://pytorch.org/get-started/locally/)

pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cpu  # For Linux without GPU (Niolon)
pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cu126  # For Linux with GPU (Mesocentre)

# 3. Clone the LongiSeg repository
git clone https://github.com/MIC-DKFZ/LongiSeg.git

# 4. Navigate into the cloned directory
cd LongiSeg

# 5. Install the package in editable mode
pip install -e .

# 6. Creat paths at the end of the ~/.bashrc file
export LongiSeg_raw="/path_to_data_dir/LongiSeg_raw"
export LongiSeg_preprocessed="/path_to_data_dir/LongiSeg_preprocessed"
export LongiSeg_results="/path_to_experiments_dir/LongiSeg_results"

# 7. After editing the file, do
source ~/.bashrc # to activate the new paths
# an easy way to check if it works is to do:
echo $LongiSeg_raw  # it will display the path you set 
```
After this, LongiSeg's command-line tools (like `LongiSeg_train`, `LongiSeg_predict`, etc.) will be available in your environment.

**If you have any troubles, refer to the [github](https://github.com/MIC-DKFZ/LongiSeg/tree/master) page**

---

## 2. Sub-Modules

### 🏋️ `train_module/`

This module contains the complete pipeline to train a new segmentation model from scratch. It handles data preparation, model training (using 5-fold cross-validation), performance evaluation, and exporting the final model.

**For detailed instructions on how to run the full training pipeline, please see the [train_module/README.md](./train_module/README.md).**

### 🧠 `inference_module/`

This module is used to run inference with a pre-trained model. It manages model retrieval from a server, prepares the input data, and runs the segmentation process to generate prediction masks.

**For detailed instructions on how to run the inference pipeline, please see the [inference_module/README.md](./inference_module/README.md).**
