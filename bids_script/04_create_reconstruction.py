import os
import sys
import shutil
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg


def format_session_str(sess):
    id_sess = sess[3:]
    return f"ses-{id_sess}"

if __name__ == "__main__":
    INPUT_PATH = os.path.join(cfg.BASE_NIOLON_PATH, "recons_folder")
    OUTPUT_PATH = os.path.join(cfg.DERIVATIVES_BIDS_PATH, "niftymic")

    for subject in os.listdir(INPUT_PATH):
        subject_path = os.path.join(INPUT_PATH, subject)
        print(f"Processing {subject}")
        for session in os.listdir(subject_path):
            print(f"\t{session}")

            session_path = os.path.join(subject_path, session, "recons_rhesus", "recon_template_space")
            if not os.path.exists(session_path):
                print(f"\t\tSkipping {subject} {session} because input folder is missing")
                continue

            reconstruction_t2w = os.path.join(session_path, "srr_template_debiased.nii.gz")

            # sub-<sub>_ses-<ses>_rec-niftymic_desc-brain_T2w.nii.gz
            output_filename = f"sub-{subject}_{session}_rec-niftymic_desc-brainbg_T2w.nii.gz"
            output_folder = os.path.join(OUTPUT_PATH, f"sub-{subject}", format_session_str(session), "anat")
            output_full_path = os.path.join(output_folder, output_filename)

            if not os.path.exists(output_folder):
                os.makedirs(output_folder)

            shutil.copy(reconstruction_t2w, output_full_path)
            exit()
        exit()
