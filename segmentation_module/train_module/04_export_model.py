import shutil
import sys
import os

def compress_path(source_path):
    """
    Compresses a file or directory into a ZIP archive.
    """
    # Check if the source exists
    if not os.path.exists(source_path):
        print(f"Error: The path '{source_path}' does not exist.")
        return

    output_filename = os.path.basename(os.path.normpath(source_path))

    try:
        # shutil.make_archive handles both files and directories
        # format='zip' is specified here
        archive_path = shutil.make_archive(output_filename, 'zip', source_path)
        print(f"Success: Archive created at {archive_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    path_to_zip = sys.argv[1]
    compress_path(path_to_zip)