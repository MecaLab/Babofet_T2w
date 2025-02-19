import subprocess
import os
import sys

if __name__ == "__main__":

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    dims = subprocess.run(f"fslval {input_file} dim3", shell=True, capture_output=True, text=True)
    print(dims)
