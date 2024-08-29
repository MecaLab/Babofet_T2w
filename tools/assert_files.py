import sys
import os
import nibabel as nb
import numpy as np
import tempfile
from nilearn.image import resample_to_img

sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg
from tools import data_organization as tdo


def check_files(origin_path, destination_path):
    cpt_fail_haste = 0
    cpt_fail_truefisp = 0
    files_failed_haste = list()
    files_failed_truefisp = list()

    for subj in os.listdir(origin_path):

        dir_list = os.listdir(os.path.join(origin_path, subj, "scans"))
        haste_files = list()
        truefisp_files = list()

        for d in dir_list:
            d_lower = d.lower()
            if "trufi" in d_lower:
                truefisp_files.append(d)
            if "haste" in d_lower:
                haste_files.append(d)

        for f in haste_files:
            nifti_filename, nifti_full_path = tdo.file_name_from_path(origin_path, subj, f)
            brainmask_filename = nifti_filename.replace(".nii", "_denoised_brainmask.nii")

            brainmask_full_path = os.path.join(destination_path, subj, "brainmask", brainmask_filename)
            if not os.path.exists(brainmask_full_path):
                cpt_fail_haste += 1
                files_failed_haste.append(os.path.join(nifti_full_path, nifti_filename))

        for f in truefisp_files:
            nifti_filename, nifti_full_path = tdo.file_name_from_path(origin_path, subj, f)
            brainmask_filename = nifti_filename.replace(".nii", "_denoised_brainmask.nii")

            brainmask_full_path = os.path.join(destination_path, subj, "brainmask", brainmask_filename)
            if not os.path.exists(brainmask_full_path):
                cpt_fail_truefisp += 1
                files_failed_truefisp.append(os.path.join(nifti_full_path, nifti_filename))

    if cpt_fail_haste != 0:
        print("Number of failed HASTE files: ", cpt_fail_haste)
        print(files_failed_haste)
    else:
        print("Everything OK for HASTE")

    if cpt_fail_truefisp != 0:
        print("Number of failed TRUEFISP files: ", cpt_fail_truefisp)
        print(files_failed_truefisp)
    else:
        print("Everything OK for TRUEFISP")


def check_size(origin_path, destination_path):
    cpt_fail_haste = 0
    cpt_fail_truefisp = 0

    for subj in os.listdir(origin_path):
        dir_list = os.listdir(os.path.join(origin_path, subj, "scans"))
        haste_files = list()
        truefisp_files = list()

        for d in dir_list:
            d_lower = d.lower()
            if "trufi" in d_lower:
                truefisp_files.append(d)
            if "haste" in d_lower:
                haste_files.append(d)

        for f in haste_files:
            nifti_filename, nifti_full_path = tdo.file_name_from_path(origin_path, subj, f)
            brainmask_filename = nifti_filename.replace(".nii", "_brainmask.nii")

            brainmask_full_path = os.path.join(destination_path, subj, "brainmask", brainmask_filename)

            img_src = nb.load(os.path.join(nifti_full_path, nifti_filename))
            img_dst = nb.load(brainmask_full_path)

            if img_src.shape != img_dst.shape:
                cpt_fail_haste += 1

            if not np.allclose(img_src.affine, img_dst.affine):
                cpt_fail_haste += 1

        for f in truefisp_files:
            nifti_filename, nifti_full_path = tdo.file_name_from_path(origin_path, subj, f)
            brainmask_filename = nifti_filename.replace(".nii", "_brainmask.nii")

            brainmask_full_path = os.path.join(destination_path, subj, "brainmask", brainmask_filename)

            img_src = nb.load(os.path.join(nifti_full_path, nifti_filename))
            img_dst = nb.load(brainmask_full_path)

            if img_src.shape != img_dst.shape:
                cpt_fail_truefisp += 1

            if not np.allclose(img_src.affine, img_dst.affine):
                cpt_fail_truefisp += 1

    if cpt_fail_haste != 0:
        print("Number of failed HASTE files: ", cpt_fail_haste)
    else:
        print("Everything OK for HASTE")

    if cpt_fail_truefisp != 0:
        print("Number of failed TRUEFISP files: ", cpt_fail_truefisp)
    else:
        print("Everything OK for TRUEFISP")


def check_intersection(path, look_for="sub-Aziza_ses-04"):

    for subj in os.listdir(path):
        if look_for == subj:
            subj_dir = os.path.join(path, subj)

            denoised_path = os.path.join(subj_dir, "denoising")
            brainmask_path = os.path.join(subj_dir, "brainmask_niftymic")

            for file in os.listdir(denoised_path):
                if "HASTE" in file:
                    brainmask_file = file.replace(".nii", "_seg.nii.gz")

                    anat_img = nb.load(os.path.join(denoised_path, file))
                    brainmask_img = nb.load(os.path.join(brainmask_path, brainmask_file))

                    anat_data = anat_img.get_fdata()
                    brainmask_data = brainmask_img.get_fdata()

                    with tempfile.NamedTemporaryFile(suffix=".nii.gz") as tmpfile_mask:
                        print(f"Computing {file}")
                        data = np.ones_like(brainmask_data)
                        data[brainmask_data == 1] = 2

                        intersection = np.logical_and(anat_data > 0, data > 0)

                        n_voxel = np.sum(intersection)

                        total_voxels = np.prod(anat_data.shape)
                        print(f"\tNombre total de voxels dans l'image : {total_voxels}")

                        if n_voxel > 0:
                            print(f"\tIl y a {n_voxel} voxels où l'intersection est non nulle")
                        else:
                            print("\tIl n'y a pas d'intersection non nulle entre le brainmask et l'image anat")
            exit()


def check_data_img(path, subj):
    subj_dir = os.path.join(path, subj)

    denoised_path = os.path.join(subj_dir, "denoising")
    brainmask_path = os.path.join(subj_dir, "brainmask_niftymic")

    for file in os.listdir(denoised_path):
        if "HASTE" in file:
            print(file)
            brainmask_file = file.replace(".nii", "_seg.nii.gz")

            anat_img = nb.load(os.path.join(denoised_path, file))
            brainmask_img = nb.load(os.path.join(brainmask_path, brainmask_file))

            anat_data = anat_img.get_fdata()
            brainmask_data = brainmask_img.get_fdata()

            print(f"\tAnat shape: {anat_data.shape} | BM shape: {brainmask_data.shape}")





if __name__ == "__main__":
    input_path = cfg.MESO_DATA_PATH
    dst_path = cfg.MESO_OUTPUT_PATH

    # check_files(input_path, dst_path)

    # check_size(input_path, dst_path)

    #check_intersection(dst_path)

    check_data_img(dst_path, "sub-Aziza_ses-04")