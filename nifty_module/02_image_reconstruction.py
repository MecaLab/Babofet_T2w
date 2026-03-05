import os
import sys
import pandas as pd
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg
import subprocess


def write_slurm_file_nifty(subj, main_path, denoised_files, bm_folder, bm_files, output_file, ga, denoising_folder="denoising"):
    filename = "slurm_files/nifty_reconstruction.slurm"
    slurm_content = f"""#!/bin/sh
    
#SBATCH --account='b219'
#SBATCH --partition=skylake  # batch 
#SBATCH --time=24:00:00
#SBATCH -c 1
#SBATCH --mem-per-cpu=48G
#SBATCH -o recon_pipeline_niftymic_{subj}.out
#SBATCH -e recon_pipeline_niftymic_{subj}.err

MAIN_PATH="{main_path}"

INPUT_PATH="${{MAIN_PATH}}/{denoising_folder}"
MASK_PATH="${{MAIN_PATH}}/{bm_folder}"

OUTPUT_PATH="${{MAIN_PATH}}/haste/reconstruction_niftymic_full_pipeline_rhesus_macaque"
MOTION_CORRECTION="${{OUTPUT_PATH}}/motion_correction"
OUTPUT_FILE="{output_file}"

TEMPLATE_PATH="/scratch/lbaptiste/data/atlas_fetal_rhesus/"
"""

    slurm_content += "\n"
    for i, file in enumerate(denoised_files, start=1):
        slurm_content += f"INPUT_FILE{i}=\"{file}\"\n"

    slurm_content += "\n"

    for i, file in enumerate(bm_files, start=1):
        slurm_content += f"MASK_FILE{i}=\"{file}\"\n"

    input_stacks = " ".join(["/data/$INPUT_FILE{}".format(i) for i in range(1, len(denoised_files) + 1)])
    mask_stacks = " ".join(["/masks/$MASK_FILE{}".format(i) for i in range(1, len(bm_files) + 1)])

    slurm_content += f"""
singularity exec \\
    -B "$INPUT_PATH":/data \\
    -B "$MASK_PATH":/masks \\
    -B "$OUTPUT_PATH":/output \\
    -B "$TEMPLATE_PATH":/template \\
    /scratch/lbaptiste/softs/niftymic.multifact_latest.sif \\
    niftymic_run_reconstruction_pipeline \\
        --filenames {input_stacks} \\
        --filenames-masks {mask_stacks} \\
        --dir-output /output/ \\
        --isotropic-resolution 0.5 \\
        --bias-field-correction 0 \\
        --template /template/Template_G{ga}_T2W.nii.gz \\
        --template-mask /template/Template_G{ga}_T2W_mask.nii.gz \\
        
"""
    with open(filename, "w", encoding="utf-8") as slurm_file:
        slurm_file.write(slurm_content)

    os.chmod(filename, 0o700)


def get_gestational_info(female_name, session_id, tsv_file):
    # Atlas available timepoints
    atlas_timepoints = [85, 110, 135]

    df = pd.read_csv(tsv_file, sep='\t')

    session_data = df[df['session_id'].str.strip() == session_id]

    if session_data.empty:
        print(f"Error: Session {session_id} not found for {female_name}.")
        return None

    gestational_age = session_data['gestational_age'].values[0]

    adequate_atlas = min(atlas_timepoints, key=lambda x: abs(x - gestational_age))

    return gestational_age, adequate_atlas


def pair_data(t2w_dir, mask_dir):
    list_t2w = []
    list_masks = []

    t2w_files = [f for f in os.listdir(t2w_dir) if f.endswith("T2w_denoised.nii.gz")]

    for t2w_name in t2w_files:
        prefix = t2w_name.split("_T2w")[0]

        expected_mask_name = f"{prefix}_desc-brain_mask.nii.gz"
        mask_full_path = os.path.join(mask_dir, expected_mask_name)

        if os.path.exists(mask_full_path):
            list_t2w.append(t2w_name)
            list_masks.append(expected_mask_name)
        else:
            print(f"Warning: No matching mask found for {t2w_name} in {mask_dir}")

    return list_t2w, list_masks


