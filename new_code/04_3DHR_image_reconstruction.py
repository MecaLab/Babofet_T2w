import os
import sys
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg
import subprocess

from tools import data_organization as tdo


def write_slurm_file(main_path, denoised_files, mask_files, output_file):
    filename = "nesvor_reconstruction.slurm"
    slurm_content = f"""#!/bin/sh

#SBATCH --account='a391'
#SBATCH --partition=volta
#SBATCH --gres=gpu:1
#SBATCH --time=00:10:00
#SBATCH -o tmp.out
#SBATCH -e tmp.err

module load userspace/all
module load cuda/11.6

echo "Running on: $SLURM_NODELIST"

MAIN_PATH="{main_path}"

INPUT_PATH="${{MAIN_PATH}}/denoising"
MASK_PATH="${{MAIN_PATH}}/brainmask"

OUTPUT_PATH="${{MAIN_PATH}}/haste/reconstruction_ebner"
MOTION_CORRECTION="${{OUTPUT_PATH}}/motion_correction"
OUTPUT_FILE="${{OUTPUT_PATH}}/{output_file}"
"""
    slurm_content += "\n"
    for i, file in enumerate(denoised_files, start=1):
        slurm_content += f"INPUT_FILE{i}=\"{file}\"\n"

    slurm_content += "\n"

    for i, file in enumerate(mask_files, start=1):
        slurm_content += f"MASK_FILE{i}=\"{file}\"\n"

    slurm_content += "\n"

    input_stacks = " ".join(["/data/$INPUT_FILE{}".format(i) for i in range(1, len(denoised_files) + 1)])
    mask_stacks = " ".join(["/masks/$MASK_FILE{}".format(i) for i in range(1, len(mask_files) + 1)])

    slurm_content += f"""
singularity exec --nv \\
    -B "$INPUT_PATH":/data \\
    -B "MASK_PATH":/masks \\
    -B "OUTPUT_PATH":/output \\
    /scratch/lbaptiste/softs/nesvor_latest.sif \\
    nesvor reconstruct \\
        --input-stacks {input_stacks} \\
        --stack-masks {mask_stacks} \\
        --output-volum /outpout/$OUTPUT_FILE \\
        --output-resolution 0.8 \\
        --registration svort \\
        --segmentation \\
        --bias-field-correction 
"""
    with open(filename, "w", encoding="utf-8") as slurm_file:
        slurm_file.write(slurm_content)

    os.chmod(filename, 0o700)


if __name__ == '__main__':
    base_path = cfg.MESO_DATA_PATH

    subject_IDs = os.listdir(base_path)
    subjects_failed = list()

    recon_approach = "ebner"

    for subject in subject_IDs:
        subj_output_dir = os.path.join(cfg.MESO_OUTPUT_PATH, subject)
        if not os.path.exists(subj_output_dir):
            os.makedirs(subj_output_dir)

        print("Starting {}".format(subject))

        dir_list = os.listdir(os.path.join(subj_output_dir, "denoising"))
        haste_files = list()
        truefisp_files = list()

        for d in dir_list:
            d_lower = d.lower()
            if "haste" in d_lower:
                haste_files.append(d)
            if "trufi" in d_lower:
                truefisp_files.append(d)

        if len(haste_files) > 0:
            print("\tStarting HASTE {}".format(subject))
            haste_subj_output_dir = os.path.join(subj_output_dir, "haste")
            bm_haste_subj_output_dir = os.path.join(subj_output_dir, "brainmask")
            denoised_subj_output_dir = os.path.join(subj_output_dir, "denoising")
            recons_haste_subj_output_dir = os.path.join(haste_subj_output_dir, 'reconstruction_' + recon_approach)

            anat_img = list()
            bm_img = list()
            for f in haste_files:
                nifti_filename = f
                bm_nifti_filename = f.replace("_denoised.nii", "_brainmask_resampled.nii")

                if os.path.exists(os.path.join(denoised_subj_output_dir, f)) and os.path.exists(os.path.join(bm_haste_subj_output_dir, bm_nifti_filename)):
                    anat_img.append(nifti_filename)
                    bm_img.append(bm_nifti_filename)

            recons_haste_subj_output = os.path.join(recons_haste_subj_output_dir, subject + '_haste_3DHR.nii.gz')
            motion_subfolder = os.path.join(recons_haste_subj_output_dir, 'motion_correction')

            if os.path.exists(recons_haste_subj_output):
                print('\t\tSkipped reconstruction HASTE for {}'.format(subject))
            else:
                if not os.path.exists(motion_subfolder):
                    os.mkdir(motion_subfolder)

                recons_haste_subj_output = subject + '_haste_3DHR.nii.gz'
                print(recons_haste_subj_output)

                write_slurm_file(subj_output_dir, anat_img, bm_img, recons_haste_subj_output)
                exit()

"""
cmd_os = "singularity run /scratch/lbaptiste/softs/niftymic.multifact_latest.sif"
                        cmd_os = 'niftymic_reconstruct_volume --filenames '
                        for v in anat_img:
                            cmd_os += v + ' '
                        cmd_os += " --filenames-masks "
                        for v in bm_img:
                            cmd_os += v + ' '

                        cmd_os += ' --output ' + recons_haste_subj_output
                        cmd_os += ' --alpha 0.01 --threshold-first 0.6 --threshold 0.7 --intensity-correction 1 --bias-field-correction 1 --isotropic-resolution 0.5'
                        cmd_os += ' --dilation-radius 5'
                        cmd_os += ' --subfolder-motion-correction ' + motion_subfolder
                        cmd_os += ' --use-masks-srr 1'
                        
                        
niftymic_reconstruct_volume 
    --filenames 
        /scratch/lbaptiste/data/dataset/babofet/subjects/sub-Formule_ses-08/scans/9-T2_HASTE_COR/resources/NIFTI/files 
        /scratch/lbaptiste/data/dataset/babofet/subjects/sub-Formule_ses-08/scans/10-T2_HASTE_AX2/resources/NIFTI/files 
        /scratch/lbaptiste/data/dataset/babofet/subjects/sub-Formule_ses-08/scans/8-T2_HASTE_SAG/resources/NIFTI/files  
    --filenames-masks 
        /scratch/lbaptiste/data/dataset/babofet/processing/sub-Formule_ses-08/brainmask/sub-Formule_ses-08_T2_HASTE_COR_9_brainmask.nii 
        /scratch/lbaptiste/data/dataset/babofet/processing/sub-Formule_ses-08/brainmask/sub-Formule_ses-08_T2_HASTE_AX2_10_brainmask.nii 
        /scratch/lbaptiste/data/dataset/babofet/processing/sub-Formule_ses-08/brainmask/sub-Formule_ses-08_T2_HASTE_SAG_8_brainmask.nii  
    --output 
    /scratch/lbaptiste/data/dataset/babofet/processing/sub-Formule_ses-08/haste/reconstruction_ebner/sub-Formule_ses-08_haste_3DHR.nii.gz 
    
    --alpha 0.01 --threshold-first 0.6 --threshold 0.7 --intensity-correction 1 --bias-field-correction 1 
    --isotropic-resolution 0.5 --dilation-radius 5 
    --subfolder-motion-correction 
        /scratch/lbaptiste/data/dataset/babofet/processing/sub-Formule_ses-08/haste/reconstruction_ebner/motion_correction --use-masks-srr 1
"""