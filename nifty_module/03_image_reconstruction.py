import os
import sys
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg


if __name__ == "__main__":
    base_path = cfg.MESO_DATA_PATH

    subject_IDs = os.listdir(base_path)
    subjects_failed = list()

    for subject in subject_IDs:
        subj_output_dir = os.path.join(cfg.MESO_OUTPUT_PATH, subject)
        if not os.path.exists(subj_output_dir):
            os.makedirs(subj_output_dir)

        print("Starting {}".format(subject))

        dir_list = os.listdir(os.path.join(subj_output_dir, "denoising"))
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
            bm_haste_subj_output_dir = os.path.join(subj_output_dir, "brainmask_niftymic")
            denoised_subj_output_dir = os.path.join(subj_output_dir, "denoising")
            recons_haste_subj_output_dir = os.path.join(haste_subj_output_dir, 'reconstruction_niftymic')

            if not os.path.exists(recons_haste_subj_output_dir):
                os.mkdir(recons_haste_subj_output_dir)

            anat_img = list()
            bm_img = list()
            for f in haste_files:
                filename = f.split(".")
                bm_nifti_filename = filename[0] + "_seg.nii.gz"

                anat_path_subj_path = os.path.join(denoised_subj_output_dir, f)
                bm_path_subj_path = os.path.join(bm_haste_subj_output_dir, filename[0], bm_nifti_filename)

                if os.path.exists(anat_path_subj_path) and os.path.exists(bm_path_subj_path):
                    print("OK")
                exit()