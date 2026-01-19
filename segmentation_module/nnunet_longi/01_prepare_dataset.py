import os
import json
import configuration as cfg


def write_json_file(path, num_training, dataset_name):
    dico_data = {
        "channel_names": {
            "0": "T2W_t",
            "1": "T2W_t-1",
            "2": "noNorm_Seg_t-1",
        },
        "labels": {
            "background": 0, "CSF": 1, "WM": 2, "GM": 3, "Ventricle": 4,
        },
        "numTraining": num_training,
        "file_ending": ".nii.gz",
        "dataset_name": dataset_name
    }
    with open(path, 'w') as f:
        json.dump(dico_data, f, indent=4)


def get_actual_previous_session(subject, current_session, full_dict):
    """Trouve la session précédente réelle dans la liste des sessions disponibles."""
    sessions = sorted(full_dict[subject])
    idx = sessions.index(current_session)
    if idx > 0:
        return sessions[idx - 1]
    return None


if __name__ == "__main__":
    train_data = {
        "Borgne": ["ses01", "ses03", "ses05"],
        "Bibi": ["ses01", "ses02", "ses04"],
        "Fabienne": ["ses01", "ses02", "ses04"],
        "Filoutte": ["ses01", "ses02", "ses03"],
        "Formule": ["ses02", "ses03", "ses04"]
    }
    test_data = {
        "Borgne": ["ses04"],
        "Bibi": ["ses03"],
        "Fabienne": ["ses03"],
        "Filoutte": ["ses04"],
        "Formule": ["ses01"]
    }

    # Fusion pour connaître toutes les sessions disponibles par sujet
    full_data = {}
    for subj in set(list(train_data.keys()) + list(test_data.keys())):
        full_data[subj] = list(set(train_data.get(subj, []) + test_data.get(subj, [])))

    id_dataset = 20
    dataset_name = f"Dataset{id_dataset:03d}_tmp_longi"
    output_path = os.path.join(cfg.NNUNET_RAW_PATH, dataset_name)

    images_tr_path = os.path.join(output_path, "imagesTr")
    images_ts_path = os.path.join(output_path, "imagesTs")
    labels_tr_path = os.path.join(output_path, "labelsTr")

    for p in [images_tr_path, images_ts_path, labels_tr_path]:
        os.makedirs(p, exist_ok=True)

    seg_dataset = "gt_dataset_2"

    # --- TRAIN ---
    print("Processing Training Files...")
    for subject, sessions in train_data.items():
        for session in sessions:
            prev = get_actual_previous_session(subject, session, full_data)
            if not prev:
                continue  # On saute les ses01 en cible d'entraînement

            # Chemins
            curr_vol = os.path.join(cfg.DATA_PATH, subject, session,
                                    "recons_rhesus/recon_template_space/srr_template.nii.gz")
            curr_seg = os.path.join(cfg.BASE_PATH, seg_dataset, "train_dataset", f"{subject}_{session}.nii.gz")
            prev_vol = os.path.join(cfg.DATA_PATH, subject, prev,
                                    "recons_rhesus/recon_template_space/srr_template.nii.gz")

            # Recherche de la seg t-1 (train ou previous_timepoint)
            prev_seg = os.path.join(cfg.BASE_PATH, seg_dataset, "train_dataset", f"{subject}_{prev}.nii.gz")
            if not os.path.exists(prev_seg):
                prev_seg = os.path.join(cfg.BASE_PATH, seg_dataset, "previous_timepoint", f"{subject}_{prev}.nii.gz")

            # Copies
            os.system(f"cp {curr_vol} {os.path.join(images_tr_path, f'{subject}_{session}_0000.nii.gz')}")
            os.system(f"cp {prev_vol} {os.path.join(images_tr_path, f'{subject}_{session}_0001.nii.gz')}")
            os.system(f"cp {prev_seg} {os.path.join(images_tr_path, f'{subject}_{session}_0002.nii.gz')}")
            os.system(f"cp {curr_seg} {os.path.join(labels_tr_path, f'{subject}_{session}.nii.gz')}")

    # --- TEST ---
    print("Processing Testing Files...")
    for subject, sessions in test_data.items():
        for session in sessions:
            prev = get_actual_previous_session(subject, session, full_data)

            curr_vol = os.path.join(cfg.DATA_PATH, subject, session,
                                    "recons_rhesus/recon_template_space/srr_template.nii.gz")

            if not prev:  # Cas Formule ses01
                prev_vol = curr_vol
                prev_seg = os.path.join(cfg.BASE_PATH, seg_dataset, "previous_timepoint", f"{subject}_{session}.nii.gz")
            else:
                prev_vol = os.path.join(cfg.DATA_PATH, subject, prev,
                                        "recons_rhesus/recon_template_space/srr_template.nii.gz")
                prev_seg = os.path.join(cfg.BASE_PATH, seg_dataset, "train_dataset", f"{subject}_{prev}.nii.gz")
                if not os.path.exists(prev_seg):
                    prev_seg = os.path.join(cfg.BASE_PATH, seg_dataset, "previous_timepoint",
                                            f"{subject}_{prev}.nii.gz")

            os.system(f"cp {curr_vol} {os.path.join(images_ts_path, f'{subject}_{session}_0000.nii.gz')}")
            os.system(f"cp {prev_vol} {os.path.join(images_ts_path, f'{subject}_{session}_0001.nii.gz')}")
            os.system(f"cp {prev_seg} {os.path.join(images_ts_path, f'{subject}_{session}_0002.nii.gz')}")

    write_json_file(os.path.join(output_path, "dataset.json"), len(os.listdir(labels_tr_path)), dataset_name)
    print("Done. Ready for nnU-Net preprocessing.")
    os.system(f"nnUNetv2_plan_and_preprocess -d {id_dataset} --verify_dataset_integrity")
