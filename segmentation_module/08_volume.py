import os
import sys
import matplotlib.pyplot as plt
import nibabel as nib
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg


def compute_vol(mask, voxel_size, labels=[1, 2, 3, 4]):
    """
    Calcule le volume en mm^3 pour chaque label dans le masque.
    """
    volumes = {}
    for label in labels:
        bin_mask = (mask == label).astype(int)
        volume = np.sum(bin_mask) * voxel_size
        volumes[label] = volume
    return volumes


def plot_one_subject(subject, input_folder, label_info, voxel_size):
    label_data = {label: [] for label in label_info}
    sessions = []
    for file in sorted(os.listdir(input_folder)):
        if file.endswith(".nii.gz") and subject in file:
            print(f"Traitement de {file} pour le sujet {subject}...")
            session = file.split(".")[0].split("_")[-1]  # subject_sesXX.nii.gz => sesXX
            pred_path = os.path.join(input_folder, file)
            pred_img = nib.load(pred_path).get_fdata()

            vols = compute_vol(pred_img, voxel_size, label_info.keys())
            for label in label_info:
                label_data[label].append(vols[label])
            sessions.append(session)

    fig, axes = plt.subplots(1, 4, figsize=(20, 6))
    for i, label in enumerate(label_info):
        axes[i].plot(sessions, label_data[label], marker='o')
        axes[i].set_title(f'Label {label}')
        axes[i].set_xlabel('Session')
        axes[i].set_ylabel('Volume (mm³)')
        axes[i].grid(True)

    plt.tight_layout()
    plt.savefig(os.path.join(output_path, f"evolution_volumes_{subject}.png"))


