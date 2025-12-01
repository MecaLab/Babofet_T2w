import os
import subprocess
import sys
import random
import nibabel as nib
import numpy as np
from scipy.ndimage import rotate
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg


def augment_volume(img_np):
    # Rotation légère
    angle = random.uniform(-5, 5)
    img_np = rotate(img_np, angle, axes=(0, 1), reshape=False, order=1)


    # Flips aléatoires
    if random.random() > 0.5:
        img_np = img_np[::-1, :, :]
    if random.random() > 0.5:
        img_np = img_np[:, ::-1, :]
    if random.random() > 0.5:
        img_np = img_np[:, :, ::-1]

    # Bruit léger
    img_np = img_np + np.random.normal(0, 0.01, img_np.shape)

    return img_np

def make_augmented_inputs(input_folder, N=10):
    for filename in os.listdir(input_folder):
        if not filename.endswith(".nii.gz"):
            continue

        path = os.path.join(input_folder, filename)
        img = nib.load(path)
        img_np = img.get_fdata()
        affine = img.affine

        for i in range(N):
            aug_folder = f"{input_folder}_aug{i}"
            os.makedirs(aug_folder, exist_ok=True)
            aug_np = augment_volume(img_np.copy())
            out_path = os.path.join(aug_folder, filename)
            nib.save(nib.Nifti1Image(aug_np, affine), out_path)

        print(f"Created {N} augmentations for {filename} at {aug_folder}")


def write_slurm_file(input_folder, output_folder, filename, dataset_id, trainer, N=10):
    slurm_content = f"""#!/bin/bash
    
#SBATCH --account='b391'
#SBATCH --partition=volta
#SBATCH --gres=gpu:1
#SBATCH --time=1:00:00
#SBATCH -c 1
#SBATCH -o predict_nnunet_%j.out
#SBATCH -e predict_nnunet_%j.err

module purge
module load userspace/all
module load gcc/14.1.0
module load cuda/12.4

source ~/.bashrc
conda activate nnunet
"""

    for i in range(N):
        aug_input = f"{input_folder}_aug{i}"
        aug_output = os.path.join(output_folder, f"aug{i}")
        os.makedirs(aug_output, exist_ok=True)
        slurm_content += f"nnUNetv2_predict -i {aug_input} -o {aug_output} -d {dataset_id} -c 3d_fullres -tr {trainer} -f all --save_probabilities\n"


    with open(filename, "w", encoding="utf-8") as slurm_file:
        slurm_file.write(slurm_content)


    os.chmod(filename, 0o700)


if __name__ == "__main__":
    dataset_id = int(sys.argv[1])
    name = sys.argv[2]
    trainer = sys.argv[3]

    N = 5


    if dataset_id < 10:
        dataset_name = f"Dataset00{dataset_id}_{name}"
    elif dataset_id < 100:
        dataset_name = f"Dataset0{dataset_id}_{name}"
    else:
        dataset_name = f"Dataset{dataset_id}_{name}"


    input_folder = os.path.join(cfg.NNUNET_RAW_PATH, dataset_name, "imagesTs")
    output_folder = os.path.join(cfg.CODE_PATH, f"snapshots/nnunet_res/pred_dataset_{dataset_id}")
    os.makedirs(output_folder, exist_ok=True)


    print("Creating augmented inputs...")
    make_augmented_inputs(input_folder, N=N)


    print("Writing SLURM file...")
    slurm_filename = "slurm_files/nnunet_prediction.slurm"
    write_slurm_file(input_folder, output_folder, slurm_filename, dataset_id, trainer, N=N)


    print("Submitting job to SLURM")
    #subprocess.run(["sbatch", slurm_filename])