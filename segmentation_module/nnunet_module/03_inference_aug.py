import os
import subprocess
import sys
import random
import nibabel as nib
import numpy as np
from scipy.ndimage import rotate
import json
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg

def augment_volume(img_np):
    transforms = {
        'angle': 0,
        'axes': (0, 1),
        'flip_0': False,
        'flip_1': False,
        'flip_2': False
    }
    # Rotation légère
    angle = random.uniform(-5, 5)
    img_np = rotate(img_np, angle, axes=(0, 1), reshape=False, order=1)
    transforms['angle'] = angle
    # Flips aléatoires
    if random.random() > 0.5:
        img_np = img_np[::-1, :, :]
        transforms['flip_0'] = True
    if random.random() > 0.5:
        img_np = img_np[:, ::-1, :]
        transforms['flip_1'] = True
    if random.random() > 0.5:
        img_np = img_np[:, :, ::-1]
        transforms['flip_2'] = True
    # Bruit léger
    img_np = img_np + np.random.normal(0, 0.01, img_np.shape)
    return img_np, transforms

def reverse_transform(pred_np, transforms):
    # Inverser les flips
    if transforms['flip_0']:
        pred_np = pred_np[::-1, :, :]
    if transforms['flip_1']:
        pred_np = pred_np[:, ::-1, :]
    if transforms['flip_2']:
        pred_np = pred_np[:, :, ::-1]
    # Inverser la rotation
    if transforms['angle'] != 0:
        pred_np = rotate(pred_np, -transforms['angle'], axes=transforms['axes'], reshape=False, order=1)
    return pred_np

def make_augmented_inputs(input_folder, N=10):
    transforms_dict = {}
    for filename in os.listdir(input_folder):
        if not filename.endswith(".nii.gz"):
            continue
        path = os.path.join(input_folder, filename)
        img = nib.load(path)
        img_np = img.get_fdata()
        affine = img.affine
        transforms_dict[filename] = []
        for i in range(N):
            aug_folder = f"{input_folder}_aug{i}"
            os.makedirs(aug_folder, exist_ok=True)
            aug_np, transforms = augment_volume(img_np.copy())
            out_path = os.path.join(aug_folder, filename)
            nib.save(nib.Nifti1Image(aug_np, affine), out_path)
            transforms_dict[filename].append(transforms)
    # Sauvegarder les transformations dans un fichier JSON
    with open(os.path.join(input_folder, 'transforms.json'), 'w') as f:
        json.dump(transforms_dict, f)
    return transforms_dict

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

# Prédire pour chaque augmentation
"""
    for i in range(N):
        aug_input = f"{input_folder}_aug{i}"
        aug_output = os.path.join(output_folder, f"aug{i}")
        os.makedirs(aug_output, exist_ok=True)
        slurm_content += f"nnUNetv2_predict -i {aug_input} -o {aug_output} -d {dataset_id} -c 3d_fullres -tr {trainer} -f all --save_probabilities\n"
    # Ajouter l'appel au script Python pour inverser les transformations
    slurm_content += f"python3 {os.path.abspath(__file__)} --reverse {input_folder} {output_folder} {N}\n"
    with open(filename, "w", encoding="utf-8") as slurm_file:
        slurm_file.write(slurm_content)
    os.chmod(filename, 0o700)

def reverse_all_transforms(input_folder, output_folder, N=10):
    # Charger les transformations
    with open(os.path.join(input_folder, 'transforms.json'), 'r') as f:
        transforms_dict = json.load(f)
    # Pour chaque fichier et chaque augmentation
    for filename in transforms_dict:
        for i in range(N):
            aug_output = os.path.join(output_folder, f"aug{i}")
            pred_path = os.path.join(aug_output, filename)
            if os.path.exists(pred_path):
                pred_img = nib.load(pred_path)
                pred_np = pred_img.get_fdata()
                transforms = transforms_dict[filename][i]
                pred_np_reversed = reverse_transform(pred_np, transforms)
                nib.save(nib.Nifti1Image(pred_np_reversed, pred_img.affine), pred_path)
                print(f"Reversed transforms for {filename} (augmentation {i})")

if __name__ == "__main__":
    if "--reverse" in sys.argv:
        input_folder = sys.argv[2]
        output_folder = sys.argv[3]
        N = int(sys.argv[4])
        reverse_all_transforms(input_folder, output_folder, N)
    else:
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
        subprocess.run(["sbatch", slurm_filename])
