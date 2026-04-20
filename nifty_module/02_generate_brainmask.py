import os
import sys
import subprocess
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg


if __name__ == "__main__":

    input_path = os.path.join(cfg.DERIVATIVES_BIDS_PATH, "intermediate", "niftymic")
    output_path = os.path.join(cfg.DERIVATIVES_BIDS_PATH, "intermediate", "fetalbet_brainmask")

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    subjects = ['sub-Filoutte']
    sessions = ['ses-01']


    for subject in subjects:
        print(f"Processing {subject}")
        for session in sessions:
            print(f"\tProcessing {session}")
            subject_path = os.path.join(input_path, subject, session)

            output_subject_path = os.path.join(output_path, subject, session)
            if not os.path.exists(output_subject_path):
                os.makedirs(output_subject_path)

            for file in os.listdir(subject_path):
                if file.endswith(".nii.gz") and "denoised" in file:
                    image_path = os.path.join(subject_path, file)
                    output_folder = os.path.join(output_subject_path, file)

                    subprocess.run([
                        'python', 'fetalbet_module/ensemble_inference.py',
                        '--image_path', image_path,
                        '--output_folder', output_folder
                    ])


