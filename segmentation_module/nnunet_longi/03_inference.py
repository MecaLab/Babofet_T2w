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

    prepare_longitudinal_inference(input_folder, prepared_folder)
    # cascade mode
    prepare_t1_for_prediction(prepared_folder, temp_t1_input)

    slurm_filename = "slurm_files/nnunet_longitudinal_prediction.slurm"
    write_slurm_cascade_prediction(slurm_filename)
    subprocess.run(["sbatch", slurm_filename])