def write_slurm(
        slurm_filename,
        fullname_subj,
        stack_path,
        denoised_files,
        bm_path,
        bm_files,
        output_path,
        template_path,
        ga):
    slurm_content = f"""#!/bin/sh
    
#SBATCH -J babofet
#SBATCH -p batch
#SBATCH -w niolon13
#SBATCH --mem-per-cpu=48G
#SBATCH --time=24:00:00
#SBATCH -N 1
#SBATCH -o logs/recon_pipeline_niftymic_{fullname_subj}.out
#SBATCH -e logs/recon_pipeline_niftymic_{fullname_subj}.err

INPUT_PATH="{stack_path}"
MASK_PATH="{bm_path}"

"""
    slurm_content += "\n"
    for i, file in enumerate(denoised_files, start=1):
        slurm_content += f"INPUT_FILE{i}=\"{file}\"\n"

    slurm_content += "\n"

    for i, file in enumerate(bm_files, start=1):
        slurm_content += f"MASK_FILE{i}=\"{file}\"\n"

    input_stacks = " ".join(["/data/$INPUT_FILE{}".format(i) for i in range(1, len(denoised_files) + 1)])
    mask_stacks = " ".join(["/masks/$MASK_FILE{}".format(i) for i in range(1, len(bm_files) + 1)])

    slurm_content += f"""
    singularity exec \\
        -B "$INPUT_PATH":/data \\
        -B "$MASK_PATH":/masks \\
        -B "$OUTPUT_PATH":/output \\
        -B "$TEMPLATE_PATH":/template \\
        /scratch/lbaptiste/softs/niftymic.multifact_latest.sif \\
        niftymic_run_reconstruction_pipeline \\
            --filenames {input_stacks} \\
            --filenames-masks {mask_stacks} \\
            --dir-output /output/ \\
            --isotropic-resolution 0.5 \\
            --bias-field-correction 0 \\
            --template /template/Template_G{ga}_T2W.nii.gz \\
            --template-mask /template/Template_G{ga}_T2W_mask.nii.gz \\

    """

    with open(slurm_filename, "w", encoding="utf-8") as slurm_file:
        slurm_file.write(slurm_content)

    os.chmod(slurm_filename, 0o700)

