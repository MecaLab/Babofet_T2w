import torch
from typing import Tuple, Union, List
import numpy as np
from nnunetv2.training.nnUNetTrainer.nnUNetTrainer import nnUNetTrainer

from batchgeneratorsv2.transforms.compose import ComposeTransforms
from batchgeneratorsv2.helpers.scalar_type import RandomScalar
from batchgeneratorsv2.transforms.utils.random import RandomTransform
from batchgeneratorsv2.transforms.base.basic_transform import BasicTransform

import torchio as tio
import gc


def aug_bias_field(img, seg):
    subject = tio.RandomBiasField()(tio.Subject(
        image=tio.ScalarImage(tensor=img),
        seg=tio.LabelMap(tensor=seg)
    ))
    img_out, seg_out = subject.image.data, subject.seg.data
    del subject
    gc.collect()  # Force garbage collection
    return img_out, seg_out


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
        if data_dict.get('image') is not None and data_dict.get('segmentation') is not None:
            data_dict['image'], data_dict['segmentation'] = self._apply_to_image(data_dict['image'],
                                                                                 data_dict['segmentation'],
                                                                                 **params)
        return data_dict

    def _apply_to_image(self, image, segmentation, **params):
        if params["bias_field"]:
            # Apply bias field artifact
            image = self._apply_bias_field(image)
            segmentation = self._apply_bias_field(segmentation)

        return image, segmentation


class nnUNetTrainerBiasField100epochs(nnUNetTrainer):
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
        self.num_epochs = 100

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
        base_transforms = super().get_training_transforms(
            patch_size, rotation_for_DA, deep_supervision_scales, mirror_axes,
            do_dummy_2d_data_aug, use_mask_for_norm, is_cascaded,
            foreground_labels, regions, ignore_label
        )

        # Récupérer la liste des transforms déjà présentes
        transform_list = base_transforms.transforms if hasattr(base_transforms, "transforms") else []

        # Ajouter ta transformation custom à la liste
        transform_list.append(
            RandomTransform(
                ArtifactTransform(bias_field=True),
                apply_probability=0.3
            )
        )

        # Recréer une nouvelle composition
        return ComposeTransforms(transform_list)