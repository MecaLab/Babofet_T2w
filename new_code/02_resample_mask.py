import os
import sys
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg
import subprocess
import time
import nibabel as nb
import numpy as np
from nilearn.image import resample_to_img

from tools import data_organization as tdo


if __name__ == '__main__':
    base_path = cfg.MESO_DATA_PATH

    subject_IDs = os.listdir(base_path)
    subject_processed_haste = list()
    subject_processed_truefisp = list()

    for subject in subject_IDs:
        subj_output_dir = os.path.join(cfg.MESO_OUTPUT_PATH, subject)

        print("Starting {}".format(subject))

        dir_list = os.listdir(os.path.join(base_path, subject, "scans"))
        haste_files = list()
        truefisp_files = list()

        for d in dir_list:
            d_lower = d.lower()
            if "haste" in d_lower:
                haste_files.append(d)
            if "trufi" in d_lower:
                truefisp_files.append(d)

        if len(haste_files) > 0:
            print("\tStarting HASTE {}".format(subject))
            haste_subj_output_dir = os.path.join(subj_output_dir, "haste")
            bm_haste_subj_output_dir = os.path.join(subj_output_dir, "brainmask")

            for f in haste_files:
                nifti_filename, nifti_full_path = tdo.file_name_from_path(base_path, subject, f)
                s_nifti_filename = nifti_filename.split(".")
                bm_nifti_filename = s_nifti_filename[0] + "_brainmask.nii"

                output_filename = s_nifti_filename[0] + "_brainmask_resampled.nii"

                if not os.path.exists(os.path.join(bm_haste_subj_output_dir, output_filename)):
                    print("\t\tComputing resampling HASTE {}".format(bm_nifti_filename))
                    img_src = nb.load(os.path.join(nifti_full_path, nifti_filename))
                    img_mask = nb.load(os.path.join(bm_haste_subj_output_dir, bm_nifti_filename))

                    resampled_img = resample_to_img(img_mask, img_src)

                    nb.save(resampled_img, os.path.join(bm_haste_subj_output_dir, output_filename))
                else:
                    print("\t\tSkiped HASTE {}".format(output_filename))

            print("\tEnding HASTE {}".format(subject))

        if len(truefisp_files) > 0:
            print("\tStarting TRUEFISP {}".format(subject))
            truefisp_subj_output_dir = os.path.join(subj_output_dir, "truefisp")
            bm_truefisp_subj_output_dir = os.path.join(subj_output_dir, "brainmask")

            for f in truefisp_files:
                nifti_filename, nifti_full_path = tdo.file_name_from_path(base_path, subject, f)
                s_nifti_filename = nifti_filename.split(".")
                bm_nifti_filename = s_nifti_filename[0] + "_brainmask.nii"

                output_filename = s_nifti_filename[0] + "_brainmask_resampled.nii"

                if not os.path.exists(os.path.join(bm_truefisp_subj_output_dir, output_filename)):
                    print("\t\tComputing resampling TRUEFISP {}".format(bm_nifti_filename))
                    img_src = nb.load(os.path.join(nifti_full_path, nifti_filename))
                    img_mask = nb.load(os.path.join(bm_truefisp_subj_output_dir, bm_nifti_filename))

                    resampled_img = resample_to_img(img_mask, img_src)

                    nb.save(resampled_img, os.path.join(bm_truefisp_subj_output_dir, output_filename))
                else:
                    print("\t\tSkiped TRUEFISP {}".format(bm_nifti_filename))
            print("\tEnding TRUEFISP {}".format(subject))

        print("Ending {}\n".format(subject))
