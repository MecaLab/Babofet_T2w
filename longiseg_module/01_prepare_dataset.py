import os
import sys
import json
sys.path.insert(0, os.path.abspath(os.curdir))
from collections import defaultdict
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


def write_patients_json(imagesTr_path, imagesTs_path, output_json):
    files = sorted(os.listdir(imagesTr_path))

    patients = defaultdict(list)
    for f in files:
        patient_name = f.split('_')[0]  # Tout avant le premier underscore comme nom patient
        patients[patient_name].append(f.split("_0000")[0])

    files = sorted(os.listdir(imagesTs_path))

    for f in files:
        patient_name = f.split("_")[0]
        patients[patient_name].append(f.split("_0000")[0])

    with open(output_json, "w") as out_file:
        json.dump(patients, out_file, indent=4)


def get_previous_session_number(curr_sess):
    sess_number = int(curr_sess[3:])
    previous_sess = sess_number - 1
    return f"ses0{previous_sess}"


if __name__ == "__main__":
    train_subject_sessions = {
        "Borgne": ["ses08", "ses09"],
        "Fabienne": ["ses03", "ses04", "ses05", "ses08"],
        "Filoutte": ["ses03", "ses04", "ses05", "ses08"],
        "Formule": ["ses02", "ses03"],
        "Bibi": ["ses07"]
    }

    test_subject_sessions = {
        "Bibi": ["ses04", "ses05", "ses06", "ses09"],
        "Borgne": ["ses04", "ses05", "ses06", "ses10"],
        "Filoutte": ["ses06", "ses07", "ses09", "ses10"],
        "Fabienne": ["ses07", "ses09"],
        # "Aziza": ["ses02", "ses03", "ses04", "ses05", "ses06", "ses07", "ses08", "ses09", "ses10"],
        # "Forme": ["ses02", "ses03", "ses05", "ses06", "ses07", "ses08", "ses09", "ses10"],
    }

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

    print("Train processing...")
    # train processing
    for subject, sessions in train_subject_sessions.items():
        print(f"\tProcessing subject: {subject}")
        input_path_3d_segs = os.path.join(cfg.SEG_OUTPUT_PATH, subject)

        input_path_3d_stacks = os.path.join(cfg.DATA_PATH, subject)

        for session in sessions:
            print(f"\t\tProcessing session: {session}")

            # Current session
            input_path_3d_stack = os.path.join(input_path_3d_stacks, session, "recons_rhesus/recon_template_space/srr_template.nii.gz")
            input_path_3d_stack_bis = os.path.join(input_path_3d_stacks, session, "recons_rhesus/recon_template_space/srr_template_debiased.nii.gz")

            input_path_3d_seg = os.path.join(input_path_3d_segs, session, "reo-SVR-output-brain_rhesus-mask-brain_bounti-4.nii.gz")

            output_path_3d_stack = os.path.join(images_tr_path, f"{subject}_{session}_bias_0000.nii.gz")
            output_path_3d_stack_bis = os.path.join(images_tr_path, f"{subject}_{session}_debias_0000.nii.gz")

            output_path_3d_seg = os.path.join(labels_tr_path, f"{subject}_{session}_bias.nii.gz")
            output_path_3d_seg_bis = os.path.join(labels_tr_path, f"{subject}_{session}_debias.nii.gz")

            os.system(f"cp {input_path_3d_stack} {output_path_3d_stack}")
            os.system(f"cp {input_path_3d_stack_bis} {output_path_3d_stack_bis}")

            os.system(f"cp {input_path_3d_seg} {output_path_3d_seg}")
            os.system(f"cp {input_path_3d_seg} {output_path_3d_seg_bis}")

            # Previous session
            previous_sess = get_previous_session_number(session)
            print(f"\t\t\tProcessing previous session: {previous_sess}")

            previous_path_3d_stack = os.path.join(input_path_3d_stacks, previous_sess)
            previous_path_3d_seg = os.path.join(input_path_3d_segs, previous_sess)

            input_path_3d_stack = os.path.join(previous_path_3d_stack, "recons_rhesus/recon_template_space/srr_template.nii.gz")
            input_path_3d_stack_bis = os.path.join(previous_path_3d_stack, "recons_rhesus/recon_template_space/srr_template_debiased.nii.gz")

            output_path_3d_stack = os.path.join(images_tr_path, f"{subject}_{previous_sess}_bias_0000.nii.gz")
            output_path_3d_stack_bis = os.path.join(images_tr_path, f"{subject}_{previous_sess}_debias_0000.nii.gz")

            os.system(f"cp {input_path_3d_stack} {output_path_3d_stack}")
            os.system(f"cp {input_path_3d_stack_bis} {output_path_3d_stack_bis}")

            input_path_3d_seg = os.path.join(previous_path_3d_seg, "reo-SVR-output-brain_rhesus-mask-brain_bounti-4.nii.gz")
            output_path_3d_seg = os.path.join(labels_tr_path, f"{subject}_{previous_sess}_bias.nii.gz")
            output_path_3d_seg_bis = os.path.join(labels_tr_path, f"{subject}_{previous_sess}_debias.nii.gz")

            os.system(f"cp {input_path_3d_seg} {output_path_3d_seg}")
            os.system(f"cp {input_path_3d_seg} {output_path_3d_seg_bis}")

    print("Test processing...")
    # test processing
    for subject, sessions in test_subject_sessions.items():
        print(f"\tProcessing subject: {subject}")
        input_path_3d_segs = os.path.join(cfg.SEG_OUTPUT_PATH, subject)
        input_path_3d_stacks = os.path.join(cfg.DATA_PATH, subject)

        for session in sessions:
            print(f"\t\tProcessing session: {session}")
            input_path_3d_stack = os.path.join(input_path_3d_stacks, session, "recons_rhesus/recon_template_space/srr_template_debiased.nii.gz")

            output_path_3d_stack = os.path.join(images_ts_path, f"{subject}_{session}_debias_0000.nii.gz")

            os.system(f"cp {input_path_3d_stack} {output_path_3d_stack}")

    dataset_json = os.path.join(output_path, "dataset.json")
    num_training = len(os.listdir(labels_tr_path))
    write_dataset_json(dataset_json, num_training, dataset_name)

    patients_json = os.path.join(output_path, "patientsTr.json")
    write_patients_json(images_tr_path, images_ts_path, patients_json)

    print("Dataset preparation completed")
    print("Running dataset check...")
    # os.system(f"LongiSeg_plan_and_preprocess -d {id_dataset} -c 3d_fullres --verify_dataset_integrity")
