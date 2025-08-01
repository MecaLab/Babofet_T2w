import os
import subprocess
import sys
import shutil
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg


def write_slurm_file(input_folder, output_folder, dataset_id, trainer):
    filename = "slurm_files/nnunet_prediction.slurm"
    slurm_content = f"""#!/bin/bash


#SBATCH --account='b219'
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

nnUNetv2_predict -i {input_folder} -o {output_folder} -d {dataset_id} -c 3d_fullres -tr {trainer} -f all --save_probabilities

"""
    with open(filename, "w", encoding="utf-8") as slurm_file:
        slurm_file.write(slurm_content)

    os.chmod(filename, 0o700)


if __name__ == "__main__":
    dataset_id = sys.argv[1]
    trainer = sys.argv[2] # "nnUNetTrainerBias_Xepochs"

    input_folder = "/scratch/lbaptiste/Babofet_T2w/pred_nnunet/"

    output_folder = f"/scratch/lbaptiste/Babofet_T2w/snapshots/nnunet_res/pred_dataset_{dataset_id}"

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    subject_sessions = {
        "Bibi": ["ses04", "ses05", "ses06", "ses09"],
        "Borgne": ["ses04", "ses05", "ses06", "ses10"],
        "Filoutte": ["ses06", "ses07", "ses09", "ses10"],
        "Fabienne": ["ses07", "ses09"],
        # "Aziza": ["ses02", "ses03", "ses04", "ses05", "ses06", "ses07", "ses08", "ses09", "ses10"],
        # "Forme": ["ses02", "ses03", "ses05", "ses06", "ses07", "ses08", "ses09", "ses10"],
    }

    mode_dataset = "debiased-2"  # "masked" or "unmasked" or "debiased-2"

    for subject, sessions in subject_sessions.items():
        print(f"Processing subject: {subject}")
        if mode_dataset == "unmasked" or mode_dataset == "debiased-2":
            input_path_3d_stacks = os.path.join(cfg.DATA_PATH, subject)
        elif mode_dataset == "masked":
            input_path_3d_stacks = os.path.join(cfg.BOUNTI_PATH, "svrtk_BOUNTI/input_SRR_niftymic/haste", subject)
        else:
            raise ValueError(f"Unknown mode_dataset: {mode_dataset}")

        for session in sessions:
            print(f"\tProcessing session: {session}")
            if mode_dataset == "unmasked" or mode_dataset == "debiased-2":
                input_path_3d_stack = os.path.join(input_path_3d_stacks, session, "recons_rhesus/recon_template_space/srr_template_debiased.nii.gz")
            elif mode_dataset == "masked":
                input_path_3d_stack = os.path.join(input_path_3d_stacks, session, "reo-SVR-output-brain_rhesus.nii.gz")
            else:
                raise ValueError(f"Unknown mode_dataset: {mode_dataset}")

            output_path_3d_stack = os.path.join(input_folder, f"{subject}_{session}_0000.nii.gz")
            if os.path.exists(output_path_3d_stack):
                print(f"\t\tOutput file {output_path_3d_stack} already exists, skipping copy.")
                continue
            shutil.copy2(input_path_3d_stack, output_path_3d_stack)

    print("Starting inference")

    write_slurm_file(input_folder, output_folder, dataset_id, trainer)
    subprocess.run(["sbatch", "slurm_files/nnunet_prediction.slurm"])