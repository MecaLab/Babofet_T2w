import subprocess
import tempfile
import sys

if __name__ == "__main__":

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    kernel_size = sys.argv[3]

    output_file = output_file.replace(".nii.gz", f"_{kernel_size}.nii.gz")

    result = subprocess.run(f"fslval {input_file} dim3", shell=True, capture_output=True, text=True)
    dims = int(result.stdout.strip())
    print(f"Nombre de coupes: {dims}")

    result = subprocess.run(f"fslval {input_file} pixdim3", shell=True, capture_output=True, text=True)
    slice_thickness = int(float(result.stdout.strip()))
    print(f"Taille d'une coupe: {slice_thickness}")

    with tempfile.NamedTemporaryFile(suffix=".nii.gz") as tmp_file:
        result = subprocess.run(f"fslmaths {input_file} -kernel sphere {kernel_size} -dilD {tmp_file.name}", shell=True, capture_output=True, text=True)
        result = subprocess.run(f"fslmaths {tmp_file.name} -kernel sphere {kernel_size} -ero {output_file}", shell=True, capture_output=True, text=True)

    print("Fermeture OK")

    """i = 0
    while i < dims:
        subprocess.run(f"fslroi {output_file} slice_{i}.nii.gz 0 -1 0 -1 {i} 1", shell=True)

        subprocess.run(
            f"fslmaths slice_{i}.nii.gz -dilM slice_dilated_{i}.nii.gz",
            shell=True
        )

        if i < 10:
            subprocess.run(f"mv slice_dilated_{i}.nii.gz slice_dilated_0{i}.nii.gz", shell=True)

        i += 1

    subprocess.run(f"fslmerge -z {output_file} slice_dilated_*.nii.gz", shell=True)
    subprocess.run("rm slice_*.nii.gz", shell=True)"""
    print(f"File written to {output_file}")
