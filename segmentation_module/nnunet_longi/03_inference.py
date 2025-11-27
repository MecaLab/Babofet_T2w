import os
import nibabel as nib
import sys
import subprocess
import numpy as np

sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg

def prepare_longitudinal_inference(input_folder, prepared_folder):
    if not os.path.exists(prepared_folder):
        os.makedirs(prepared_folder)

    for file_t in os.listdir(input_folder):
        if "0000" in file_t:
            case_name = file_t.replace("_0000.nii.gz", "")
            file_t_path = os.path.join(input_folder, file_t)
            file_t1_path = os.path.join(input_folder, f"{case_name}_0001.nii.gz")

            image_t1 = nib.load(file_t1_path)
            data_t1 = image_t1.get_fdata()
            seg_t1 = np.zeros_like(data_t1)
            nib.save(
                nib.Nifti1Image(seg_t1, image_t1.affine, image_t1.header),
                os.path.join(prepared_folder, f"{case_name}_0002.nii.gz")
            )

            os.system(f"cp {file_t_path} {os.path.join(prepared_folder, f'{case_name}_0000.nii.gz')}")
            os.system(f"cp {file_t1_path} {os.path.join(prepared_folder, f'{case_name}_0001.nii.gz')}")

    print(f"t-1 segmentations prepared.\nSaved in {prepared_folder}")


def prepare_t1_for_prediction(prepared_folder, temp_t1_input):
    if not os.path.exists(temp_t1_input):
        os.makedirs(temp_t1_input)

    for file in os.listdir(prepared_folder):
        if "0001" in file:
            case_name = file.replace("_0001.nii.gz", "")
            file_t1_path = os.path.join(prepared_folder, file)

            os.system(f"cp {file_t1_path} {os.path.join(temp_t1_input, f'{case_name}_0000.nii.gz')}")

            img = nib.load(file_t1_path)
            zeros = np.zeros_like(img.get_fdata())
            nib.save(
                nib.Nifti1Image(zeros, img.affine, img.header),
                os.path.join(temp_t1_input, f"{case_name}_0001.nii.gz")
            )
            nib.save(
                nib.Nifti1Image(zeros, img.affine, img.header),
                os.path.join(temp_t1_input, f"{case_name}_0002.nii.gz")
            )
    print(f"T2w images prepared for prediction.\nSaved in {temp_t1_input}")


def create_helper_script(helper_script_path):
    """
    Crée un script Python helper pour les opérations appelées par SLURM.
    """
    helper_content = f"""#!/usr/bin/env python3
\"\"\"
Script helper pour l'inférence longitudinale nnUNet.
Appelé par le job SLURM pour manipuler les fichiers.
\"\"\"

import argparse
import shutil
from pathlib import Path
import nibabel as nib
import numpy as np


def update_channel2(input_folder, pred_t1_folder):
    \"\"\"Met à jour le canal 2 avec les prédictions de t-1.\"\"\"
    input_folder = Path(input_folder)
    pred_t1_folder = Path(pred_t1_folder)

    updated = 0
    total = 0

    for file_t in input_folder.glob("*_0000.nii.gz"):
        case_name = file_t.name.replace("_0000.nii.gz", "")
        total += 1

        pred_file = pred_t1_folder / f"{{case_name}}_t1.nii.gz"

        if pred_file.exists():
            shutil.copy(pred_file, input_folder / f"{{case_name}}_0002.nii.gz")
            updated += 1
            print(f"✓ {{case_name}}: canal 2 mis à jour")
        else:
            print(f"⚠️  {{case_name}}: prédiction t-1 non trouvée")

    print(f"\\n✓ {{updated}}/{{total}} canaux 2 mis à jour")


def ensure_channel2(input_folder):
    \"\"\"Crée le canal 2 avec des zéros s'il n'existe pas.\"\"\"
    input_folder = Path(input_folder)

    created = 0

    for file_t in input_folder.glob("*_0000.nii.gz"):
        case_name = file_t.name.replace("_0000.nii.gz", "")
        file_canal2 = input_folder / f"{{case_name}}_0002.nii.gz"

        if not file_canal2.exists():
            img = nib.load(file_t)
            zeros = np.zeros_like(img.get_fdata())
            nib.save(
                nib.Nifti1Image(zeros, img.affine),
                file_canal2
            )
            created += 1
            print(f"⚠️  {{case_name}}: canal 2 créé avec zéros")

    if created > 0:
        print(f"\\n⚠️  {{created}} canaux 2 créés avec zéros (performances dégradées)")
    else:
        print("\\n✓ Tous les canaux 2 présents")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", required=True, choices=["update_channel2", "ensure_channel2"])
    parser.add_argument("--input", required=True, help="Dossier d'entrée")
    parser.add_argument("--pred_t1", help="Dossier des prédictions t-1 (pour mode update_channel2)")

    args = parser.parse_args()

    if args.mode == "update_channel2":
        if not args.pred_t1:
            raise ValueError("--pred_t1 requis pour mode update_channel2")
        update_channel2(args.input, args.pred_t1)
    elif args.mode == "ensure_channel2":
        ensure_channel2(args.input)
"""

    helper_script_path.parent.mkdir(exist_ok=True, parents=True)

    with open(helper_script_path, "w", encoding="utf-8") as f:
        f.write(helper_content)

    os.chmod(helper_script_path, 0o755)
    print(f"✓ Script helper créé : {helper_script_path}")