if __name__ == "__main__":
    raw_path = cfg.SOURCEDATA_BIDS_PATH
    derivative_path = cfg.DERIVATIVES_BIDS_PATH
    atlas_path = cfg.FETAL_RESUS_ATLAS

    slurm_dir = "slurm_files"
    if not os.path.exists(slurm_dir):
        os.makedirs(slurm_dir)

    logs_dir = "logs"
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)

    subject = "sub-Aziza"
    session = "ses-01"
    fullname_subj = f"{subject}_{session}"
    slurm_filename = f"{slurm_dir}/reconstruction_niftymic_{fullname_subj}.slurm"

    tsv_file = os.path.join(raw_path, "raw", subject, f"{subject}_sessions.tsv")
    if not os.path.exists(tsv_file):
        print(f"ERROR: tsv file does not exist at {tsv_file}")
        exit()

    stacks_path = os.path.join(derivative_path, "intermediate", "niftymic", subject, session)
    if not os.path.exists(stacks_path):
        print(f"ERROR: stacks path does not exist at {stacks_path}")
        exit()

    brainmask_path = os.path.join(derivative_path, "niftymic", subject, session, "anat")
    if not os.path.exists(brainmask_path):
        print(f"ERROR: brainmask path does not exist at {brainmask_path}")
        exit()

    ga, atlas = get_gestational_info(subject, session, tsv_file)

    list_t2w, list_masks = pair_data(stacks_path, brainmask_path)

    write_slurm(
        slurm_filename=slurm_filename,
        fullname_subj=fullname_subj,
        stack_path=stacks_path,
        denoised_files=list_t2w,
        bm_path=brainmask_path,
        bm_files=list_masks,
        output_path="",
        template_path=atlas_path,
        ga=ga,
    )

    exit()

    """base_path = cfg.MESO_DATA_PATH

    subject_IDs = os.listdir(base_path)

    # /!\ When changing this value, make sur to update the 2nd parameter of mv_recons.sh file within the slurm file
    mask_model = "fetalbet"  # could be 'nifty' or 'mattia' or 'manual'

    if mask_model == "manual":
        bm_folder = "manual_masks"
    elif mask_model == "nifty":
        bm_folder = "brainmask_niftymic"
    elif mask_model == "mattia":
        bm_folder = "mattia_masks"
    elif mask_model == "fetalbet":
        bm_folder = "fetalbet_masks_v2"

    denoising_folder = "denoising"

    ga = "135"  # gestational age in days, used for the template. Should be 85, 110 or 135

    list_subjs = [
        # "sub-Aziza_ses-01",  "sub-Aziza_ses-09", # "sub-Aziza_ses-05",
        # "sub-Borgne_ses-08", "sub-Borgne_ses-10", "sub-Borgne_ses-09",
        # "sub-Bibi_ses-06", "sub-Bibi_ses-07", "sub-Bibi_ses-09",
        # "sub-Filoutte_ses-07", "sub-Filoutte_ses-08", "sub-Filoutte_ses-09", "sub-Filoutte_ses-10",
        "sub-Formule_ses-07", "sub-Formule_ses-09",
        # "sub-Borgne_ses-01", "sub-Borgne_ses-03", "sub-Borgne_ses-04", "sub-Borgne_ses-05", "sub-Borgne_ses-06", "sub-Borgne_ses-07"
    ]

    for subject in list_subjs:

        subj_output_dir = os.path.join(cfg.MESO_OUTPUT_PATH, subject)

        if not os.path.exists(subj_output_dir):
            os.makedirs(subj_output_dir)

        output_dir = os.path.join(subj_output_dir, "haste", "reconstruction_niftymic_full_pipeline_rhesus_macaque")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        print(f"Starting {subject}")

        dir_list = os.listdir(os.path.join(subj_output_dir, denoising_folder))
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
            bm_haste_subj_output_dir = os.path.join(subj_output_dir, bm_folder)

            denoised_subj_output_dir = os.path.join(subj_output_dir, denoising_folder)
            recons_haste_subj_output_dir = os.path.join(haste_subj_output_dir, 'reconstruction_niftymic')

            if not os.path.exists(recons_haste_subj_output_dir):
                os.mkdir(recons_haste_subj_output_dir)

            anat_img = list()
            bm_img = list()
            for f in haste_files:
                filename = f.split(".")
                anat_path_subj_path = os.path.join(denoised_subj_output_dir, f)
                if mask_model == "nifty":  # for brainmask_niftymic folder
                    bm_nifti_filename = filename[0] + "_seg.nii.gz"
                    bm_path_subj_path = os.path.join(bm_haste_subj_output_dir, filename[0], bm_nifti_filename)

                elif mask_model == "manual":  # with manual brainmask
                    bm_nifti_filename = filename[0] + "_mask.nii"
                    bm_path_subj_path = os.path.join(bm_haste_subj_output_dir, bm_nifti_filename)
                    if not os.path.exists(bm_path_subj_path):
                        bm_nifti_filename = filename[0] + "_mask.nii.gz"
                        bm_path_subj_path = os.path.join(bm_haste_subj_output_dir, bm_nifti_filename)

                elif mask_model == "mattia":  # with mattia brainmask
                    bm_nifti_filename = filename[0] + "_mask.nii.gz"
                    bm_path_subj_path = os.path.join(bm_haste_subj_output_dir, bm_nifti_filename)

                elif mask_model == "fetalbet":  # with fetalbet brainmask
                    bm_nifti_filename = filename[0] + "_mask.nii.gz"
                    bm_path_subj_path = os.path.join(bm_haste_subj_output_dir, bm_nifti_filename)

                if os.path.exists(anat_path_subj_path) and os.path.exists(bm_path_subj_path):
                    anat_img.append(f)
                    bm_img.append(bm_nifti_filename)

            motion_subfolder = os.path.join(recons_haste_subj_output_dir, 'motion_correction')

            if not os.path.exists(motion_subfolder):
                os.mkdir(motion_subfolder)

            recons_haste_subj_output = subject + f"_haste_3DHR_{mask_model}_bm_pipeline.nii.gz"

            write_slurm_file_nifty(
                subj=subject,
                main_path=subj_output_dir,
                denoised_files=anat_img,
                bm_folder=bm_folder,
                bm_files=bm_img,
                output_file=recons_haste_subj_output,
                ga=ga,
                denoising_folder=denoising_folder
            )

            print(f"\t\tComputing reconstruction for {subject}")
            subprocess.run(["sbatch", "slurm_files/nifty_reconstruction.slurm"])"""