import os
import sys
import subprocess
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg


if __name__ == "__main__":
    intermediate_path = os.path.join(cfg.DERIVATIVES_BIDS_PATH, "intermediate", "surf-slam")
    input_split_seg = os.path.join(intermediate_path, "Seg_Hemi")

    dst_path = os.path.join(cfg.DERIVATIVES_BIDS_PATH, "surf-slam")
    if not os.path.exists(dst_path):
        os.makedirs(dst_path)

    labels_map = {
        "R": 2,  # WM right
        "L": 6,  # WM left
    }

    args_extraction = sys.argv[1]  # should be viz or full

    for subject in os.listdir(input_split_seg):
        subject_src_path = os.path.join(input_split_seg, subject)
        subject_dst_path = os.path.join(dst_path, subject)

        if not os.path.exists(subject_dst_path):
            os.makedirs(subject_dst_path)

        print(f"Processing subject: {subject}")

        for session in os.listdir(subject_src_path):
            hemi_split_basename = f"{subject}_{session}_hemi.nii.gz"
            session_file = os.path.join(subject_src_path, session, hemi_split_basename)

            if not os.path.exists(session_file):
                continue

            print(f"\tProcessing session: {session}")
            full_subject_dst_path = os.path.join(subject_dst_path, session, "anat")
            if not os.path.exists(full_subject_dst_path):
                os.makedirs(full_subject_dst_path)

            for label_name, label_val in labels_map.items():
                print(f"\t\tProcessing {label_name}")

                # sub-<sub>_ses-<ses>_hemi-L_white.surf.gii
                output_file_pattern = f"{subject}_{session}_hemi-{label_name}_white.surf.gii"

                if os.path.exists(os.path.join(full_subject_dst_path, output_file_pattern)):
                    print(f"\t\t\tOutput file {output_file_pattern} already exists. Skipping.")
                    continue

                output_full_path = os.path.join(full_subject_dst_path, output_file_pattern)

                if args_extraction == "viz":
                    input_full_path = os.path.join(subject_src_path, session, session_file)


                    subprocess.run([
                        "python", "surface_processing/generate_mesh.py",
                        "-s", input_full_path,
                        "-l", str(label_val),
                        "-m", output_full_path,
                        "-r", "0",
                        "-n", "10"
                    ], check=True)
                elif args_extraction == "full":
                    surf_proc_soft_path = os.path.join(cfg.SOFTS_PATH, "surf_proc_v0.0.2a.sif")
                    # input_full_path = f"/home/atlas_fetal_rhesus_v2/Seg_Hemi/{subject}/{session}/{session_file}"
                    # output_full_path = f"/home/atlas_fetal_rhesus_v2/Surf_Hemi/{subject}/{output_file_pattern}"

                    input_full_path = f"/home/{session_file}"
                    output_full_path = f"/output/{output_full_path}"

                    subprocess.run([
                        "singularity", "run",
                        "-B", f"{input_split_seg}:/home/",
                        "-B", f"{dst_path}:/output/",
                        surf_proc_soft_path,
                        "generate_mesh", "-s", input_full_path, "-l", str(label_val), "-m", output_full_path
                    ], check=True)