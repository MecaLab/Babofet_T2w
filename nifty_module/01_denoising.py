import os
import sys
import subprocess
sys.path.insert(0, os.path.abspath(os.curdir))
from tools import data_organization as tdo
import configuration as cfg


def nii2niigz(input_path):
    print("Starting compression of nii files in {}".format(input_path))
    for filename in os.listdir(input_path):
        if filename.endswith(".nii"):
            full_path = os.path.join(input_path, filename)
            subprocess.run(['gzip', '-v', '-f', full_path], check=True)


def denoising_data(input_path, output_path):
    DENOISING_PATH_EXE = os.path.join(cfg.SOFTS_PATH, "DenoiseImage")

    subject_IDs = os.listdir(input_path)

    for subject in subject_IDs:
        subj_output_dir = os.path.join(output_path, subject)
        if not os.path.exists(subj_output_dir):
            os.mkdir(subj_output_dir)

        print("Starting {}".format(subject))

        dir_list = os.listdir(os.path.join(input_path, subject, "scans"))
        haste_files = list()

        for d in dir_list:
            if "haste" in d.lower():
                haste_files.append(d)

        if len(haste_files) > 0:
            haste_subj_output_dir = os.path.join(subj_output_dir, "haste")
            bm_haste_subj_output_dir = os.path.join(subj_output_dir, "denoising")

            if not os.path.exists(haste_subj_output_dir):
                os.mkdir(haste_subj_output_dir)
            if not os.path.exists(bm_haste_subj_output_dir):
                os.mkdir(bm_haste_subj_output_dir)

            for f in haste_files:
                if "missfront" in f:
                    continue
                elif "ND" in f:
                    continue
                print("\t\tProcessing {}".format(f))
                nifti_filename, nifti_full_path = tdo.file_name_from_path(input_path, subject, f)
                if nifti_filename is None:
                    print("\t\t\tNo nifti found for {}".format(f))
                    continue
                s_nifti_filename = nifti_filename.split(".")
                bm_nifti_filename = s_nifti_filename[0] + "_denoised.nii"
                bm_full_path = os.path.join(bm_haste_subj_output_dir, bm_nifti_filename)

                input_full_path = os.path.join(nifti_full_path, nifti_filename)

                cmd = [DENOISING_PATH_EXE, "-i", input_full_path, "-o", bm_full_path]
                subprocess.run(cmd)

                print("\t\t\tEnd {}".format(nifti_filename))

            nii2niigz(bm_haste_subj_output_dir)

        print("Ending {}\n".format(subject))


def denoising_data_bids_format(input_path, output_path):
    DENOISING_PATH_EXE = os.path.join(cfg.SOFTS_PATH, "DenoiseImage")

    for folder in os.listdir(input_path):
        if folder.startswith("sub"):
            print(f"Processing {folder}")

            input_folder_path = os.path.join(input_path, folder)
            for session in os.listdir(input_folder_path):
                print(f"\t{session}")
            exit()



if __name__ == "__main__":

    """input_path = cfg.MESO_DATA_PATH
    output_path = cfg.MESO_OUTPUT_PATH
    denoising_data(input_path, output_path)"""
    input_path = os.path.join(cfg.SOURCEDATA_BIDS_PATH, "raw")
    output_path = os.path.join(cfg.DERIVATIVES_BIDS_PATH, "intermediate", "niftymic")

    denoising_data_bids_format(input_path, output_path)