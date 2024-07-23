import os
import sys
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg
import subprocess
import time

from tools import data_organization as tdo


if __name__ == '__main__':
    base_path = cfg.MESO_DATA_PATH

    subject_IDs = os.listdir(base_path)
    subject_processed_haste = list()
    subject_processed_truefisp = list()

    for subject in subject_IDs:
        subj_output_dir = os.path.join(cfg.MESO_OUTPUT_PATH, subject)
        if not os.path.exists(subj_output_dir):
            os.mkdir(subj_output_dir)

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
            haste_subj_output_dir = os.path.join(subj_output_dir, "haste")
            bm_haste_subj_output_dir = os.path.join(subj_output_dir, "denoising")

            if not os.path.exists(haste_subj_output_dir):
                os.mkdir(haste_subj_output_dir)
            if not os.path.exists(bm_haste_subj_output_dir):
                os.mkdir(bm_haste_subj_output_dir)

            for f in haste_files:
                nifti_filename, nifti_full_path = tdo.file_name_from_path(base_path, subject, f)
                s_nifti_filename = nifti_filename.split(".")
                bm_nifti_filename = s_nifti_filename[0] + "_denoised.nii"
                bm_full_path = os.path.join(bm_haste_subj_output_dir, bm_nifti_filename)

                input_full_path = os.path.join(nifti_full_path, nifti_filename)

                if os.path.exists(bm_full_path):
                    print("\tSkipped {}".format(nifti_filename))
                else:
                    cmd = ["/scratch/lbaptiste/softs/DenoiseImage", "-i"]
                    cmd.append(input_full_path)
                    cmd.append("-o")
                    cmd.append(bm_full_path)

                    subprocess.run(cmd)

                    print("\tEnd {}".format(nifti_filename))

            print("Ending {}".format(subject))