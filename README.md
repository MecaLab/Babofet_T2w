# Babofet_T2w: Fetal Brain MRI Processing Pipeline

This project provides a complete, end-to-end pipeline for processing fetal baboons T2-weighted (T2w) MRI scans. The workflow starts with raw, multi-slice MRI data and produces high-resolution 3D brain volumes, tissue segmentations, and finally, 3D cortical surface models. The pipeline is built upon a BIDS dataset format.

## Pipeline Overview

The project is organized into three main modules that are designed to be run in sequence. The output of one module serves as the input for the next.

You can run each module independently, but they are designed to work together in sequence for a complete processing workflow.

To do so, ensure that the output from one module is correctly placed in the expected input location for the next module, as defined in `configuration.py`.
Then you can just run the `run_them_all.sh <SUBJECT> <SESSION>` (eg, `./run_them_all.sh sub-Borgne ses-01`) script to execute the entire pipeline for that module.
Or if you want to run the modules one by one, you can follow the instructions in each module's `README.md` file.

## How to install ?

To set up the environment for this project, you can follow the steps below. This will ensure that you have all the necessary dependencies installed and that your paths are correctly configured.

```bash
# 1. Clone the repository and create virtual env using conda
git clone git@github.com:MecaLab/Babofet_T2w.git # or https://github.com/MecaLab/Babofet_T2w.git
conda create -n longiseg python=3.12
conda activate longiseg

# 2. Install PyTorch (https://pytorch.org/get-started/locally/)

pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cpu  # For Linux without GPU (Niolon)
# or 
pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cu126  # For Linux with GPU (Mesocentre)

# 3. Clone the LongiSeg repository and install it
git clone https://github.com/MIC-DKFZ/LongiSeg.git
cd LongiSeg
pip install -e .

# 4. Clone the Surface Processing repository and install it
cd ..
git clone https://github.com/fetpype/surface_processing
cd surface_processing
pip install -r requirements.txt

# 5. Set paths (Run these lines once to append to your .bashrc, make sur to replace the paths with the actual paths on your system)
echo 'export LongiSeg_raw="/envau/work/meca/data/babofet_DB/2024_new_stuff/LongiSeg_raw"' >> ~/.bashrc
echo 'export LongiSeg_preprocessed="/envau/work/meca/data/babofet_DB/2024_new_stuff/LongiSeg_preprocessed"' >> ~/.bashrc
echo 'export LongiSeg_results="/envau/work/meca/data/babofet_DB/2024_new_stuff/LongiSeg_trained_models"' >> ~/.bashrc

# 6. After editing the file, do
source ~/.bashrc # to activate the new paths
# an easy way to check if it works is to do:
conda activate longiseg # MANDATORY
echo $LongiSeg_raw  # it will display the path you set 

# 7. Install the required packages for this project
cd .. # if you are still in the LongiSeg directory, go back to the root of the project
pip install -r requirements.txt  # Install the required Python packages for the project
chmod u+x run_them_all.sh  # Make the main script executable
```

**Workflow:**

1.  🧠 **`nifty_module/`**
    -   **Input**: Raw, multi-slice T2w NIfTI files.
    -   **Process**: This module is responsible for the 3D reconstruction of the fetal brain MRI. It uses **NiftyMIC** to take multiple low-resolution 2D slices and reconstruct them into a single high-resolution, motion-corrected 3D volume. This step is crucial for correcting fetal and maternal movement during the scan.
    -   **Output**: A 3D brain volume (`..._rec-niftymic_desc-brainbg_T2w.nii.gz`).

2.  🎨 **`segmentation_module/`**
    -   **Input**: The 3D reconstructed brain volume from the `nifty_module`.
    -   **Process**: This module performs tissue segmentation on the reconstructed 3D volume. It utilizes **LongiSeg**, a deep learning-based tool, to classify different brain tissues such as gray matter, white matter, and cerebrospinal fluid (CSF).
    -   **Output**: A 3D segmentation mask (`..._desc-longiseg_dseg.nii.gz`).

3.  ✨ **`extraction_module/`**
    -   **Input**: The 3D segmentation mask from the `segmentation_module`.
    -   **Process**: The final module in the pipeline is for surface extraction. It takes the segmentation mask, registers an atlas to the subject's brain, splits the brain into left and right hemispheres, and then extracts the cortical surfaces, particularly the inner surface of the cortical plate (the future white matter surface).
    -   **Output**: 3D surface files for each hemisphere (`..._hemi-L_white.surf.gii` and `..._hemi-R_white.surf.gii`).

---
## Additional Scripts

### `bids_script/`
This folder contains helper scripts for organizing and managing data according to the Brain Imaging Data Structure (BIDS) format. This ensures that the data is standardized and easily shareable.

## Configuration
The file `configuration.py` contains all the paths for the BIDS dataset, as well as for the inputs and outputs of the different modules. It is the main configuration file for the entire pipeline.

## How to Use

Each module contains its own set of scripts and a detailed `README.md` file with specific instructions on how to run its pipeline.

To process data from start to finish, run the modules in the following order:

1.  **Navigate to `nifty_module/`** and follow its README to reconstruct your raw MRI data.
2.  **Navigate to `segmentation_module/`** and follow its README to segment the reconstructed volumes.
3.  **Navigate to `extraction_module/`** and follow its README to extract the cortical surfaces from the segmentations.