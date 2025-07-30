import os
import sys
import json
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg
import shutil


def write_dataset_json(path, num_training, dataset_name):
    dico_data = {
        "channel_names": {
            "0": "T2W",
        },
        "labels": {
            "background": 0,
            "CSF": 1,
            "WM": 2,
            "GM": 3,
            "Ventricle": 4,
        },
        "numTraining": num_training,
        "file_ending": ".nii.gz",
        "dataset_name": dataset_name
    }
    with open(path, 'w') as f:
        json.dump(dico_data, f, indent=4)


def write_patients_json():
    pass


def get_previous_session_number(curr_sess):
    sess_number = int(curr_sess[3:])
    previous_sess = sess_number - 1
    return f"ses0{previous_sess}"


def get_data_from_previous_session(previous_sess, main_path):
    pass


if __name__ == "__main__":
    subject_sessions = {
        "Borgne": ["ses08"],
        "Fabienne": ["ses03", "ses04", "ses05", "ses08"],
        "Filoutte": ["ses03", "ses04", "ses05"],
        "Formule": ["ses02", "ses03"],
    }

    mode_dataset = "debiased-2"  # "masked" or "unmasked" or "debiased-2" or "full"

    id_dataset = int(sys.argv[1])  # should be integer, eg, 1, 2, 3, etc.
    name = sys.argv[2]  # the dataset name, can be whatever you want, but you will need to use it later so remember it
    if id_dataset < 10:
        dataset_name = f"Dataset00{id_dataset}_{name}"
    elif id_dataset < 100:
        dataset_name = f"Dataset0{id_dataset}_{name}"
    else:
        dataset_name = f"Dataset{id_dataset}_{name}"

    output_path = os.path.join(cfg.LONGISEG_RAW_PATH, dataset_name)

    images_tr_path = os.path.join(output_path, "imagesTr")
    images_ts_path = os.path.join(output_path, "imagesTs")
    labels_tr_path = os.path.join(output_path, "labelsTr")

    if not os.path.exists(images_tr_path):
        os.makedirs(images_tr_path)
    if not os.path.exists(images_ts_path):
        os.makedirs(images_ts_path)
    if not os.path.exists(labels_tr_path):
        os.makedirs(labels_tr_path)

    for subject, sessions in subject_sessions.items():
        print(f"Processing subject: {subject}")

        input_path_3d_stacks = os.path.join(cfg.DATA_PATH, subject)
        input_path_3d_segs = os.path.join(cfg.SEG_OUTPUT_PATH, subject)

        for session in sessions:
            print(f"\tProcessing session: {session}")

            current_path_3d_stack = os.path.join(input_path_3d_stacks, session)
            current_path_3d_seg = os.path.join(input_path_3d_segs, session)

            # Current session
            input_path_3d_stack = os.path.join(current_path_3d_stack, "recons_rhesus/recon_template_space/srr_template.nii.gz")
            input_path_3d_stack_bis = os.path.join(current_path_3d_stack, "recons_rhesus/recon_template_space/srr_template_debiased.nii.gz")

            input_path_3d_seg = os.path.join(current_path_3d_seg, "reo-SVR-output-brain_rhesus-mask-brain_bounti-4.nii.gz")

            output_path_3d_stack = os.path.join(images_tr_path, f"{subject}_{session}_bias_t{session[3:]}_0000.nii.gz")
            output_path_3d_stack_bis = os.path.join(images_tr_path, f"{subject}_{session}_debias_t{session[3:]}_0000.nii.gz")

            output_path_3d_seg = os.path.join(labels_tr_path, f"{subject}_{session}_bias.nii.gz")
            output_path_3d_seg_bis = os.path.join(labels_tr_path, f"{subject}_{session}_debias.nii.gz")

            shutil.copy2(input_path_3d_stack, output_path_3d_stack)
            shutil.copy2(input_path_3d_stack_bis, output_path_3d_stack_bis)

            shutil.copy2(input_path_3d_seg, output_path_3d_seg)
            shutil.copy2(input_path_3d_seg, output_path_3d_seg_bis)

            # Previous sess
            previous_sess = get_previous_session_number(curr_sess=session)
            print(f"\tProcessing previous session: {session}")

            previous_path_3d_stack = os.path.join(input_path_3d_stacks, previous_sess)
            previous_path_3d_seg = os.path.join(input_path_3d_segs, previous_sess)

            input_path_3d_stack = os.path.join(previous_path_3d_stack, "recons_rhesus/recon_template_space/srr_template.nii.gz")
            input_path_3d_stack_bis = os.path.join(previous_path_3d_stack, "recons_rhesus/recon_template_space/srr_template_debiased.nii.gz")

            output_path_3d_stack = os.path.join(images_tr_path, f"{subject}_{previous_sess}_bias_t{previous_sess[3:]}_0000.nii.gz")
            output_path_3d_stack_bis = os.path.join(images_tr_path, f"{subject}_{previous_sess}_debias_t{previous_sess[3:]}_0000.nii.gz")

            shutil.copy2(input_path_3d_stack, output_path_3d_stack)
            shutil.copy2(input_path_3d_stack_bis, output_path_3d_stack_bis)

