import os
import sys
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg
import subprocess


def write_slurm_file(main_path, denoised_files):
    filename = "nifty_bm_extraction.slurm"
    slurm_content = f"""#!/bin/sh
    
#SBATCH --account='a391'
#SBATCH --partition=pascal
#SBATCH --gres=gpu:1
#SBATCH --time=01:00:00
#SBATCH -c 1
#SBATCH --mail-type=END
#SBATCH --mail-user=baptiste.LEROUX@univ-amu.fr
#SBATCH --mem-per-cpu=50G
#SBATCH -o tmp.out
#SBATCH -e tmp.err

module purge
module load userspace/all
module load cuda/10.2

echo "Running on: $SLURM_NODELIST"

MAIN_PATH="{main_path}"

INPUT_PATH="${{MAIN_PATH}}/denoising"
OUTPUT_PATH="${{MAIN_PATH}}/brainmask_niftymic"
"""

    slurm_content += "\n"

    for i, file in enumerate(denoised_files, start=1):
        slurm_content += f"INPUT_FILE{i}=\"{file}\"\n"

    input_stacks = " ".join([f"/data/$INPUT_FILE{i}" for i in range(1, len(denoised_files) + 1)])

    slurm_content += f"""
singularity exec \\
    -B "$INPUT_PATH":/data \\
    -B "$OUTPUT_PATH":/output \\
    /scratch/lbaptiste/softs/niftymic.multifact_latest.sif \\
    niftymic_segment_fetal_brains \\
            --filenames {input_stacks} \\
            --dir-output /output \\
            --verbose 2 \\
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

        if len(haste_files) > 0:
            print(f"\tStarting HASTE {subject}")

            haste_subj_output_dir = os.path.join(subj_output_dir, "haste")
            bm_haste_subj_output_dir = os.path.join(subj_output_dir, "brainmask_niftymic")

            if not os.path.exists(haste_subj_output_dir):
                os.mkdir(haste_subj_output_dir)
            if not os.path.exists(bm_haste_subj_output_dir):
                os.mkdir(bm_haste_subj_output_dir)

            anat_img = list()
            for f in haste_files:
                nifti_filename, nifti_full_path = f, os.path.join(subj_output_dir, "denoising")

                s_nifti_filename = nifti_filename.split(".")
                output_path = os.path.join(bm_haste_subj_output_dir, s_nifti_filename[0])

                if os.path.exists(os.path.join(nifti_full_path, nifti_filename)):
                    anat_img.append(nifti_filename)

            if not os.path.exists(output_path):
                print(f"\t\tComputing HASTE {subject}")
                write_slurm_file(
                    main_path=subj_output_dir,
                    denoised_files=anat_img,
                )
                subprocess.run(["sbatch", "nifty_bm_extraction.slurm"])
                print(f"\t\tComputing Brainmask for {subject}")
            else:
                print(f"\t\tSkipped Brainmask Extraction for {subject}")
        print(f"\tEnding {subject}")
