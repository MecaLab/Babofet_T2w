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
    # Sécurité : convertit les listes en tensors
    if isinstance(img, list):
        img = torch.tensor(img)
    if isinstance(seg, list):
        seg = torch.tensor(seg)

    # TorchIO attend (C, D, H, W)
    if img.ndim == 4 and img.shape[0] not in [1, 3]:
        img = img.permute(3, 0, 1, 2)
    if seg.ndim == 4 and seg.shape[0] not in [1]:
        seg = seg.permute(3, 0, 1, 2)

    img = img.float()
    seg = seg.long()

    subject = tio.RandomBiasField()(tio.Subject(
        image=tio.ScalarImage(tensor=img),
        seg=tio.LabelMap(tensor=seg)
    ))

    img_out, seg_out = subject.image.data, subject.seg.data
    del subject
    gc.collect()
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
        print("💡 Entrée de ArtifactTransform.apply")
        print("Type image:", type(data_dict.get('image')))
        print("Type seg:", type(data_dict.get('segmentation')))
        print("Shape image:", getattr(data_dict.get('image'), 'shape', 'N/A'))
        print("Shape seg:", getattr(data_dict.get('segmentation'), 'shape', 'N/A'))
        print("----------", flush=True)

        if data_dict.get('image') is not None and data_dict.get('segmentation') is not None:
            data_dict['image'], data_dict['segmentation'] = self._apply_to_image(
                data_dict['image'], data_dict['segmentation'], **params
            )
        return data_dict

    def _apply_to_image(self, image, segmentation, **params):
        if params["bias_field"]:
            # Apply bias field artifact
            image, segmentation = aug_bias_field(image, segmentation)

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

    def setup_data_loader_train(self):
        self.dataloader_train_kwargs['num_workers'] = 0
        super().setup_data_loader_train()

    def setup_data_loader_val(self):
        self.dataloader_val_kwargs['num_workers'] = 0
        super().setup_data_loader_val()

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