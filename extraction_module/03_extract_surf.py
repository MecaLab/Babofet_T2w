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

    suffix = "_corrected"

    if not os.path.exists(dst_path):
        os.makedirs(dst_path)

    for subject in os.listdir(src_path):
        subject_src_path = os.path.join(src_path, subject)
        subject_dst_path = os.path.join(dst_path, subject)

        if not os.path.exists(subject_dst_path):
            os.makedirs(subject_dst_path)

        print(f"Processing subject: {subject}")

        for session in os.listdir(subject_src_path):
            session_file = f"{subject}_{session}_hemi{suffix}.nii.gz"
            if not os.path.exists(os.path.join(subject_src_path, session, session_file)):
                continue
            print(f"\tSession file: {session_file}")

            for label_name, label_val in labels_map.items():
                print(f"\t\tProcessing {label_name}")
                output_file = session_file.replace("_hemi.nii.gz", f".{label_name}.white.gii")

                if os.path.exists(os.path.join(subject_dst_path, output_file)):
                    print(f"\t\t\tOutput file {output_file} already exists. Skipping.")
                    continue

                input_full_path = f"/home/atlas_fetal_rhesus_v2/Seg_Hemi/{subject}/{session}/{session_file}"
                output_full_path = f"/home/atlas_fetal_rhesus_v2/Surf_Hemi/{subject}/{output_file}"


                subprocess.run([
                    "singularity", "run", "-B", f"{base_path}:/home/atlas_fetal_rhesus_v2", "surf_proc_v0.0.2a.sif",
                    "generate_mesh", "-s", input_full_path, "-l", str(label_val), "-m", output_full_path
                ], check=True)