import os
import subprocess
import sys
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg


def write_slurm_file(input_folder, output_folder, filename, partition, dataset_id, trainer, model_path):
    cross_val_path = os.path.join(model_path, f"crossval_results_folds_0_1_2_3_4")
    pkl_file = os.path.join(cross_val_path, "postprocessing.pkl")
    plans_json = os.path.join(cross_val_path, "plans.json")
    slurm_content = f"""#!/bin/bash

#SBATCH --account='b219'
#SBATCH --partition={partition}
#SBATCH --gres=gpu:1
#SBATCH --time=02:00:00
#SBATCH -c 12
#SBATCH -o predict_nnunet_%j.out
#SBATCH -e predict_nnunet_%j.err

module purge
module load userspace/all
module load gcc/14.1.0
module load cuda/12.4

source ~/.bashrc
conda activate nnunet

nnUNetv2_predict -i {input_folder} -o {output_folder} -d {dataset_id} -c 3d_fullres -tr {trainer} -f 0 1 2 3 4 -p nnUNetPlans
nnUNetv2_apply_postprocessing -i {output_folder} -o {output_folder} -pp_pkl_file {pkl_file} -np 8 -plans_json {plans_json}

"""
    with open(filename, "w", encoding="utf-8") as slurm_file:
        slurm_file.write(slurm_content)

    os.chmod(filename, 0o700)


def copy_files(main_path, output_path, subjects):
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    for subject in subjects:
        subject_path = os.path.join(main_path, subject)

        for session in os.listdir(subject_path):
            session_path = os.path.join(subject_path, session)

            t2w_biased = os.path.join(session_path, "recons_rhesus/recon_template_space/srr_template.nii.gz")
            t2w_biased_dest = os.path.join(output_path, f"{subject}_{session}_0000.nii.gz")

            if not os.path.exists(t2w_biased_dest):
                subprocess.run(["cp", t2w_biased, t2w_biased_dest])

            t2w_debiased = os.path.join(session_path, "recons_rhesus/recon_template_space/srr_template_debiased.nii.gz")
            t2w_debiased_dest = os.path.join(output_path, f"{subject}_{session}_0001.nii.gz")

            if not os.path.exists(t2w_debiased_dest):
                subprocess.run(["cp", t2w_debiased, t2w_debiased_dest])

        print(f"End for {subject}")


if __name__ == "__main__":
    dataset_id = int(sys.argv[1])
    name = sys.argv[2]
    trainer = sys.argv[3]  # "nnUNetTrainerBias_Xepochs
    partition = sys.argv[4]  # e.g., "volta", "kepler", etc

    looking_for = ["Borgne_ses06"]

    dataset_name = f"Dataset{dataset_id:03d}_{name}"

    input_dir_3d_vol = "inference_all"

    if not os.path.exists(input_dir_3d_vol):
        os.makedirs(input_dir_3d_vol)
    
    # copy_files(cfg.DATA_PATH, input_dir_3d_vol, subjects=["Bibi"])

    tmp_path = os.path.join(input_dir_3d_vol, "pred_tmp")
    if not os.path.exists(tmp_path):
        os.makedirs(tmp_path)

    for sess in looking_for:
        curr_sess = sess.split("_")[-1][3:]
        print(curr_sess)
        exit()



    model_path = os.path.join(cfg.NNUNET_RESULTS_PATH, dataset_name, f"{trainer}__nnUNetPlans__3d_fullres")

    output_folder = os.path.join(input_dir_3d_vol, f"{dataset_id}_segmentations")  # output segmentations

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    print("Starting inference")
    filename = "slurm_files/nnunet_prediction_all.slurm"
    write_slurm_file(input_dir_3d_vol, output_folder, filename, partition, dataset_id, trainer, model_path)
    subprocess.run(["sbatch", filename])

