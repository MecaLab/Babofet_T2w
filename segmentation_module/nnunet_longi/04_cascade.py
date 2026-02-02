import os
import subprocess
import sys
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg

def write_slurm_file(input_folder, output_folder, filename, dataset_id, trainer, model_path, partition="volta"):
    cross_val_path = os.path.join(model_path, f"crossval_results_folds_0_1_2_3_4")
    pkl_file = os.path.join(cross_val_path, "postprocessing.pkl")
    plans_json = os.path.join(cross_val_path, "plans.json")
    slurm_content = f"""#!/bin/bash
    
#SBATCH --account='b391'
#SBATCH --partition={partition}
#SBATCH --gres=gpu:1
#SBATCH --time=30:00
#SBATCH -c 1
#SBATCH -o predict_nnunet_%j.out
#SBATCH -e predict_nnunet_%j.err

module purge
module load userspace/all
module load gcc/14.1.0
module load cuda/12.4

source ~/.bashrc
conda activate longiseg_new
"""

    with open(filename, "w", encoding="utf-8") as slurm_file:
        slurm_file.write(slurm_content)

    os.chmod(filename, 0o700)

def organize_files(subject, sessions, input_path, output_path):
    seg_dataset = "gt_dataset_2"
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    for subject_ in os.listdir(input_path):
        if subject_ != subject:
            continue

        subject_input_dir = os.path.join(input_path, subject)
        for session in os.listdir(subject_input_dir):
            if session not in sessions:
                continue
            dir_sess = os.path.join(output_path, f"pred_{session}")
            if not os.path.exists(dir_sess):
                os.makedirs(dir_sess)

            prev_sess = f"ses{int(session[-2:]) - 1:02d}"
            print(session, prev_sess)

            curr_vol = os.path.join(subject_input_dir, session,
                                    "recons_rhesus/recon_template_space/srr_template_debiased.nii.gz")
            prev_vol = os.path.join(subject_input_dir, prev_sess,
                                    "recons_rhesus/recon_template_space/srr_template_debiased.nii.gz")
            prev_seg = os.path.join(cfg.BASE_PATH, seg_dataset, "train_dataset", f"{subject}_{prev_sess}.nii.gz")
            if not os.path.exists(prev_seg):
                prev_seg = os.path.join(cfg.BASE_PATH, seg_dataset, "test_dataset", f"{subject}_{prev_sess}.nii.gz")
            if not os.path.exists(prev_seg):
                prev_seg = None

            output_curr_vol = os.path.join(dir_sess, f"{subject}_{session}_0000.nii.gz")
            output_prev_vol = os.path.join(dir_sess, f"{subject}_{session}_0001.nii.gz")

            os.system(f"cp {curr_vol} {output_curr_vol}")
            os.system(f"cp {prev_vol} {output_prev_vol}")
            if prev_seg:
                print("OUI", prev_seg)
                output_prev_seg = os.path.join(dir_sess, f"{subject}_{session}_0002.nii.gz")
                os.system(f"cp {prev_seg} {output_prev_seg}")



if __name__ == "__main__":
    input_path = cfg.DATA_PATH
    output_path = "data_nnunet_longi/Borgne"
    sessions = ["ses06", "ses07", "ses08", "ses09", "ses10"]
    organize_files("Borgne", sessions, input_path, output_path)