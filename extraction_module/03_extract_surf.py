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
                output_file = session_file.replace("_hemi.nii.gz", f".{label_name}.white.gii")

                input_full_path = f"/home/atlas_fetal_rhesus_v2/Seg_Hemi/{subject}/{session_file}"
                output_full_path = f"/home/atlas_fetal_rhesus_v2/Surf_Hemi/{subject}/{output_file}"

                subprocess.run([
                    "singularity", "run", "-B", f"{base_path}:/home", "surf_proc_v0.0.2a.sif",
                    "generate_mesh", "-s", input_full_path , "-l", str(label_val), "-m", output_full_path
                ], check=True)

                exit()
                """
                singularity run -B /scratch/lbaptiste/surface_processing/:/home surface_processing/surf_proc_v0.0.2a.sif
                 generate_mesh -s /home/Borgne_ses06_hemi.nii.gz -l 2 -m /home/Borgne_ses06.right.white.gii
                """