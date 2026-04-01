import subprocess
import zipfile
import sys
import os
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
    zip_server_path = sys.argv[1]
    dst_path = sys.argv[2]
    # retrieve_zip(zip_server_path, dst_path)
    exit()
    output_longi = os.path.join(cfg.LONGISEG_RESULTS_PATH, )
    unzip_file(dst_path, cfg.LONGISEG_RESULTS_PATH)