def plot_every_subject(input_folder, label_info, voxel_size, df, dataset_id):
    label_data = {label: {} for label in label_info}
    for file in sorted(os.listdir(input_folder)):
        if file.endswith(".nii.gz"):
            subject_session = file.split(".")[0]  # SUJET_SESXX
            subject = "_".join(subject_session.split("_")[:-1])
            session = subject_session.split("_")[-1]  # SESXX
            session_col = f"ses-{session[3:]}"  # Convertir sesXX en ses-XX

            pred_path = os.path.join(input_folder, file)
            pred_img = nib.load(pred_path).get_fdata()

            vols = compute_vol(pred_img, voxel_size, label_info.keys())

            gestational_days = df.loc[df['subject'] == subject, session_col].values
            if len(gestational_days) == 0 or np.isnan(gestational_days[0]):
                print(f"Session {session} pour le sujet {subject} non trouvée ou NaN dans le CSV.")
                continue
            gestational_days = gestational_days[0]

            for label in label_info:
                if subject not in label_data[label]:
                    label_data[label][subject] = {"gestational_days": [], "volumes": []}
                label_data[label][subject]["gestational_days"].append(gestational_days)
                label_data[label][subject]["volumes"].append(vols[label])

    for label in label_info:
        fig, ax = plt.subplots(figsize=(12, 6))
        for subject in label_data[label]:
            days = label_data[label][subject]["gestational_days"]
            volumes = label_data[label][subject]["volumes"]
            sorted_pairs = sorted(zip(days, volumes), key=lambda x: x[0])
            days_sorted, volumes_sorted = zip(*sorted_pairs) if sorted_pairs else ([], [])

            ax.plot(days_sorted, volumes_sorted, marker='o', label=subject)

        ax.set_title(f'Label {label_info[label]["name"]}')
        ax.set_xlabel('Gestational Days')
        ax.set_ylabel('Volume (mm³)')
        ax.grid(True)
        ax.legend(title='Sujet', bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        plt.savefig(os.path.join(output_path, f"evolution_volumes_{label_info[label]['name']}_by_gestational_days_{dataset_id}.png"))
        plt.close()


def get_all_seg_hemi(root_dir):
    datas = {}
    for subject in os.listdir(root_dir):
        subject_path = os.path.join(root_dir, subject)
        for session in os.listdir(subject_path):
            session_path = os.path.join(subject_path, session)
            name = f"{subject}_{session}"
            seg_path = os.path.join(session_path, f"{name}_hemi_new.nii.gz")
            if os.path.exists(seg_path):
                datas[f"{subject}_{session}"] = seg_path

    return datas


def plot_hemisphere_volumes(seg_dict, voxel_size, df, output_path):
    # Définition des labels par hémisphère
    left_labels = {'WM_left': 6, 'GM_left': 7}
    right_labels = {'WM_right': 2, 'GM_right': 3}

    # Structure pour stocker les données par hémisphère et par tissu
    hemisphere_data = {
        'left': {tissue: {subject: {'gestational_days': [], 'volumes': []} for subject in set(subj.split('_')[0] for subj in seg_dict.keys())}
                for tissue in ['WM', 'GM']},
        'right': {tissue: {subject: {'gestational_days': [], 'volumes': []} for subject in set(subj.split('_')[0] for subj in seg_dict.keys())}
                 for tissue in ['WM', 'GM']}
    }

    for subject_session, seg_path in seg_dict.items():
        subject = "_".join(subject_session.split("_")[:-1])
        session = subject_session.split("_")[-1]
        session_col = f"ses-{session[3:]}"

        # Charger l'image et calculer les volumes
        seg_img = nib.load(seg_path).get_fdata()
        vols = {label: np.sum(seg_img == value) * np.prod(voxel_size) for label, value in {**left_labels, **right_labels}.items()}

        # Récupérer l'âge gestationnel
        gestational_days = df.loc[df['subject'] == subject, session_col].values
        if len(gestational_days) == 0 or np.isnan(gestational_days[0]):
            print(f"Session {session} pour le sujet {subject} non trouvée ou NaN dans le CSV.")
            continue
        gestational_days = gestational_days[0]

        # Stocker les volumes par hémisphère et tissu
        for tissue, side_labels in [('WM', {'left': 6, 'right': 2}), ('GM', {'left': 7, 'right': 3})]:
            for side, label in side_labels.items():
                hemisphere_data[side][tissue][subject]['gestational_days'].append(gestational_days)
                hemisphere_data[side][tissue][subject]['volumes'].append(vols[f"{tissue}_{side}"])

    # Génération des graphiques
    for tissue in ['WM', 'GM']:
        fig, (ax_left, ax_right) = plt.subplots(1, 2, figsize=(14, 6))

        # Plot hémisphère gauche
        for subject in hemisphere_data['left'][tissue]:
            days = hemisphere_data['left'][tissue][subject]['gestational_days']
            volumes = hemisphere_data['left'][tissue][subject]['volumes']
            sorted_pairs = sorted(zip(days, volumes), key=lambda x: x[0])
            if sorted_pairs:
                days_sorted, volumes_sorted = zip(*sorted_pairs)
                ax_left.plot(days_sorted, volumes_sorted, marker='o', label=subject)
        ax_left.set_title(f'{tissue} - Left Hemisphere')
        ax_left.set_xlabel('Gestational Days')
        ax_left.set_ylabel('Volume (mm³)')
        ax_left.grid(True)
        ax_left.legend(title='Subject', bbox_to_anchor=(1.05, 1), loc='upper left')

        # Plot hémisphère droit
        for subject in hemisphere_data['right'][tissue]:
            days = hemisphere_data['right'][tissue][subject]['gestational_days']
            volumes = hemisphere_data['right'][tissue][subject]['volumes']
            sorted_pairs = sorted(zip(days, volumes), key=lambda x: x[0])
            if sorted_pairs:
                days_sorted, volumes_sorted = zip(*sorted_pairs)
                ax_right.plot(days_sorted, volumes_sorted, marker='o', label=subject)
        ax_right.set_title(f'{tissue} - Right Hemisphere')
        ax_right.set_xlabel('Gestational Days')
        ax_right.grid(True)

        plt.tight_layout()
        plt.savefig(os.path.join(output_path, f"evolution_volumes_{tissue}_by_hemisphere.png"))
        plt.close()



if __name__ == "__main__":
    """# Hemisphere split

    output_path = os.path.join(cfg.CODE_PATH, f"snapshots/hemi_split/volumes")
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    seg_dict = get_all_seg_hemi(os.path.join(cfg.BASE_PATH, "atlas_fetal_rhesus_v2/Seg_Hemi"))

    csv_path = os.path.join(cfg.CODE_PATH, "table_data", "sessions_to_days.csv")
    df = pd.read_csv(csv_path)

    voxel_size = np.power(0.5, 3)
    plot_hemisphere_volumes(seg_dict, voxel_size=voxel_size, df=df, output_path=output_path)

    # plot_volume_hemisphere(input_folder, voxel_size=0.5**3, output_path=".")"""

    dataset_id = int(sys.argv[1])

    input_folder = os.path.join(cfg.CODE_PATH, f"inference_all/{dataset_id}_segmentations")

    # output_path = os.path.join(cfg.CODE_PATH, f"snapshots/{model_type}/volumes")
    output_path = os.path.join(cfg.CODE_PATH, "snapshots/nnunet_res/volumes")

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    csv_path = os.path.join(cfg.CODE_PATH, "table_data", "sessions_to_days.csv")
    df = pd.read_csv(csv_path)

    voxel_size = np.power(0.5, 3)
    label_info = {
        2: {"name": "WM"},
        3: {"name": "GM"}
    }
    subject = "Borgne"
    plot_one_subject(subject, input_folder, label_info, voxel_size)
    # plot_every_subject(input_folder, label_info, voxel_size, df, dataset_id)

