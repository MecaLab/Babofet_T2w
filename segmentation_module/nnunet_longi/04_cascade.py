import os
import subprocess
import sys
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg


def write_cascade_slurm(filename, subject, sessions, output_path, model_path, dataset_id):
    cross_val_path = os.path.join(model_path, f"crossval_results_folds_0_1_2_3_4")
    pkl_file = os.path.join(cross_val_path, "postprocessing.pkl")
    plans_json = os.path.join(cross_val_path, "plans.json")
    sorted_sessions = sorted(sessions)
    abs_output_path = os.path.abspath(output_path)

    slurm_content = f"""#!/bin/bash

#SBATCH --account='b391'
#SBATCH --partition=volta
#SBATCH --gres=gpu:1
#SBATCH --time=02:00:00
#SBATCH -c 8
#SBATCH -o cascade_{subject}_%j.out
#SBATCH -e cascade_{subject}_%j.err

module purge
module load userspace/all
module load gcc/14.1.0
module load cuda/12.4

source ~/.bashrc
conda activate nnunet

BASE_DIR="{abs_output_path}"

"""
    # Génération de la boucle séquentielle pour la cascade
    for i, session in enumerate(sorted_sessions):
        slurm_content += f"""
echo "--- Processing {subject} {session} ---"
# Lancer la prédiction pour la session actuelle
nnUNetv2_predict -i $BASE_DIR/pred_{session} -o $BASE_DIR/pred_{session} -d {dataset_id} -tr nnUNetTrainerBias_1000epochs -c 3d_fullres -f 0 1 2 3 4 --save_probabilities
nnUNetv2_apply_postprocessing -i $BASE_DIR/pred_{session} -o $BASE_DIR/pred_{session} -pp_pkl_file {pkl_file} -np 8 -plans_json {plans_json}

"""
        # Si ce n'est pas la dernière session, on prépare le canal 0002 de la suivante (t+1)
        if i < len(sorted_sessions) - 1:
            next_session = sorted_sessions[i + 1]
            slurm_content += f"""
# Copier la prédiction actuelle vers le canal 0002 de la session suivante
cp $BASE_DIR/pred_{session}/{subject}_{session}.nii.gz $BASE_DIR/pred_{next_session}/{subject}_{next_session}_0002.nii.gz
"""

    with open(filename, "w", encoding="utf-8") as f:
        f.write(slurm_content)

    os.chmod(filename, 0o700)
    return filename

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
                output_prev_seg = os.path.join(dir_sess, f"{subject}_{session}_0002.nii.gz")
                os.system(f"cp {prev_seg} {output_prev_seg}")



if __name__ == "__main__":
    input_path = cfg.DATA_PATH

    subject = "Formule"
    output_path = f"data_nnunet_longi/{subject}"
    sessions = ["ses05", "ses06", "ses07", "ses08", "ses09"]
    trainer = "nnUNetTrainerBias_1000epochs"
    dataset_id = 20
    dataset_name = f"Dataset{dataset_id:03d}_tmp_longi"
    model_path = os.path.join(cfg.NNUNET_RESULTS_PATH, dataset_name, f"{trainer}__nnUNetPlans__3d_fullres")

    organize_files(subject, sessions, input_path, output_path)

    filename = f"slurm_files/cascade_{subject}.slurm"
    write_cascade_slurm(filename, subject, sessions, output_path, model_path, dataset_id=20)
    subprocess.run(["sbatch", filename])