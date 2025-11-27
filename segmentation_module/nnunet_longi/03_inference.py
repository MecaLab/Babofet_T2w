import os
import subprocess
import sys
from pathlib import Path
import nibabel as nib
import numpy as np

sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg


def prepare_t1_for_prediction(input_folder, temp_t1_folder):
    """
    Prépare les images t-1 pour prédiction (sans contexte longitudinal).
    Pour chaque cas, crée :
    - Canal 0 : image t-1
    - Canal 1 : zéros
    - Canal 2 : zéros
    """
    input_folder = Path(input_folder)
    temp_t1_folder = Path(temp_t1_folder)
    temp_t1_folder.mkdir(exist_ok=True, parents=True)

    cases_processed = []

    for file_t in input_folder.glob("*_0000.nii.gz"):
        case_name = file_t.name.replace("_0000.nii.gz", "")
        file_t1 = input_folder / f"{case_name}_0001.nii.gz"

        if not file_t1.exists():
            print(f"⚠️  {case_name}_0001.nii.gz non trouvé, cas ignoré")
            continue

        # Canal 0 : image t-1
        os.system(f"cp {file_t1} {temp_t1_folder / f'{case_name}_t1_0000.nii.gz'}")

        # Canaux 1 et 2 : zéros (pas d'info longitudinale pour prédire t-1)
        img = nib.load(file_t1)
        zeros = np.zeros_like(img.get_fdata())

        nib.save(
            nib.Nifti1Image(zeros, img.affine),
            temp_t1_folder / f"{case_name}_t1_0001.nii.gz"
        )
        nib.save(
            nib.Nifti1Image(zeros, img.affine),
            temp_t1_folder / f"{case_name}_t1_0002.nii.gz"
        )

        cases_processed.append(case_name)

    print(f"✓ {len(cases_processed)} cas préparés pour prédiction t-1")
    return cases_processed


def update_channel2_with_predictions(input_folder, pred_t1_folder, cases):
    """
    Met à jour le canal 2 avec les prédictions de t-1.
    """
    input_folder = Path(input_folder)
    pred_t1_folder = Path(pred_t1_folder)

    updated = 0
    for case_name in cases:
        pred_file = pred_t1_folder / f"{case_name}_t1.nii.gz"

        if pred_file.exists():
            # Remplacer le canal 2 par la prédiction t-1
            os.system(f"cp {pred_file} {input_folder / f'{case_name}_0002.nii.gz'}")
            updated += 1
        else:
            print(f"⚠️  Prédiction t-1 non trouvée pour {case_name}")

    print(f"✓ {updated}/{len(cases)} canaux 2 mis à jour avec prédictions t-1")
    return updated


def prepare_longitudinal_inference(images_ts_folder, prepared_folder):
    """
    Prépare les données pour l'inférence longitudinale.
    Crée les 3 canaux pour chaque cas (canal 2 initialement vide).
    """
    images_ts_folder = Path(images_ts_folder)
    prepared_folder = Path(prepared_folder)
    prepared_folder.mkdir(exist_ok=True, parents=True)

    all_files = list(images_ts_folder.glob("*_0000.nii.gz"))

    if not all_files:
        raise ValueError(f"Aucun fichier *_0000.nii.gz trouvé dans {images_ts_folder}")

    cases = []
    for file in all_files:
        case_name = file.name.replace("_0000.nii.gz", "")
        file_t1 = images_ts_folder / f"{case_name}_0001.nii.gz"

        if not file_t1.exists():
            print(f"⚠️  {case_name}_0001.nii.gz non trouvé, cas ignoré")
            continue

        # Canal 0 : image t
        os.system(f"cp {file} {prepared_folder / f'{case_name}_0000.nii.gz'}")

        # Canal 1 : image t-1
        os.system(f"cp {file_t1} {prepared_folder / f'{case_name}_0001.nii.gz'}")

        # Canal 2 : segmentation t-1 (initialement zéros)
        img_t1 = nib.load(file_t1)
        zeros = np.zeros_like(img_t1.get_fdata())
        nib.save(
            nib.Nifti1Image(zeros, img_t1.affine),
            prepared_folder / f"{case_name}_0002.nii.gz"
        )

        cases.append(case_name)

    print(f"✓ {len(cases)} cas préparés avec 3 canaux")
    return cases


def write_slurm_cascade_prediction(input_folder, output_folder, filename, dataset_id, trainer,
                                   temp_t1_input, temp_t1_output, helper_script):
    """
    Crée un script SLURM pour l'inférence en cascade.
    Appelle un script Python externe pour les opérations sur les fichiers.
    """
    slurm_content = f"""#!/bin/bash

#SBATCH --account='b391'
#SBATCH --partition=volta
#SBATCH --gres=gpu:1
#SBATCH --time=30:00
#SBATCH -c 1
#SBATCH -o predict_nnunet_longi_%j.out
#SBATCH -e predict_nnunet_longi_%j.err

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

echo ""
echo "ÉTAPE 2: Mise à jour du canal 2"
echo "------------------------------------------"

# Mettre à jour le canal 2 avec les prédictions t-1
python {helper_script} --mode update_channel2 --input {input_folder} --pred_t1 {temp_t1_output}

echo ""
echo "ÉTAPE 3: Prédiction finale avec contexte longitudinal"
echo "------------------------------------------"

# Prédiction finale avec les 3 canaux corrects
nnUNetv2_predict -i {input_folder} -o {output_folder} -d {dataset_id} -c 3d_fullres -tr {trainer} -f all --save_probabilities

echo ""
echo "=========================================="
echo "✓ Prédiction longitudinale terminée"
echo "Résultats dans: {output_folder}"
echo "=========================================="

"""
    with open(filename, "w", encoding="utf-8") as slurm_file:
        slurm_file.write(slurm_content)

    os.chmod(filename, 0o700)


