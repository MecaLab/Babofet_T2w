import torch
from typing import Tuple, Union, List
import numpy as np
from nnunetv2.training.nnUNetTrainer.nnUNetTrainer import nnUNetTrainer

from batchgeneratorsv2.transforms.utils.compose import ComposeTransforms
from batchgeneratorsv2.helpers.scalar_type import RandomScalar
from batchgeneratorsv2.transforms.utils.random import RandomTransform
from batchgeneratorsv2.transforms.base.basic_transform import BasicTransform

import torchio as tio
import gc


def aug_bias_field(img, seg):
    """
    Applique un bias field avec gestion d'erreurs robuste
    """
    try:
        # Vérification des inputs
        if img is None or seg is None:
            return img, seg

        # Conversion en tenseur si nécessaire
        if isinstance(img, list):
            img = torch.tensor(img)
        if isinstance(seg, list):
            seg = torch.tensor(seg)

        # Vérification que ce sont bien des tenseurs
        if not isinstance(img, torch.Tensor) or not isinstance(seg, torch.Tensor):
            return img, seg

        # Conversion de type
        img = img.float()
        seg = seg.long()

        # Vérification des dimensions
        if img.ndim < 3 or seg.ndim < 3:
            return img, seg

        # TorchIO attend (C, D, H, W) - ajustement si nécessaire
        if img.ndim == 4 and img.shape[0] not in [1, 3]:
            img = img.permute(3, 0, 1, 2)
        if seg.ndim == 4 and seg.shape[0] not in [1]:
            seg = seg.permute(3, 0, 1, 2)

        # Application du bias field avec gestion d'erreur
        subject = tio.Subject(
            image=tio.ScalarImage(tensor=img),
            seg=tio.LabelMap(tensor=seg)
        )

        transform = tio.RandomBiasField(coefficients=0.5, order=3)
        subject = transform(subject)

        img_out, seg_out = subject.image.data, subject.seg.data

        # Nettoyage mémoire
        del subject, transform
        gc.collect()

        return img_out, seg_out

    except Exception as e:
        print(f"Erreur dans aug_bias_field: {e}")
        # Retourner les données originales en cas d'erreur
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


class nnUNetTrainerBiasField1000epochs(nnUNetTrainer):
    """
    Custom trainer for nnUNet that applies a bias field artifact during training.
    """

    def __init__(self,
                 plans: dict,
                 configuration: str,
                 fold: int,
                 dataset_json: dict,
                 device: torch.device = torch.device('cuda')):
        super().__init__(plans, configuration, fold, dataset_json, device)
        self.num_epochs = 1000

    def get_training_transforms(
            self,
            patch_size: Union[np.ndarray, Tuple[int]],
            rotation_for_DA: RandomScalar,
            deep_supervision_scales: Union[List, Tuple, None],
            mirror_axes: Tuple[int, ...],
            do_dummy_2d_data_aug: bool,
            use_mask_for_norm: List[bool] = None,
            is_cascaded: bool = False,
            foreground_labels: Union[Tuple[int, ...], List[int]] = None,
            regions: List[Union[List[int], Tuple[int, ...], int]] = None,
            ignore_label: int = None,
    ) -> BasicTransform:
        try:
            base_transforms = super().get_training_transforms(
                patch_size, rotation_for_DA, deep_supervision_scales, mirror_axes,
                do_dummy_2d_data_aug, use_mask_for_norm, is_cascaded,
                foreground_labels, regions, ignore_label
            )

            # Récupérer la liste des transforms déjà présentes
            if hasattr(base_transforms, "transforms"):
                transform_list = list(base_transforms.transforms)
            else:
                transform_list = [base_transforms]

            # Ajouter ta transformation custom à la liste avec une probabilité plus faible
            transform_list.append(
                RandomTransform(
                    ArtifactTransform(bias_field=True),
                    apply_probability=0.5
                )
            )

            # Recréer une nouvelle composition
            return ComposeTransforms(transform_list)

        except Exception as e:
            print(f"Erreur dans get_training_transforms: {e}")
            # Retourner les transforms de base en cas d'erreur
            return super().get_training_transforms(
                patch_size, rotation_for_DA, deep_supervision_scales, mirror_axes,
                do_dummy_2d_data_aug, use_mask_for_norm, is_cascaded,
                foreground_labels, regions, ignore_label
            )