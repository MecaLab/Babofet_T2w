import os
import sys
import torch
import torchvision
import matplotlib.pyplot as plt
from torchvision.io import read_image
from torchvision.ops.boxes import masks_to_boxes
from torchvision.transforms import ToTensor
from torchvision.utils import draw_bounding_boxes, draw_segmentation_masks
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
from torchvision.models.detection.mask_rcnn import MaskRCNNPredictor
from torch.utils.tensorboard import SummaryWriter
from engine import train_one_epoch, evaluate
import utils


base_path = os.path.join("/scratch/lbaptiste", "Mask_RCNN", "MRI_dataset_png")
device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
print(device)


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
        mask = read_image(mask_path, mode=torchvision.io.ImageReadMode.RGB)

        img = img.float() / 255.0

        obj_ids = torch.unique(mask)
        obj_ids = obj_ids[1:]  # remove background id
        num_objects = len(obj_ids)

        masks = (mask == obj_ids[:, None, None]).to(dtype=torch.uint8)
        boxes = masks_to_boxes(masks)

        labels = torch.ones((num_objects, ), dtype=torch.int64)
        image_id = idx
        area = (boxes[:, 3] - boxes[:, 1]) * (boxes[:, 2] - boxes[:, 0])
        iscrowd = torch.zeros((num_objects, ), dtype=torch.int64)

        target = {
            "boxes": boxes,
            "masks": masks,
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


def get_model_instance_segmentation(num_classes):
    # load an instance segmentation model pre-trained on COCO
    model = torchvision.models.detection.maskrcnn_resnet50_fpn(pretrained=True)

    # get number of input features for the classifier
    in_features = model.roi_heads.box_predictor.cls_score.in_features
    # replace the pre-trained head with a new one
    model.roi_heads.box_predictor = FastRCNNPredictor(in_features, num_classes)

    # now get the number of input features for the mask classifier
    in_features_mask = model.roi_heads.mask_predictor.conv5_mask.in_channels
    hidden_layer = 32
    # and replace the mask predictor with a new one
    model.roi_heads.mask_predictor = MaskRCNNPredictor(
        in_features_mask,
        hidden_layer,
        num_classes
    )

    return model


def get_transform():
    return ToTensor()


custom_ds = BrainDataset(root=base_path, transforms=None)
num_classes = 2

data_loader = torch.utils.data.DataLoader(
    custom_ds,
    batch_size=8,
    shuffle=True,
    collate_fn=utils.collate_fn
)

model = get_model_instance_segmentation(num_classes)

# move model to the right device
model.to(device)

params = [p for p in model.parameters() if p.requires_grad]
optimizer = torch.optim.SGD(
    params,
    lr=0.005,
    momentum=0.9,
    weight_decay=0.0005
)

# and a learning rate scheduler
lr_scheduler = torch.optim.lr_scheduler.StepLR(
    optimizer,
    step_size=3,
    gamma=0.1
)

# let's train it just for 2 epochs
num_epochs = 2
writer = SummaryWriter(log_dir='runs/brain_seg')


# Fonction pour enregistrer les métriques dans TensorBoard
def log_metrics_to_tensorboard(metric_logger, writer, step):
    for name, meter in metric_logger.meters.items():
        value = meter.global_avg if hasattr(meter, 'global_avg') else meter.avg
        writer.add_scalar(name, value, step)


def train_model(num_epochs):
    # To follow tensorboard on local
    # ssh -N -f -p 8822 -L localhost:16006:localhost:6006 lbaptiste@login.mesocentre.univ-amu.fr

    for epoch in range(num_epochs):
        # train for one epoch, printing every 10 iterations
        metric_logger = train_one_epoch(model, optimizer, data_loader, device, epoch, print_freq=10)
        # update the learning rate
        lr_scheduler.step()
        # evaluate on the test dataset
        # evaluate(model, data_loader_test, device=device)
        log_metrics_to_tensorboard(metric_logger, writer, epoch)

        torch.save(model.state_dict(), f"brain_segmentation_model_epoch_{epoch}.pth")

    writer.close()


def inference_model(img_path):
    print("Start inference")
    image = read_image(img_path, mode=torchvision.io.ImageReadMode.RGB)

    model.eval()
    with torch.no_grad():
        image_float = image.float() / 255.0
        print(image_float.shape)
        predictions = model([image_float.to(device), ])
        pred = predictions[0]

    pred_labels = [f"pedestrian: {score:.3f}" for label, score in zip(pred["labels"], pred["scores"])]
    pred_boxes = pred["boxes"].long()
    image_uint8 = (image_float * 255).to(torch.uint8)
    print(image_uint8.shape)
    output_image = draw_bounding_boxes(image_uint8, pred_boxes, pred_labels, colors="red")

    masks = (pred["masks"] > 0.7).squeeze(1)
    output_image = draw_segmentation_masks(output_image, masks, alpha=0.5, colors="blue")

    plt.imshow(output_image.permute(1, 2, 0).numpy())
    plt.figure(figsize=(12, 12))
    plt.savefig("tmp.png")


if __name__ == "__main__":

    model.load_state_dict(torch.load("brain_segmentation_model_epoch_1.pth"))
    inference_model(os.path.join(base_path, "images", "Aziza_09_axial_022.png"))
