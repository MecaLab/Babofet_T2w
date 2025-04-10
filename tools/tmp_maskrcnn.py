import os
import sys
import torch
import torchvision
from torchvision.io import read_image
from torchvision.ops.boxes import masks_to_boxes
from torchvision.transforms import v2
from torchvision.transforms.v2 import functional as F
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg

base_path = os.path.join(cfg.BASE_PATH, "Mask_RCNN", "MRI_dataset_png")


class BrainDataset(torch.utils.data.Dataset):
    def __init__(self, root, transforms):
        self.root = root
        self.transforms = transforms
        self.imgs = list(sorted(os.listdir(os.path.join(root, "images"))))
        self.masks = list(sorted(os.listdir(os.path.join(root, "masks"))))

    def __getitem__(self, idx):
        img_path = os.path.join(self.root, "images", self.imgs[idx])
        mask_path = os.path.join(self.root, "masks", self.masks[idx])

        img = read_image(img_path, mode=torchvision.io.ImageReadMode.RGB)
        mask = read_image(mask_path, mode=torchvision.io.ImageReadMode.UINT8)

        obj_ids = torch.unique(mask)
        obj_ids = obj_ids[1:]  # remove background id
        num_objects = len(obj_ids)

        masks = (mask == obj_ids[:, None, None]).to(dtype=torch.uint8)
        boxes = masks_to_boxes(masks)

        labels = torch.ones((num_objects, ), dtype=torch.int64)
        image_id = idx
        area = (boxes[:, 3] - boxes[:, 1]) * (boxes[:, 2] - boxes[:, 0])
        iscrowd = torch.zeros((num_objects, ), dtype=torch.int64)

        img = v2.tv_tensors.Image(img)

        target = {
            "boxes": tv_tensors.BoundingBoxes(boxes, format="XYXY", canvas_size=F.get_size(img)),
            "masks": tv_tensors.Mask(masks),
            "labels": labels,
            "image_id": image_id,
            "area": area,
            "iscrowd": iscrowd
        }

        if self.transforms:
            img, target = self.transforms(img, target)

        return img, target

    def __len__(self):
        return len(self.imgs)


custom_ds = BrainDataset(root=base_path, transforms=None)
print(custom_ds[0])