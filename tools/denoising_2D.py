import os
import sys
sys.path.insert(0, os.path.abspath(os.curdir))
import subprocess

from tools import data_organization as tdo


def denoising_data(input_path, output_path):
    base_path = input_path

    subject_IDs = os.listdir(base_path)

    for subject in subject_IDs:
        subj_output_dir = os.path.join(output_path, subject)
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
            print("\tStarting HASTE {}".format(subject))
            haste_subj_output_dir = os.path.join(subj_output_dir, "haste")
            bm_haste_subj_output_dir = os.path.join(subj_output_dir, "denoising")

            if not os.path.exists(haste_subj_output_dir):
                os.mkdir(haste_subj_output_dir)
            if not os.path.exists(bm_haste_subj_output_dir):
                os.mkdir(bm_haste_subj_output_dir)

            for f in haste_files:
                print(f)
                exit()
                nifti_filename, nifti_full_path = tdo.file_name_from_path(base_path, subject, f)
                s_nifti_filename = nifti_filename.split(".")
                bm_nifti_filename = s_nifti_filename[0] + "_denoised.nii"
                bm_full_path = os.path.join(bm_haste_subj_output_dir, bm_nifti_filename)

                input_full_path = os.path.join(nifti_full_path, nifti_filename)

                cmd = ["/scratch/lbaptiste/softs/DenoiseImage", "-i"]
                cmd.append(input_full_path)
                cmd.append("-o")
                cmd.append(bm_full_path)

                subprocess.run(cmd)

                print("\t\tEnd {}".format(nifti_filename))

            print("\tEnding HASTE {}".format(subject))

        if len(truefisp_files) > 0:
            print("\tStarting TRUEFISP {}".format(subject))
            truefisp_subj_output_dir = os.path.join(subj_output_dir, "truefisp")
            bm_truefisp_subj_output_dir = os.path.join(subj_output_dir, "denoising")

            if not os.path.exists(truefisp_subj_output_dir):
                os.mkdir(truefisp_subj_output_dir)
            if not os.path.exists(bm_truefisp_subj_output_dir):
                os.mkdir(bm_truefisp_subj_output_dir)

            for f in truefisp_files:
                nifti_filename, nifti_full_path = tdo.file_name_from_path(base_path, subject, f)
                s_nifti_filename = nifti_filename.split(".")
                bm_nifti_filename = s_nifti_filename[0] + "_denoised.nii"
                bm_full_path = os.path.join(bm_truefisp_subj_output_dir, bm_nifti_filename)

                input_full_path = os.path.join(nifti_full_path, nifti_filename)

                if os.path.exists(bm_full_path):
                    print("\t\tSkipped {}".format(nifti_filename))
                else:
                    cmd = ["/scratch/lbaptiste/softs/DenoiseImage", "-i"]
                    cmd.append(input_full_path)
                    cmd.append("-o")
                    cmd.append(bm_full_path)

                    subprocess.run(cmd)

                    print("\t\tEnd {}".format(nifti_filename))
            print("\tEnding TRUEFISP {}".format(subject))

        print("Ending {}\n".format(subject))