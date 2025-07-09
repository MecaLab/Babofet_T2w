import torch
from nnunetv2.training.nnUNetTrainer.nnUNetTrainer import nnUNetTrainer
from nnunetv2.training.data_augmentation.default_data_augmentation import get_default_augmentation
import torchio as tio
from torchio.transforms import RandomBiasField


class nnUNetTrainerWithBiasField(nnUNetTrainer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.num_epochs = 100  # Forcer 100 époques

    def get_data_augmentation(self):
        # Get the default nnUNet transforms (they use batchgenerators)
        tr_transforms, val_transforms = get_default_augmentation(
            self.dataloaders_cfg,
            self.patch_size,
            self.rotation_for_DA,
            self.rotation_for_DA,
            self.do_dummy_2D_data_aug,
            self.use_nondet_train,
            self.use_nondet_val
        )

        # Wrap batchgenerators transforms in a callable
        def apply_batchgenerators_transforms(sample, transforms):
            # Convert from torch.Tensor to numpy before applying batchgenerators
            sample['data'] = sample['data'].numpy()
            sample['seg'] = sample['seg'].numpy()
            sample = transforms(**sample)
            # Convert back to torch.Tensor
            sample['data'] = torch.from_numpy(sample['data'])
            sample['seg'] = torch.from_numpy(sample['seg'])
            return sample

        # TorchIO transform: RandomBiasField
        bias_transform = RandomBiasField(coefficients=0.5, order=3, p=0.5)

        # Function to apply both transforms
        def combined_train_transform(sample):
            subject = tio.Subject(
                image=tio.ScalarImage(tensor=sample['data'][0]),
                mask=tio.LabelMap(tensor=sample['seg'][0])
            )
            subject = bias_transform(subject)
            # Reinsert into nnUNet sample format
            sample['data'][0] = subject['image'].data
            sample['seg'][0] = subject['mask'].data
            # Apply nnUNet default augmentation
            sample = apply_batchgenerators_transforms(sample, tr_transforms)
            return sample

        return combined_train_transform, val_transforms
