import os
import sys
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg
import subprocess


if __name__ == "__main__":
    base_path = os.path.join(cfg.BASE_NIOLON_PATH, "atlas_fetal_rhesus_v2")
    src_path = os.path.join(base_path, "Seg_Hemi")
    dst_path = os.path.join(base_path, "Surf_Hemi")

    labels_map = {
        "right": 2,  # WM right
        "left": 6,  # WM left
    }

    if not os.path.exists(dst_path):
        os.makedirs(dst_path)

    for subject in os.listdir(src_path):
        subject_src_path = os.path.join(src_path, subject)
        subject_dst_path = os.path.join(dst_path, subject)

        if not os.path.exists(subject_dst_path):
            os.makedirs(subject_dst_path)

        print(f"Starting {subject}")
        for session_file in os.listdir(subject_src_path):
            print(f"\tSession file: {session_file}")
            for label_name, label_val in labels_map.items():
                print(f"\t\tProcessing {label_name}")
                input_file = os.path.join(subject_src_path, session_file)
                output_file = os.path.join(subject_dst_path, session_file.replace("_hemi.nii.gz", f"_{label_name}.white.gii"))

                subprocess.run([
                    "singularity", "run", "-B", f"{base_path}:/home", "surf_proc_v0.0.2a.sif",
                    "generate_mesh", "-s", f"/home/Seg_Hemi/{input_file}", "-l", str(label_val), "-m", f"/home/Surf_Hemi/{output_file}"
                ], check=True)

                exit()
                """
                singularity run -B /scratch/lbaptiste/surface_processing/:/home surface_processing/surf_proc_v0.0.2a.sif
                 generate_mesh -s /home/Borgne_ses06_hemi.nii.gz -l 2 -m /home/Borgne_ses06.right.white.gii
                """