import os
import sys
import torch
from typing import Tuple, Union, List
import numpy as np
from nnunetv2.training.nnUNetTrainer.nnUNetTrainer import nnUNetTrainer

from batchgeneratorsv2.transforms.utils.compose import ComposeTransforms
from batchgeneratorsv2.helpers.scalar_type import RandomScalar
from batchgeneratorsv2.transforms.utils.random import RandomTransform
from batchgeneratorsv2.transforms.base.basic_transform import BasicTransform

sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg
from segmentation_module.ArtifactTransform import ArtifactTransform


class nnUNetTrainerBias(nnUNetTrainer):
    def __init__(self,
                 plans: dict,
                 configuration: str,
                 fold: int,
                 dataset_json: dict,
                 device: torch.device = torch.device('cuda')):
        super().__init__(plans, configuration, fold, dataset_json, device)

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


class nnUNetTrainerBias_100epochs(nnUNetTrainerBias):
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


class nnUNetTrainerBias_200epochs(nnUNetTrainerBias):
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
        self.num_epochs = 200


class nnUNetTrainerBias_500epochs(nnUNetTrainerBias):
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
        self.num_epochs = 500


class nnUNetTrainerBias_1000epochs(nnUNetTrainerBias):
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


class nnUNetTrainerBias_2000epochs(nnUNetTrainerBias):
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
        self.num_epochs = 2000


class nnUNetTrainerBias_3000epochs(nnUNetTrainerBias):
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
        self.num_epochs = 4000


class nnUNetTrainerBias_4000epochs(nnUNetTrainerBias):
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
        self.num_epochs = 4000


if __name__ == "__main__":
    print("Copying file to appropriate directory")

    current_file_path = os.path.join(cfg.CODE_PATH, "segmentation_module/nnunet_module/"
                                                    "nnUNetTrainerBiasField_Xepochs.py")
    os.system(f"cp {current_file_path} {cfg.NNUNET_PYTHON_PATH}")
