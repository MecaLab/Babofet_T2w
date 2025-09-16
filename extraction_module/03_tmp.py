import numpy as np
import os
import sys
import nibabel as nib
import ants
from scipy.ndimage import zoom

sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg

def ants_register(fixed, moving_atlas_file):
    moving_atlas = ants.image_read(moving_atlas_file)
    mytx = ants.registration(fixed=fixed, moving=moving_atlas, type_of_transform="Affine")
    warped_atlas = mytx['warpedmovout']
    wraped_mi = ants.image_mutual_information(fixed, warped_atlas)
    return wraped_mi

def find_best_atlas(fixed, atlas_path, atlas_list):
    best_atlas = None
    for i, atlas in enumerate(atlas_list):
        atlas_file = os.path.join(atlas_path, f"ONPRC_G{atlas}_Norm.nii.gz")
        current_mi = ants_register(fixed, atlas_file)
        print(f"\t{atlas}: {current_mi}")
        if i > 0:
            diff_mi = current_mi - previous_mi
            print(f"\t\t{atlas} - {atlas_list[i-1]} = {diff_mi}")
        if best_atlas is None or current_mi < best_atlas[1]:
            best_atlas = [atlas, current_mi]
        previous_mi = current_mi
    return best_atlas[0]

def resample_to_target(moving_img, target_img):
    moving_data = moving_img.get_fdata()
    target_shape = target_img.shape
    zoom_factors = [t / m for t, m in zip(target_shape, moving_data.shape)]
    resampled_data = zoom(moving_data, zoom_factors, order=0)
    return nib.Nifti1Image(resampled_data, target_img.affine)

if __name__ == "__main__":
    recons_folder = cfg.RECONS_FOLDER
    atlas_path = os.path.join(cfg.BASE_NIOLON_PATH, "atlas_fetal_rhesus_v2")
    output_split_seg = os.path.join(atlas_path, "Seg_Hemi")
    atlas_timepoints = [85, 97, 110, 122, 135, 147, 155]

    if not os.path.exists(output_split_seg):
        os.makedirs(output_split_seg)

    for subject in os.listdir(recons_folder):
        if subject != "Borgne":
            continue
        print(f"Starting {subject}")
        subject_output_split_seg = os.path.join(output_split_seg, subject)
        if not os.path.exists(subject_output_split_seg):
            os.makedirs(subject_output_split_seg)
        subject_path = os.path.join(recons_folder, subject)
        for session in os.listdir(subject_path):
            print(f"\tSession: {session}")
            session_subject_path = os.path.join(subject_path, session)
            recons_rhesus_folder = os.path.join(session_subject_path, "recons_rhesus/recon_template_space")
            t2_subj = os.path.join(recons_rhesus_folder, "srr_template_debiased.nii.gz")
            t2_subj_seg = os.path.join(cfg.BASE_NIOLON_PATH, "nnunet_pred_dataset_7_3000", f"{subject}_{session}.nii.gz")

            if not os.path.exists(t2_subj_seg):
                print(f"\tOriginal segmentation for {subject} {session} does not exist. Skipping...")
                continue

            # Charger le volume 3D original (référence)
            t2_subj_img = nib.load(t2_subj)
            fixed = ants.image_read(t2_subj)
            fixed_seg = ants.image_read(t2_subj_seg)

            # Trouver le meilleur atlas
            best_atlas = find_best_atlas(fixed, os.path.join(atlas_path, "Volumes"), atlas_timepoints)
            print(f"\tBest atlas: {best_atlas}")

            # Charger les masques
            moving_seg_file = os.path.join(atlas_path, "Segmentations", "structures_dilated", f"ONPRC_G{best_atlas}_NFseg_structures_dilated.nii.gz")
            hemi_splitted_seg = nib.load(moving_seg_file)
            nnunet_seg = nib.load(t2_subj_seg)

            # Rééchantillonner hemi_splitted_seg vers t2_subj_img
            hemi_resampled = resample_to_target(hemi_splitted_seg, t2_subj_img)
            hemi_data = hemi_resampled.get_fdata()
            tissue_data = nnunet_seg.get_fdata()

            # Créer la nouvelle segmentation (même taille que t2_subj_img)
            new_data = np.zeros_like(tissue_data, dtype=np.uint8)

            # Règles de mapping
            new_data[(hemi_data == 1) & (tissue_data == 1)] = 1  # CSF gauche
            new_data[(hemi_data == 1) & (tissue_data == 2)] = 2  # WM gauche
            new_data[(hemi_data == 1) & (tissue_data == 3)] = 3  # GM gauche
            new_data[(hemi_data == 1) & (tissue_data == 4)] = 4  # Ventricule gauche

            new_data[(hemi_data == 2) & (tissue_data == 1)] = 5  # CSF droit
            new_data[(hemi_data == 2) & (tissue_data == 2)] = 6  # WM droit
            new_data[(hemi_data == 2) & (tissue_data == 3)] = 7  # GM droit
            new_data[(hemi_data == 2) & (tissue_data == 4)] = 8  # Ventricule droit

            new_data[(hemi_data == 3)] = 9  # Tronc
            new_data[(hemi_data == 4)] = 10  # Cervelet

            # Sauvegarder avec l'affine et le header de t2_subj_img
            file_seg_out = os.path.join(subject_output_split_seg, f"{subject}_{session}_hemi.nii.gz")
            output_img = nib.Nifti1Image(new_data, t2_subj_img.affine, t2_subj_img.header)
            nib.save(output_img, file_seg_out)

            exit()
