import os
import subprocess


if __name__ == "__main__":
    base_path = '/envau/work/meca/data/babofet_DB/2024_new_stuff/derivatives/'
    output_base_path = '/envau/work/meca/data/babofet_DB/2024_new_stuff/fetalBET_masks_V2/'

    sub = ['Filoutte']
    ses = ['07', '08', '09', '10']

    for folder in os.listdir(base_path):
        if any(s in folder for s in sub) and any(s in folder for s in ses):

            print(f"Processing folder: {folder}")

            for file in os.listdir(os.path.join(base_path, folder, 'denoising')):
                if file.endswith('.nii.gz'):

                    image_path = os.path.join(base_path, folder, 'denoising', file)
                    output_folder = os.path.join(output_base_path, folder)

                    os.makedirs(output_folder, exist_ok=True)

                    print(f"Processing {image_path}...")
                    subprocess.run([
                        'python', 'ensemble_inference.py',
                        '--image_path', image_path,
                        '--output_folder', output_folder
                    ])
