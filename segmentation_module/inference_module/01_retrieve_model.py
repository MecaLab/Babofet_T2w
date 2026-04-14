import subprocess
import zipfile
import sys
import os
import argparse
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg

def retrieve_zip(zip_server_path, dst_path):
    MESO_USER = "lbaptiste"
    MESO_HOST = "login.mesocentre.univ-amu.fr"
    MESO_PORT = "8822"

    # Construct the remote source string: user@host:path
    remote_source = f"{MESO_USER}@{MESO_HOST}:{zip_server_path}"

    # Build the command list for subprocess
    # -P (uppercase) is used for the port in scp
    command = [
        "scp",
        "-P", MESO_PORT,
        remote_source,
        dst_path
    ]

    try:
        print(f"Executing: {' '.join(command)}")
        subprocess.run(command, check=True, capture_output=True, text=True)
        print("File retrieved successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error during scp: {e.stderr}")
        return False


def unzip_file(zip_path, extract_to):
    """
    Unzips a ZIP archive to a specific destination.
    """
    if not os.path.exists(zip_path):
        print(f"Error: The file {zip_path} does not exist.")
        return False

    # Create destination directory if it doesn't exist
    if not os.path.exists(extract_to):
        os.makedirs(extract_to)

    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
            print(f"Success: Extracted to {extract_to}")
            return True
    except zipfile.BadZipFile:
        print("Error: The file is corrupted or not a zip file.")
        return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export a trained model to a ZIP file")

    parser.add_argument(
        "--server_path",
        help="Path to the zip file on the server (mesocentre)",
        required=True
    )
    parser.add_argument(
        "--dst_path",
        help="Path to where save the zip file",
        required=True
    )
    args = parser.parse_args()

    zip_server_path = args.server_path
    dst_path = args.dst_path

    if not os.path.exists(dst_path):
        retrieve_zip(zip_server_path, dst_path)

    folder_name = os.path.basename(dst_path).split(".")[0]  # DatasetXXX_NAME.zip => DatasetXXX_NAME

    output_longi_folder = os.path.join(cfg.LONGISEG_RESULTS_PATH, folder_name)
    unzip_file(dst_path, output_longi_folder)
