import subprocess
import os
import sys

if __name__ == "__main__":

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    result = subprocess.run(f"fslval {input_file} dim3", shell=True, capture_output=True, text=True)
    dims = result.stdout.strip()
    print(f"Nombre de coupe: {dims}")

    result = subprocess.run(f"fslval {input_file} pixdim3", shell=True, capture_output=True, text=True)
    slice_thickness = int(float(result.stdout.strip()))
    print(type(slice_thickness))
    print(f"Taille de la coupe: {slice_thickness}")