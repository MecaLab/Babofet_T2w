import os


def file_name_from_path(input_path, subject, f):
    full_path = os.path.join(input_path, subject, "scans", f, "resources", "NIFTI", "files")
    for file in os.listdir(full_path):
        if file.endswith(".nii") or file.endswith("nii.gz"):
            return file, full_path
