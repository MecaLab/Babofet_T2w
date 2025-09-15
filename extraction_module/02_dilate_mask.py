import os
import subprocess
import sys
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg


def dilate_bm(filename_in, filename_out):
    print(f"\tComputing: {filename_in}")

    command = f"fslmaths {filename_in} -dilM -dilM -dilM -dilM {filename_out}"
    subprocess.run(command, shell=True)

    command = f"fslmaths {filename_out} -uthr 3.5 {filename_out}"
    subprocess.run(command, shell=True, check=True)

    command = f"fslmaths {filename_out} -dilM {filename_out}"
    subprocess.run(command, shell=True, check=True)

    command = f"fslmaths {filename_out} -ero {filename_out}"
    subprocess.run(command, shell=True)

    print(f"\tOutput: {filename_out}")


def dilate_bm_bis(input_file, output_file):
    print(f"\tComputing: {input_file}")

    command = f"fslmaths {input_file} -dilM -dilM -dilM -dilM -dillall {output_file}"
    subprocess.run(command, shell=True)

    command = f"fslmaths {output_file} -uthr 3.5 {output_file}"
    subprocess.run(command, shell=True)

    command = f"fslmaths {output_file} -dilM {output_file}"
    subprocess.run(command, shell=True)

    command = f"fslmaths {output_file} -ero {output_file}"
    subprocess.run(command, shell=True)

    print(f"\tOutput: {output_file}")


if __name__ == "__main__":
    atlas_path = os.path.join(cfg.BASE_NIOLON_PATH, "atlas_fetal_rhesus_v2")

    seg_folder = os.path.join(atlas_path, "Segmentations")

    atlas_timepoints = [85, 97, 110, 122, 135, 147, 155]

    for ts in atlas_timepoints:

        filename_in = os.path.join(seg_folder, f"ONPRC_G{ts}_NFseg_3.nii.gz")
        if not os.path.exists(filename_in):
            print(f"Error ! File {filename_in} does not exists. Run the previous script")
            continue
        filename_out = os.path.join(seg_folder, "tmp", f"ONPRC_G{ts}_NFseg_3_dilall.nii.gz")

        # dilate_bm(filename_in, filename_out)
        dilate_bm_bis(filename_in, filename_out)
        break


