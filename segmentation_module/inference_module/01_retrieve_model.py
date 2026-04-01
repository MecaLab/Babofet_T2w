import subprocess
import sys
import os


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
        # run() waits for the command to finish
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print(result)
        print("File retrieved successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error during scp: {e.stderr}")
        return False


if __name__ == "__main__":
    zip_server_path = sys.argv[1]
    dst_path = sys.argv[2]
    retrieve_zip(zip_server_path, dst_path)