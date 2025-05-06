# module load all singularity
# cd /envau/work/meca/users/auzias/svrtk_BOUNTI/
# # bash /home/auto-proc-svrtk/scripts/auto-brain-bounti-segmentation-fetal.sh /mnt/test_sub-0001/ /mnt/test_sub-0001/


import sys
import os
import shutil
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg

if __name__ == "__main__":
    input_dir = cfg.DATA_PATH

    output_dir = os.path.join(cfg.BOUNTI_PATH, "svrtk_BOUNTI", "input_SRR_niftymic", "haste")  # path for BOUNTI input
    output_dir_seg = os.path.join(cfg.BOUNTI_PATH, "svrtk_BOUNTI", "output_BOUNTI_seg", "haste")  # path for BOUNTI output

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    if not os.path.exists(output_dir_seg):
        os.makedirs(output_dir_seg)

    for subject in os.listdir(input_dir):
        subject_path = os.path.join(input_dir, subject)

        for session in os.listdir(subject_path):
            subject_session_path = os.path.join(subject_path, session)

            if not "recons_rhesus" in os.listdir(subject_session_path):  # change 'tmp_exp' to 'recons_pipeline' if needed
                continue

            print(f"Processing {subject} {session}...")

            srr_vol = os.path.join(subject_session_path, "recons_rhesus", "recon_template_space", "srr_template_masked_test.nii.gz")

            path_subj = os.path.join(output_dir, subject)
            if not os.path.exists(path_subj):
                os.makedirs(path_subj)

            output_path_subj = os.path.join(path_subj, session)
            if not os.path.exists(output_path_subj):
                os.makedirs(output_path_subj)

            output_recon_file = os.path.join(output_path_subj, "reo-SVR-output-brain_rhesus.nii.gz")
            if os.path.exists(output_recon_file):
                print(f"File {output_recon_file} already exists, skipping...")
                continue

            shutil.copy(srr_vol, output_recon_file)

            path_subj_seg = os.path.join(output_dir_seg, subject)
            if not os.path.exists(path_subj_seg):
                os.mkdir(path_subj_seg)

            output_path_subj_seg = os.path.join(path_subj_seg, session)
            if not os.path.exists(output_path_subj_seg):
                os.mkdir(output_path_subj_seg)



