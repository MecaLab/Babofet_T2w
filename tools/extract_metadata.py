import sys
import os
import glob
import pandas as pd
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg


def get_field(dicom, field):
    try:
        return dicom[field].value
    except:
        return None


def get_dicom_directory_metadata(directory, fields, path_df):
    all_files = glob.iglob(os.path.join(directory, "**"), recursive=True)
    print(all_files)


if __name__ == "__main__":
    get_dicom_directory_metadata(
        directory=cfg.MESO_OUTPUT_PATH,
        fields=cfg.DICOM_META_TO_EXTRACT,
        path_df="",
    )