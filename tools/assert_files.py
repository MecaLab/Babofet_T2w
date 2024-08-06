import sys
import os
import nibabel as nb
import numpy as np
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


def resample_to_reference():
    src = "/scratch/lbaptiste/data/dataset/babofet/subjects/sub-Formule_ses-08/scans/9-T2_HASTE_COR/resources/NIFTI/files/sub-Formule_ses-08_T2_HASTE_COR_9.nii"
    dst = "/scratch/lbaptiste/data/dataset/babofet/processing/sub-Formule_ses-08/brainmask/sub-Formule_ses-08_T2_HASTE_COR_9_brainmask.nii"

    img_src = nb.load(src)
    img_dst = nb.load(dst)

    resampled_img = resample_to_img(img_dst, img_src, interpolation='nearest')

    print(resampled_img.affine)
    print(img_src.affine)
    print(img_dst.affine)

    nb.save(resampled_img, "/scratch/lbaptiste/data/dataset/babofet/processing/sub-Formule_ses-08/brainmask/sub-Formule_ses-08_T2_HASTE_COR_9_brainmask_resampled_bis.nii")


if __name__ == "__main__":
    input_path = cfg.MESO_DATA_PATH
    dst_path = cfg.MESO_OUTPUT_PATH

    # check_files(input_path, dst_path)

    # check_size(input_path, dst_path)

    resample_to_reference()
