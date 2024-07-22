import os
import sys
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg
import subprocess

from tools import data_organization as tdo


def write_slurm_file(input_path, output_path, input_file, output_file):
    filename = "nesvor.slurm"
    slurm_content = f"""#!/bin/sh

#SBATCH --account='a391'
#SBATCH --partition=volta
#SBATCH --gres=gpu:1
#SBATCH --time=00:05:00
#SBATCH -o tmp.out
#SBATCH -e tmp.err

module load userspace/all
module load cuda/11.6

singularity exec --nv -B '{input_path}':/data -B '{output_path}':/output softs/nesvor_latest.sif nesvor segment-stack --input-stacks '/data/{input_file}' --output-stack-masks '/output/{output_file}'
echo "Running on: $SLURM_NODELIST"
    """

    with open(filename, "w", encoding="utf-8") as slurm_file:
        slurm_file.write(slurm_content)

    os.chmod(filename, 0o700)


if __name__ == "__main__":

    base_path = cfg.MESO_DATA_PATH

    subject_IDs = os.listdir(base_path)
    subject_IDs.sort()
    print('subjects to be processed')
    print(subject_IDs)
    subject_processed_haste = list()
    subject_processed_truefisp = list()

    for subject in subject_IDs:
        subj_output_dir = os.path.join(cfg.MESO_OUTPUT_PATH, subject)
        if not os.path.exists(subj_output_dir):
            os.makedirs(subj_output_dir)

        print("----------------------" + subject)

        dir_list = os.listdir(os.path.join(base_path, subject, "scans"))
        haste_files = list()
        truefisp_files = list()

        for d in dir_list:
            d_lower = d.lower()
            if "haste" in d_lower:
                haste_files.append(d)
            if "trufi" in d_lower:
                truefisp_files.append(d)

        if len(haste_files) > 0:
            haste_subj_output_dir = os.path.join(subj_output_dir, "haste")
            bm_haste_subj_output_dir = os.path.join(subj_output_dir, "brainmask")

            if not os.path.exists(haste_subj_output_dir):
                os.mkdir(haste_subj_output_dir)
            if not os.path.exists(bm_haste_subj_output_dir):
                os.mkdir(bm_haste_subj_output_dir)

            # cmd1 = ["--input-stacks"]
            # cmd2 = ["--output-stack-masks"]

            cmd1 = list()
            cmd2 = list()

            already_done = list()
            for f in haste_files:
                nifti_filename, nifti_full_path = tdo.file_name_from_path(base_path, subject, f)
                s_nifti_filename = nifti_filename.split(".")
                bm_nifti_filename = s_nifti_filename[0] + "_brainmask.nii"
                bm_output_file = os.path.join(bm_haste_subj_output_dir, bm_nifti_filename)

                if os.path.exists(bm_output_file):
                    already_done.append(True)
                else:
                    cmd1.append(nifti_filename)
                    cmd2.append(bm_nifti_filename)

            for input, output in zip(cmd1, cmd2):
                print(input, output)

                write_slurm_file(input_path=nifti_full_path, output_path=bm_haste_subj_output_dir,
                                 input_file=input, output_file=output)
                break

            break


# input_path = "/scratch/lbaptiste/data/dataset/babofet/subjects/sub-Aziza_ses-01/scans/10-T2_HASTE_AX2/resources/NIFTI/files"
# output_path = "/scratch/lbaptiste/data/dataset/babofet/output"
# input_file = "sub-Aziza_ses-01_T2_HASTE_AX2_10.nii"
# output_file = "mask.nii.gz"
#
# # Contenu du fichier SLURM
# slurm_script_content = f"""#!/bin/sh
#
# #SBATCH --account='a391'
# #SBATCH --partition=volta
# #SBATCH --gres=gpu:1
# #SBATCH --time=00:30:00
# #SBATCH -o tmp.out
# #SBATCH -e tmp.err
#
# module load userspace/all
# module load cuda/11.6
#
# singularity exec --nv -B "{input_path}":/data -B "{output_path}":/output softs/nesvor_latest.sif nesvor segment-stack --input-stacks "/data/{input_file}" --output-stack-masks "/output/{output_file}"
#
# echo "Running on: $SLURM_NODELIST"
# """
#
# # Écrire le contenu dans le fichier nesvor.slurm
# slurm_script_path = "nesvor.slurm"
# with open(slurm_script_path, "w", encoding="utf-8") as file:
#     file.write(slurm_script_content)
#
# # Soumettre le job à SLURM
# subprocess.run(["sbatch", slurm_script_path])