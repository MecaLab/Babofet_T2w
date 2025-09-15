import os
import subprocess
import sys
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg


def run_cmd(cmd):
    print(" ".join(cmd))
    subprocess.run(cmd, check=True)


if __name__ == "__main__":
    atlas_path = os.path.join(cfg.BASE_NIOLON_PATH, "atlas_fetal_rhesus_v2")

    seg_folder = os.path.join(atlas_path, "Segmentations")

    atlas_timepoints = [85, 97, 110, 122, 135, 147, 155]

    tmp_dir = os.path.join(seg_folder, "tmp")
    tmp_files = []

    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)

    labels = [1, 2, 3]

    input_mask = os.path.join(seg_folder, "ONPRC_G85_NFseg_3.nii.gz")
    output_mask = os.path.join(seg_folder, "ONPRC_G85_NFseg_3_dilall_new.nii.gz")

    for label in labels:
        out_bin = os.path.join(tmp_dir, f"label_{label}.nii.gz")
        run_cmd(["fslmaths", input_mask, "-thr", str(label), "-uthr", str(label), out_bin])
        tmp_files.append(out_bin)

    """
    for ts in atlas_timepoints:

        filename_in = os.path.join(seg_folder, f"ONPRC_G{ts}_NFseg_3.nii.gz")
        if not os.path.exists(filename_in):
            print(f"Error ! File {filename_in} does not exists. Run the previous script")
            continue
        filename_out = os.path.join(seg_folder, f"ONPRC_G{ts}_NFseg_3_dilall.nii.gz")

        print(f"Computing: {filename_in}")

        command = f"fslmaths {filename_in} -dilM -dilM -dilM -dilM {filename_out}"
        subprocess.run(command, shell=True)

        command = f"fslmaths {filename_out} -uthr 3.5 {filename_out}"
        subprocess.run(command, shell=True, check=True)

        command = f"fslmaths {filename_out} -dilM {filename_out}"
        subprocess.run(command, shell=True, check=True)

        command = f"fslmaths {filename_out} -ero {filename_out}"
        subprocess.run(command, shell=True)"""


