import os
import sys
import shutil
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg


if __name__ == "__main__":
    pred_seg = os.path.join(cfg.DERIVATIVES_BIDS_PATH, "intermediate", "longiseg", "inference_data", "res_seg")
    base_output_path = os.path.join(cfg.DERIVATIVES_BIDS_PATH, "longiseg")

    if not os.path.exists(pred_seg):
        print("Error ! Segmentations results does not exist")
        exit(1)

    if not os.path.exists(base_output_path):
        os.makedirs(base_output_path)

    for file in os.listdir(pred_seg):
        if file.endswith(".nii.gz"):
            # Borgne_ses-01.nii.gz
            file_splited = file.split(".")[0].split("_")  # [SUBJ, SESS]
            sub_subject = file_splited[0]
            session = file_splited[1]

            input_seg_path = os.path.join(pred_seg, file)
            output_path = os.path.join(base_output_path, sub_subject, session, "anat")
            if not os.path.exists(output_path):
                os.makedirs(output_path)

            # SUBJ_SESS_desc-longiseg_dseg.nii
            output_name = f"{sub_subject}_{session}_desc-longiseg_dseg.nii.gz"
            output_seg_path = os.path.join(output_path, output_name)
            shutil.copy(input_seg_path, output_seg_path)

