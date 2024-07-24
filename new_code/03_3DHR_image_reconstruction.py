import os
import sys
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg
import subprocess

from tools import data_organization as tdo


if __name__ == '__main__':
    base_path = cfg.MESO_DATA_PATH

    subject_IDs = os.listdir(base_path)
    subjects_failed = list()

    recon_approach = "ebner"

    for subject in subject_IDs:
        subj_output_dir = os.path.join(cfg.MESO_OUTPUT_PATH, subject)
        if not os.path.exists(subj_output_dir):
            os.makedirs(subj_output_dir)

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
            recons_haste_subj_output_dir = os.path.join(haste_subj_output_dir, 'reconstruction_' + recon_approach)

            if not os.path.exists(haste_subj_output_dir):
                os.mkdir(haste_subj_output_dir)
            if not os.path.exists(bm_haste_subj_output_dir):
                os.mkdir(bm_haste_subj_output_dir)
            if not os.path.exists(recons_haste_subj_output_dir):
                os.mkdir(recons_haste_subj_output_dir)

            anat_img = list()
            bm_img = list()
            for f in haste_files:
                nifti_filename, nifti_full_path = tdo.file_name_from_path(base_path, subject, f)
                s_nifti_filename = nifti_filename.split(".")
                bm_nifti_filename = s_nifti_filename[0] + "_brainmask.nii"
                bm_output_file = os.path.join(bm_haste_subj_output_dir, bm_nifti_filename)

                if os.path.exists(nifti_full_path) and os.path.exists(bm_output_file):
                    anat_img.append(nifti_full_path)
                    bm_img.append(bm_output_file)

                if len(bm_img) > 2:
                    recons_haste_subj_output = os.path.join(recons_haste_subj_output_dir, subject + '_haste_3DHR.nii.gz')
                    motion_subfolder = os.path.join(recons_haste_subj_output_dir, 'motion_correction')

                    if os.path.exists(recons_haste_subj_output):
                        print('\t\tSkipped reconstruction HASTE for {}'.format(subject))
                    else:
                        if not os.path.exists(motion_subfolder):
                            os.mkdir(motion_subfolder)
                        cmd_os = 'niftymic_reconstruct_volume --filenames '
                        for v in anat_img:
                            cmd_os += v + ' '
                        cmd_os += " --filenames-masks "
                        for v in bm_img:
                            cmd_os += v + ' '

                        cmd_os += ' --output ' + recons_haste_subj_output
                        cmd_os += ' --alpha 0.01 --threshold-first 0.6 --threshold 0.7 --intensity-correction 1 --bias-field-correction 1 --isotropic-resolution 0.5'
                        cmd_os += ' --dilation-radius 5'
                        cmd_os += ' --subfolder-motion-correction ' + motion_subfolder
                        cmd_os += ' --use-masks-srr 1'

                        print(cmd_os)
                break
            break
        break