import sys
import os

sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg
from tools import data_organization as tdo


def check_haste_files(origin_path, destination_path):
    cpt_fail = 0
    files_failed = list()
    for subj in os.listdir(origin_path):

        dir_list = os.listdir(os.path.join(origin_path, subj, "scans"))
        haste_files = list()

        for d in dir_list:
            d_lower = d.lower()
            if "haste" in d_lower:
                haste_files.append(d)

        for f in haste_files:
            nifti_filename, nifti_full_path = tdo.file_name_from_path(origin_path, subj, f)
            brainmask_filename = nifti_filename.replace(".nii", "_brainmask.nii")

            brainmask_full_path = os.path.join(destination_path, subj, "brainmask", brainmask_filename)
            if not os.path.exists(brainmask_full_path):
                cpt_fail += 1
                files_failed.append(os.path.join(nifti_full_path, nifti_filename))

    if cpt_fail != 0:
        print("Number of failed files: ", cpt_fail)
        print(files_failed)
    else:
        print("Everything OK")


def check_truefisp_files(origin_path, destination_path):
    cpt_fail = 0
    files_failed = list()
    for subj in os.listdir(origin_path):

        dir_list = os.listdir(os.path.join(origin_path, subj, "scans"))
        truefisp_files = list()

        for d in dir_list:
            d_lower = d.lower()
            if "trufi" in d_lower:
                truefisp_files.append(d)

        for f in truefisp_files:
            nifti_filename, nifti_full_path = tdo.file_name_from_path(origin_path, subj, f)
            brainmask_filename = nifti_filename.replace(".nii", "_brainmask.nii")

            brainmask_full_path = os.path.join(destination_path, subj, "brainmask", brainmask_filename)
            if not os.path.exists(brainmask_full_path):
                cpt_fail += 1
                files_failed.append(os.path.join(nifti_full_path, nifti_filename))

    if cpt_fail != 0:
        print("Number of failed files: ", cpt_fail)
        print(files_failed)
    else:
        print("Everything OK")


if __name__ == "__main__":
    input_path = cfg.MESO_DATA_PATH
    dst_path = cfg.MESO_OUTPUT_PATH

    check_haste_files(input_path, dst_path)
    check_truefisp_files(input_path, dst_path)
