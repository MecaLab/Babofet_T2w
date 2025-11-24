import os
import sys
import numpy as np
import torch
from batchgeneratorsv2.transforms.base.basic_transform import BasicTransform
import torchio as tio
import gc

sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg


def aug_bias_field(img, seg):
    try:
        if img is None or seg is None:
            return img, seg

        # Convertir en tenseurs Torch
        if isinstance(img, np.ndarray):
            img = torch.from_numpy(img)
        if isinstance(seg, np.ndarray):
            seg = torch.from_numpy(seg)

        img = img.float()
        seg = seg.long()

        # TorchIO exige 4 dimensions : (C, D, H, W)
        # Si 3D → ajouter une dimension de canal
        if img.ndim == 3:
            img = img.unsqueeze(0)   # (1, D, H, W)
        if seg.ndim == 3:
            seg = seg.unsqueeze(0)   # (1, D, H, W)

        # Vérifier maintenant
        if img.ndim != 4:
            raise ValueError(f"Image shape invalid: {img.shape}")
        if seg.ndim != 4:
            raise ValueError(f"Seg shape invalid: {seg.shape}")

        # SUBJECT TorchIO
        subject = tio.Subject(
            image=tio.ScalarImage(tensor=img),
            seg=tio.LabelMap(tensor=seg)
        )

        transform = tio.RandomBiasField(coefficients=0.5, order=3)
        subject = transform(subject)

        img_out, seg_out = subject.image.data, subject.seg.data

        return img_out, seg_out

    except Exception as e:
        print(f"Erreur dans aug_bias_field: {e}")
        return img, seg


class ArtifactTransform(BasicTransform):
    def __init__(self, bias_field=False):
        """
        Initialize the ArtifactTransform.

        :param bias_field: If True, applies a bias field artifact transform.
        """
        super().__init__()
        self.bias_field = bias_field

    def get_parameters(self, **kwargs):
        """
        Get parameters for the artifact transform.

        :param kwargs: Additional parameters.
        :return: Dictionary of parameters.
        """
        return {"bias_field": self.bias_field}

    def apply(self, data_dict, **params):
        try:
            # Vérification des clés requises
            if 'image' not in data_dict or 'segmentation' not in data_dict:
                return data_dict

            if data_dict['image'] is not None and data_dict['segmentation'] is not None:
                data_dict['image'], data_dict['segmentation'] = self._apply_to_image(
                    data_dict['image'], data_dict['segmentation'], **params
                )
            return data_dict

        except Exception as e:
            print(f"Erreur dans ArtifactTransform.apply: {e}")
            # Retourner les données originales en cas d'erreur
            return data_dict

    def _apply_to_image(self, image, segmentation, **params):
        try:
            if params.get("bias_field", False):
                # Apply bias field artifact
                image, segmentation = aug_bias_field(image, segmentation)
            return image, segmentation

        except Exception as e:
            print(f"Erreur dans _apply_to_image: {e}")
            return image, segmentation


if __name__ == "__main__":
    image = os.path.join(cfg.BASE_PATH, "3D_Borgne_ses08.nii.gz")
    seg = os.path.join(cfg.BASE_PATH, "seg_Borgne_ses08.nii.gz")

    import nibabel as nib

    img_nii = nib.load(image)
    seg_nii = nib.load(seg)
    affine_img = img_nii.affine
    affine_seg = seg_nii.affine

    img_out, seg_out = aug_bias_field(img_nii.get_fdata(), seg_nii.get_fdata())

    img_np = img_out.cpu().numpy()
    seg_np = seg_out.cpu().numpy()

    # Retrait du canal si nécessaire (C=1)
    if img_np.ndim == 4 and img_np.shape[0] == 1:
        img_np = img_np[0]

    if seg_np.ndim == 4 and seg_np.shape[0] == 1:
        seg_np = seg_np[0]

    # Normalisation des types de données
    img_np = img_np.astype(np.float32)  # image anatomique
    seg_np = seg_np.astype(np.uint8)  # segmentation (labels entiers)

    # Sauvegarde NIfTI
    nib.save(nib.Nifti1Image(img_np, affine_img), "img_out.nii.gz")
    nib.save(nib.Nifti1Image(seg_np, affine_seg), "seg_out.nii.gz")