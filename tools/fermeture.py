import subprocess
import tempfile
import sys


def fermeture_3D(input_file, output_file, kernel_size=None, kernel_object="sphere"):

    result = subprocess.run(f"fslval {input_file} dim3", shell=True, capture_output=True, text=True)
    dims = int(result.stdout.strip())
    print(f"Nombre de coupes: {dims}")

    if kernel_size is None:
        result = subprocess.run(f"fslval {input_file} pixdim3", shell=True, capture_output=True, text=True)
        kernel_size = int(float(result.stdout.strip()))
        print(f"Taille d'une coupe: {kernel_size}")

    with tempfile.NamedTemporaryFile(suffix=".nii.gz") as tmp_file:
        result = subprocess.run(f"fslmaths {input_file} -bin -kernel {kernel_object} {kernel_size} -dilD {tmp_file.name}", shell=True,
                                capture_output=True, text=True)
        result = subprocess.run(f"fslmaths {tmp_file.name} -bin -kernel {kernel_object} {kernel_size} -ero {output_file}", shell=True,
                                capture_output=True, text=True)

    print("Fermeture 3D OK")


def dilation_2D(input_file, output_file, kernel_size=None, kernel_object="sphere"):
    result = subprocess.run(f"fslval {input_file} dim3", shell=True, capture_output=True, text=True)
    dims = int(result.stdout.strip())
    print(f"Nombre de coupes: {dims}")

    for i in range(dims):
        subprocess.run(f"fslroi {input_file} slice_{i}.nii.gz 0 -1 0 -1 {i} 1", shell=True)

        subprocess.run(
            f"fslmaths slice_{i}.nii.gz -bin -kernel {kernel_object} {kernel_size} -dilD slice_dilated_{i}.nii.gz",
            shell=True
        )

        # Pour être sûr que les fichiers soient dans le bon ordre lors du merge
        if i < 10:
            subprocess.run(f"mv slice_dilated_{i}.nii.gz slice_dilated_0{i}.nii.gz", shell=True)

    subprocess.run(f"fslmerge -z {output_file} slice_dilated_*.nii.gz", shell=True)
    subprocess.run("rm slice_*.nii.gz", shell=True)

    print("Dilation 2D OK")


if __name__ == "__main__":

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    kernel_size = sys.argv[3]
    kernel_object = sys.argv[4]

    output_file = output_file.replace(".nii.gz", f"_{kernel_object}_{kernel_size}.nii.gz")

    # dilation_2D(input_file, output_file, kernel_size, kernel_object)
    fermeture_3D(input_file, output_file, kernel_size, kernel_object)
    print(f"File saved as {output_file}")
