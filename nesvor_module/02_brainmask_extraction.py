import os
import sys
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg
import subprocess

from tools import data_organization as tdo


def write_slurm_file(input_path, output_path, input_file, output_file):
    filename = "nesvor_bm_extraction.slurm"
    slurm_content = f"""#!/bin/sh

#SBATCH --account='a391'
#SBATCH --partition=volta
#SBATCH --gres=gpu:1
#SBATCH --time=00:05:00
#SBATCH -o tmp.out
#SBATCH -e tmp.err

module load userspace/all
module load cuda/11.6

echo "Running on: $SLURM_NODELIST"

singularity exec --nv \\
    -B "{input_path}":/data \\
    -B "{output_path}":/output \\
     /scratch/lbaptiste/softs/nesvor_latest.sif \\
    nesvor segment-stack \\
        --input-stacks "/data/{input_file}" \\
        --output-stack-masks "/output/{output_file}"
    """

    with open(filename, "w", encoding="utf-8") as slurm_file:
        slurm_file.write(slurm_content)

    os.chmod(filename, 0o700)


if __name__ == "__main__":

    base_path = cfg.MESO_OUTPUT_PATH

    subject_IDs = os.listdir(base_path)
    subject_processed_haste = list()
    subject_processed_truefisp = list()

    for subject in subject_IDs:
        print("Starting {}".format(subject))

        dir_list = os.listdir(os.path.join(base_path, subject, "denoising"))
        haste_files = list()
        truefisp_files = list()

        for d in dir_list:
            d_lower = d.lower()
            if "haste" in d_lower:
                haste_files.append(d)
            if "trufi" in d_lower:
                truefisp_files.append(d)

        subj_output_dir = os.path.join(base_path, subject)

        # Haste files
        if len(haste_files) > 0:
            print("\tStarting HASTE {}".format(subject))
            haste_subj_output_dir = os.path.join(subj_output_dir, "haste")
            bm_haste_subj_output_dir = os.path.join(subj_output_dir, "brainmask")

            if not os.path.exists(haste_subj_output_dir):
                os.mkdir(haste_subj_output_dir)
            if not os.path.exists(bm_haste_subj_output_dir):
                os.mkdir(bm_haste_subj_output_dir)

            for f in haste_files:
                nifti_filename, nifti_full_path = f, os.path.join(subj_output_dir, f)
                # nifti_filename, nifti_full_path = tdo.file_name_from_path(base_path, subject, f)
                s_nifti_filename = nifti_filename.split(".")
                bm_nifti_filename = s_nifti_filename[0] + "_brainmask.nii"

                if not os.path.exists(os.path.join(bm_haste_subj_output_dir, bm_nifti_filename)):

                    write_slurm_file(input_path=nifti_full_path, output_path=bm_haste_subj_output_dir,
                                     input_file=nifti_filename, output_file=bm_nifti_filename)

                    exit()

                    subprocess.run(["sbatch", "nesvor.slurm"])
                    print("\t\tComputing HASTE {}".format(bm_nifti_filename))
                else:
                    print("\t\tSkiped {}".format(bm_nifti_filename))

            print("\tEnding HASTE {}".format(subject))

        # Truefisp files
        if len(truefisp_files) > 0:
            print("\tStarting TRUEFISP {}".format(subject))
            truefisp_subj_output_dir = os.path.join(subj_output_dir, "truefisp")
            bm_truefisp_subj_output_dir = os.path.join(subj_output_dir, "brainmask")

            if not os.path.exists(truefisp_subj_output_dir):
                os.mkdir(truefisp_subj_output_dir)
            if not os.path.exists(bm_truefisp_subj_output_dir):
                os.mkdir(bm_truefisp_subj_output_dir)

            for f in truefisp_files:
                nifti_filename, nifti_full_path = tdo.file_name_from_path(base_path, subject, f)
                s_nifti_filename = nifti_filename.split(".")
                bm_nifti_filename = s_nifti_filename[0] + "_brainmask.nii"

                if not os.path.exists(os.path.join(bm_truefisp_subj_output_dir, bm_nifti_filename)):

                    write_slurm_file(input_path=nifti_full_path, output_path=bm_truefisp_subj_output_dir,
                                     input_file=nifti_filename, output_file=bm_nifti_filename)

                    subprocess.run(["sbatch", "nesvor.slurm"])
                    print("\t\tComputing TRUEFISP {}".format(bm_nifti_filename))
                else:
                    print("\t\tSkiped {}".format(bm_nifti_filename))
            print("\tEnding TRUEFISP {}".format(subject))

        print("Ending {}\n".format(subject))