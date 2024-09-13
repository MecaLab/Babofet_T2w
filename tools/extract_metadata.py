import sys
import os
import glob
import pandas as pd
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg
from pydicom import dcmread


def get_field(dicom, field):
    try:
        return dicom[field].value
    except:
        return None


def get_dicom_file_metadata(path_dicom, fields):
    """Extract fields of interest from a dicom file

    Extract the fields of interest from a dicom file (e.g. PatientID)
    and store their value inside a DataFrame.

    Parameters
    ----------
    path_dicom: dicom file, a loaded dicom file
    fields: list of str, dicom fields to retrieve

    Returns
    -------
    Object, value stored in the dicom field
    """
    # do not read the image (faster) and query the field
    try:
        dicom = dcmread(path_dicom, stop_before_pixels=True)
        metadata = {f: [get_field(dicom, f)] for f in fields}
        print(dicom)
    except:
        metadata = {f: ["extraction_error"] for f in fields}
    finally:
        metadata["file_path"] = path_dicom
        df = pd.DataFrame(metadata)
    return df


def get_dicom_directory_metadata(directory, fields, path_df):
    all_files = glob.iglob(os.path.join(directory, "**"), recursive=True)
    only_files = (f for f in all_files if os.path.isfile(f))
    # remove .info dicom files if any
    only_dcm_files = (f for f in only_files if ".info" not in f)
    # extract metadata per file and concatenate them at the directory level

    dfs = (get_dicom_file_metadata(f, fields) for f in only_dcm_files)

    print(dfs)


if __name__ == "__main__":
    get_dicom_directory_metadata(
        directory=cfg.MESO_OUTPUT_PATH,
        fields=cfg.DICOM_META_TO_EXTRACT,
        path_df="",
    )