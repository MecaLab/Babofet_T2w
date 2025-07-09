import torchio as tio
import gc
from batchgeneratorsv2.transforms.base.basic_transform import ImageOnlyTransform, BasicTransform


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