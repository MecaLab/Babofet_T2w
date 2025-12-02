import os
import sys
import json
import shutil
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg


def write_json_file(path, num_training, dataset_name):
    dico_data = {
        "channel_names": {
            "0": "T2W",
            "1": "T2W",
            "2": "noNorm",
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


def get_previous_session(session):
    # Extraire le numéro de session
    num = int(session[3:])  # On prend les deux derniers caractères et on les convertit en entier
    # Calculer le numéro précédent
    previous_num = num - 1
    # Formater le résultat avec un zéro devant si nécessaire
    return f"ses{previous_num:02d}"


def get_file_from_subject_session(subject, session):
    return os.path.join(cfg.DATA_PATH, subject, session,
                                       "recons_rhesus/recon_template_space/srr_template.nii.gz")



if __name__ == "__main__":
    train_data = {
        "Borgne": ["ses08"],
        "Bibi": ["ses02", "ses07"],
        "Fabienne": ["ses03", "ses08"],
        "Filoutte": ["ses04", "ses05"],
        "Formule": ["ses02", "ses03"]
    }

    test_data = {
        "Borgne": ["ses09"],
        "Fabienne": ["ses04", "ses05"],
        "Filoutte": ["ses03", "ses08"]
    }

    id_dataset = 20
    name = "tmp_longi"

    if id_dataset < 10:
        dataset_name = f"Dataset00{id_dataset}_{name}"
    elif id_dataset < 100:
        dataset_name = f"Dataset0{id_dataset}_{name}"
    else:
        dataset_name = f"Dataset{id_dataset}_{name}"

    output_path = os.path.join(cfg.NNUNET_RAW_PATH, dataset_name)

    images_tr_path = os.path.join(output_path, "imagesTr")
    images_ts_path = os.path.join(output_path, "imagesTs")
    labels_tr_path = os.path.join(output_path, "labelsTr")

    if not os.path.exists(images_tr_path):
        os.makedirs(images_tr_path)
    if not os.path.exists(images_ts_path):
        os.makedirs(images_ts_path)
    if not os.path.exists(labels_tr_path):
        os.makedirs(labels_tr_path)

    print("Training files...")
    for subject in train_data:
        break
        print(f"\tProcessing subject: {subject}")
        for session in train_data[subject]:
            print(f"\t\tProcessing session: {session}")
            current_volume_path = get_file_from_subject_session(subject, session)
            current_seg_path = os.path.join(cfg.BASE_PATH, "gt_dataset", "train_dataset", f"{subject}_{session}.nii.gz")

            previous_session = get_previous_session(session)
            previous_volume_path = get_file_from_subject_session(subject, previous_session)

            if previous_session in train_data[subject]:
                previous_seg = os.path.join(cfg.BASE_PATH, "gt_dataset", "train_dataset", f"{subject}_{previous_session}.nii.gz")
            else:
                previous_seg = os.path.join(cfg.BASE_PATH, "gt_dataset", "previous_timepoint", f"{subject}_{previous_session}.nii.gz")

            output_path_current_vol = os.path.join(images_tr_path, f"{subject}_{session}_0000.nii.gz")   # T2w t
            output_path_current_seg = os.path.join(labels_tr_path, f"{subject}_{session}.nii.gz")  # seg t

            output_path_previous_vol = os.path.join(images_tr_path, f"{subject}_{session}_0001.nii.gz")  # T2w t-1
            output_path_previous_seg = os.path.join(images_tr_path, f"{subject}_{session}_0002.nii.gz")  # seg t-1

            if not os.path.exists(output_path_current_vol):
                os.system(f"cp {current_volume_path} {output_path_current_vol}")
                os.system(f"cp {current_seg_path} {output_path_current_seg}")

                os.system(f"cp {previous_volume_path} {output_path_previous_vol}")
                os.system(f"cp {previous_seg} {output_path_previous_seg}")

    print("Testing files...")
    for subject in test_data:
        print(f"\tProcessing subject: {subject}")
        for session in test_data[subject]:
            print(f"\t\tProcessing session: {session}")
            current_volume_path = get_file_from_subject_session(subject, session)

            previous_session = get_previous_session(session)
            previous_volume_path = get_file_from_subject_session(subject, previous_session)

            output_path_current_vol = os.path.join(images_ts_path, f"{subject}_{session}_0000.nii.gz")
            output_path_previous_vol = os.path.join(images_ts_path, f"{subject}_{session}_0001.nii.gz")

            os.system(f"cp {current_volume_path} {output_path_current_vol}")
            os.system(f"cp {previous_volume_path} {output_path_previous_vol}")

    dataset_json = os.path.join(output_path, "dataset.json")
    num_training = len(os.listdir(labels_tr_path))
    write_json_file(dataset_json, num_training, dataset_name)
    os.system(f"nnUNetv2_plan_and_preprocess -d {id_dataset} --verify_dataset_integrity")
