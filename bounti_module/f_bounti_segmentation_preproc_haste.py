# module load all singularity
# cd /envau/work/meca/users/auzias/svrtk_BOUNTI/
# # bash /home/auto-proc-svrtk/scripts/auto-brain-bounti-segmentation-fetal.sh /mnt/test_sub-0001/ /mnt/test_sub-0001/


import sys
import os
import shutil
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg

if __name__ == "__main__":
    subject = sys.argv[1]

    base_path = os.path.join(cfg.RECONS_FOLDER, subject)

    output_dir = cfg.SEG_INPUT_PATH_NIOLON  # path for BOUNTI input
    output_dir_seg = cfg.SEG_OUTPUT_PATH_NIOLON  # path for BOUNTI output

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    if not os.path.exists(output_dir_seg):
        os.makedirs(output_dir_seg)

    for session in os.listdir(base_path):
        subject_session_path = os.path.join(base_path, session)

        if not "recons_rhesus" in os.listdir(subject_session_path):
            continue

        print(f"Processing {subject} {session}...")

        srr_vol = os.path.join(subject_session_path, "recons_rhesus", "recon_template_space", "srr_template_masked_dilated.nii.gz")

        if not os.path.exists(srr_vol):
            print(f"\tFile {srr_vol} does not exist. Make sure to run previous scripts to generate it.")
            continue

        path_subj = os.path.join(output_dir, subject)
        if not os.path.exists(path_subj):
            os.makedirs(path_subj)

        output_path_subj = os.path.join(path_subj, session)
        if not os.path.exists(output_path_subj):
            os.makedirs(output_path_subj)

        output_recon_file = os.path.join(output_path_subj, "reo-SVR-output-brain_rhesus.nii.gz")  # bounti filename format
        if os.path.exists(output_recon_file):
            print(f"\tFile {output_recon_file} already exists, skipping...")
            continue

        shutil.copy(srr_vol, output_recon_file)

        path_subj_seg = os.path.join(output_dir_seg, subject, session)
        if not os.path.exists(path_subj_seg):
            os.makedirs(path_subj_seg)


