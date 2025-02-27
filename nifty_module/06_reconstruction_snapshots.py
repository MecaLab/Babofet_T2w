import os
import sys
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg
from tools import qc_recons
import matplotlib.pyplot as plt
import nibabel as nib
import SimpleITK as sitk  # installed on mesocentre


def plot_slice(image, slice_index, title):
    plt.imshow(image[:, :, slice_index].T, cmap='gray', origin='lower')
    plt.title(title)
    plt.axis('off')
    plt.savefig(f"{title}.png")


if __name__ == "__main__":
    base_path = os.path.join(cfg.DATA_PATH, "Fabienne")

    img1 = nib.load(os.path.join(base_path, "ses09", f"manual_brainmask", f"sub-Fabienne_ses-09_haste_3DHR_manual_bm_T-1_pipeline.nii.gz"))
    img2 = nib.load(os.path.join(base_path, "ses09", f"nifty_brainmask", f"sub-Fabienne_ses-09_haste_3DHR_nifty_bm_T-1_pipeline.nii.gz"))
    img3 = nib.load(os.path.join(base_path, "ses09", f"mattia_brainmask", f"sub-Fabienne_ses-09_haste_3DHR_mattia_bm_T-1_pipeline.nii.gz"))

    sitk_img1 = sitk.GetImageFromArray(img1.get_fdata())
    sitk_img1.SetOrigin(img1.affine[:3, 3])
    sitk_img1.SetDirection(img1.affine[:3, :3].ravel())
    sitk_img1.SetSpacing(img1.header.get_zooms()[:3])

    sitk_img2 = sitk.GetImageFromArray(img2.get_fdata())
    sitk_img2.SetOrigin(img2.affine[:3, 3])
    sitk_img2.SetDirection(img2.affine[:3, :3].ravel())
    sitk_img2.SetSpacing(img2.header.get_zooms()[:3])

    sitk_img3 = sitk.GetImageFromArray(img3.get_fdata())
    sitk_img3.SetOrigin(img3.affine[:3, 3])
    sitk_img3.SetDirection(img3.affine[:3, :3].ravel())
    sitk_img3.SetSpacing(img3.header.get_zooms()[:3])

    reference_image = sitk_img1

    transform = sitk.CenteredTransformInitializer(reference_image,
                                                  sitk_img2,
                                                  sitk.Euler3DTransform(),
                                                  sitk.CenteredTransformInitializerFilter.GEOMETRY)

    resampler = sitk.ResampleImageFilter()
    resampler.SetReferenceImage(reference_image)
    resampler.SetInterpolator(sitk.sitkLinear)
    resampler.SetTransform(transform)

    resampled_img2 = resampler.Execute(sitk_img2)

    transform = sitk.CenteredTransformInitializer(reference_image,
                                                  sitk_img3,
                                                  sitk.Euler3DTransform(),
                                                  sitk.CenteredTransformInitializerFilter.GEOMETRY)

    resampled_img3 = resampler.Execute(sitk_img3)

    # Convertir les images SimpleITK en tableaux NumPy
    resampled_img2_array = sitk.GetArrayFromImage(resampled_img2)
    resampled_img3_array = sitk.GetArrayFromImage(resampled_img3)

    slice_index = 50  # Choisissez une tranche appropriée
    plot_slice(img1.get_fdata(), slice_index, 'Volume 1 manual')
    plot_slice(resampled_img2_array, slice_index, 'Volume 2 Recalé nifty')
    plot_slice(resampled_img3_array, slice_index, 'Volume 3 Recalé mattia')

    """subject = "Fabienne"
    base_path = os.path.join(cfg.DATA_PATH, subject)
    modes = ["manual", "nifty", "mattia"]

    datas = {}
    # plot the matplotlib table format for the qc:
    # 1 row per slice in the anat img, 1 col per method (manual, nifty, etc)
    # 1 file per session
    name = "default-param"
    for session in os.listdir(base_path):
        datas[session] = {}
        for mode in modes:
            datas[session][mode] = {}
            datas[session][mode]["anat"] = os.path.join(base_path, session, f"{mode}_brainmask", f"sub-{subject}_ses-{session[3:]}_haste_3DHR_{mode}_bm_pipeline.nii.gz")

    qc_recons.qc_plot_table_recons(datas, name)"""


    """# 1 snapshot per reconstruction
    modes = ["manual"]
    base_path = os.path.join(cfg.DATA_PATH, subject)

    for mode in modes:
        qc_recons.qc_recons_bis(base_path, subject, mode)"""

    """
    base_path = cfg.MESO_OUTPUT_PATH
    model = "niftymic"  # niftymic or nesvor
    mode = "manual"  # manual bm or nifty bm
    debug = False

    qc_recons.qc_recons(
        base_path,
        model,
        mode,
    )
    """