def write_slurm_cascade_prediction(filename):
    slurm_content = f"""#!/bin/bash
#SBATCH --account='b391'
#SBATCH --partition=volta
#SBATCH --gres=gpu:1
#SBATCH --time=10:00
#SBATCH -c 1
#SBATCH -o predict_nnunet_%j.out
#SBATCH -e predict_nnunet_%j.err

module purge
module load userspace/all
module load gcc/14.1.0
module load cuda/12.4

source ~/.bashrc
conda activate nnunet

echo "=========================================="
echo "INFÉRENCE LONGITUDINALE EN CASCADE"
echo "=========================================="

echo ""
echo "ÉTAPE 1: Prédiction des segmentations t-1"
echo "------------------------------------------"

# Prédire les segmentations de t-1
nnUNetv2_predict -i {temp_t1_input} -o {temp_t1_output} -d {dataset_id} -c 3d_fullres -tr {trainer} -f all

"""
    with open(filename, "w", encoding="utf-8") as slurm_file:
        slurm_file.write(slurm_content)

    os.chmod(filename, 0o700)


if __name__ == "__main__":
    dataset_id = int(sys.argv[1])
    name = sys.argv[2]
    trainer = sys.argv[3]  # "nnUNetTrainerBias_Xepochs"

    if dataset_id < 10:
        dataset_name = f"Dataset00{dataset_id}_{name}"
    elif dataset_id < 100:
        dataset_name = f"Dataset0{dataset_id}_{name}"
    else:
        dataset_name = f"Dataset{dataset_id}_{name}"

    input_folder = os.path.join(cfg.NNUNET_RAW_PATH, dataset_name, "imagesTs")

    output_folder = os.path.join(cfg.CODE_PATH, f"snapshots/nnunet_longi/pred_dataset_{dataset_id}")

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    prepared_folder = os.path.join(output_folder, "prepared_t1_seg")
    temp_t1_input = os.path.join(output_folder, "temp_t1_input")
    temp_t1_output = os.path.join(output_folder, "temp_t1_predictions")

    helper_script_path = os.path.join(cfg.CODE_PATH, "segmentation_module/nnunet_longi/helper.py")

    create_helper_script(helper_script_path)

    exit()

    prepare_longitudinal_inference(input_folder, prepared_folder)
    # cascade mode
    prepare_t1_for_prediction(prepared_folder, temp_t1_input)

    slurm_filename = "slurm_files/nnunet_longitudinal_prediction.slurm"
    write_slurm_cascade_prediction(slurm_filename)
    subprocess.run(["sbatch", slurm_filename])