def write_slurm_simple_prediction(input_folder, output_folder, filename, dataset_id, trainer,
                                  helper_script):
    """
    Version simple : suppose que le canal 2 existe ou le crée avec des zéros.
    """
    slurm_content = f"""#!/bin/bash

#SBATCH --account='b391'
#SBATCH --partition=volta
#SBATCH --gres=gpu:1
#SBATCH --time=30:00
#SBATCH -c 1
#SBATCH -o predict_nnunet_longi_%j.out
#SBATCH -e predict_nnunet_longi_%j.err

module purge
module load userspace/all
module load gcc/14.1.0
module load cuda/12.4

source ~/.bashrc
conda activate nnunet

echo "=========================================="
echo "INFÉRENCE LONGITUDINALE (MODE SIMPLE)"
echo "=========================================="

echo "⚠️  Canal 2 sera rempli de zéros si absent"
echo ""

# Vérifier et créer le canal 2 si nécessaire
python {helper_script} --mode ensure_channel2 --input {input_folder}

# Prédiction
nnUNetv2_predict -i {input_folder} -o {output_folder} -d {dataset_id} -c 3d_fullres -tr {trainer} -f all --save_probabilities

echo ""
echo "✓ Prédiction terminée"

"""
    with open(filename, "w", encoding="utf-8") as slurm_file:
        slurm_file.write(slurm_content)

    os.chmod(filename, 0o700)


def create_helper_script(helper_script_path, prepared_folder):
    """
    Crée un script Python helper pour les opérations appelées par SLURM.
    """
    helper_content = f"""#!/usr/bin/env python3
\"\"\"
Script helper pour l'inférence longitudinale nnUNet.
Appelé par le job SLURM pour manipuler les fichiers.
\"\"\"

import os
import argparse
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
            os.system(f"cp {{pred_file}} {{input_folder / f'{{{{case_name}}}}_0002.nii.gz'}}")
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

    helper_script_path = Path(helper_script_path)
    helper_script_path.parent.mkdir(exist_ok=True, parents=True)

    with open(helper_script_path, "w", encoding="utf-8") as f:
        f.write(helper_content)

    os.chmod(helper_script_path, 0o755)
    print(f"✓ Script helper créé : {helper_script_path}")


if __name__ == "__main__":
    dataset_id = int(sys.argv[1])
    name = sys.argv[2]
    trainer = sys.argv[3]
    mode = sys.argv[4] if len(sys.argv) > 4 else "cascade"  # "cascade" ou "simple"

    if dataset_id < 10:
        dataset_name = f"Dataset00{dataset_id}_{name}"
    elif dataset_id < 100:
        dataset_name = f"Dataset0{dataset_id}_{name}"
    else:
        dataset_name = f"Dataset{dataset_id}_{name}"

    images_ts_folder = os.path.join(cfg.NNUNET_RAW_PATH, dataset_name, "imagesTs")
    base_output_folder = os.path.join(cfg.CODE_PATH, f"snapshots/nnunet_longi/dataset_{dataset_id}")

    prepared_folder = os.path.join(base_output_folder, "prepared_input")
    output_folder = os.path.join(base_output_folder, "predictions")
    temp_t1_input = os.path.join(base_output_folder, "temp_t1_input")
    temp_t1_output = os.path.join(base_output_folder, "temp_t1_predictions")

    # Script helper Python
    helper_script = os.path.join(cfg.CODE_PATH, "segmentation_module/nnunet_longi/nnunet_longi_helper.py")

    print("=" * 60)
    print("INFÉRENCE NNUNET LONGITUDINALE")
    print("=" * 60)
    print(f"Dataset: {dataset_name}")
    print(f"Input: {images_ts_folder}")
    print(f"Output: {output_folder}")
    print(f"Mode: {mode}")
    print("=" * 60)

    # Créer le script helper
    create_helper_script(helper_script, prepared_folder)

    # Préparer les données (créer les 3 canaux avec canal 2 initialement vide)
    print("\nÉTAPE 1: Préparation des données...")
    cases = prepare_longitudinal_inference(images_ts_folder, prepared_folder)

    if mode == "cascade":
        print("\nÉTAPE 2: Préparation des images t-1 pour prédiction...")
        prepare_t1_for_prediction(prepared_folder, temp_t1_input)

    # Créer le dossier de sortie
    os.makedirs(output_folder, exist_ok=True)

    # Créer le script SLURM
    slurm_filename = "slurm_files/nnunet_longitudinal_prediction.slurm"
    os.makedirs("slurm_files", exist_ok=True)

    if mode == "cascade":
        print("\n→ Mode CASCADE : prédiction en 2 étapes (recommandé)")
        write_slurm_cascade_prediction(
            prepared_folder, output_folder, slurm_filename,
            dataset_id, trainer, temp_t1_input, temp_t1_output, helper_script
        )
    else:
        print("\n→ Mode SIMPLE : canal 2 rempli de zéros si absent")
        write_slurm_simple_prediction(
            prepared_folder, output_folder, slurm_filename,
            dataset_id, trainer, helper_script
        )

    print(f"\n✓ {len(cases)} cas préparés")
    print(f"✓ Script SLURM créé : {slurm_filename}")
    print(f"✓ Script helper créé : {helper_script}")

    print("\nLancement du job SLURM...")
    subprocess.run(["sbatch", slurm_filename])
    print("\n✓ Job soumis !")