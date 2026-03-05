import os
import sys
import shutil
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg


def format_session_str(sess):
    id_sess = sess[3:]
    return f"ses-{id_sess}"

def unformat_session_str(sess):
    id_sess = sess[3:]
    return f"ses0{id_sess}"


def clean_file(input_dir):
    for subject in os.listdir(input_dir):
        if subject.endswith(".json"):
            continue
        print(f"{subject}")
        subject_path = os.path.join(input_dir, subject)
        for session in os.listdir(subject_path):
            print(f"\t{session}")
            session_path = os.path.join(subject_path, session, "anat")

            # sub-Filoutte_ses02_rec-niftymic_desc-brainbg_T2w
            session_corr = session.replace("-", "")
            t2w_2_del = f"{subject}_{session_corr}_rec-niftymic_desc-brainbg_T2w.nii.gz"
            json_2_del = f"{subject}_{session_corr}_rec-niftymic_desc-brainbg_T2w.json"
            try:
                os.remove(os.path.join(session_path, t2w_2_del))
                os.remove(os.path.join(session_path, json_2_del))
            except FileNotFoundError:
                pass


if __name__ == "__main__":
    INPUT_PATH = os.path.join(cfg.BASE_NIOLON_PATH, "recons_folder")
    OUTPUT_PATH = os.path.join(cfg.DERIVATIVES_BIDS_PATH, "niftymic")

    # clean_file(OUTPUT_PATH)

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

            formated_sess = format_session_str(session)

            # sub-<sub>_ses-<ses>_rec-niftymic_desc-brain_T2w.nii.gz
            output_filename = f"sub-{subject}_{formated_sess}_rec-niftymic_desc-brainbg_T2w.nii.gz"
            output_folder = os.path.join(OUTPUT_PATH, f"sub-{subject}", formated_sess, "anat")
            output_full_path = os.path.join(output_folder, output_filename)
            print(output_full_path)
            exit()

            if not os.path.exists(output_folder):
                os.makedirs(output_folder)

            shutil.copy(reconstruction_t2w, output_full_path)
