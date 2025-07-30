import random
from torchvision.transforms import functional as F


class Compose(object):
    """组合多个transform函数"""
    def __init__(self, transforms):
        self.transforms = transforms

    def __call__(self, image, target):
        for t in self.transforms:
            image, target = t(image, target)
        return image, target


class ToTensor(object):
    """将PIL图像转为Tensor"""
    def __call__(self, image, target):
        image = F.to_tensor(image)
        return image, target


class RandomHorizontalFlip(object):
    """随机水平翻转图像以及bboxes"""
    def __init__(self, prob=0.5):
        self.prob = prob

    def __call__(self, image, target):
        if random.random() < self.prob:
            height, width = image.shape[-2:]
            image = image.flip(-1)  # 水平翻转图片
            bbox = target["boxes"]
            # bbox: xmin, ymin, xmax, ymax
            bbox[:, [0, 2]] = width - bbox[:, [2, 0]]  # 翻转对应bbox坐标信息
            target["boxes"] = bbox
        return image, target


class Normalize(object):
    """对图像进行标准化处理

    Args:
        mean (sequence): 每个通道的均值
        std (sequence): 每个通道的标准差
        inplace(bool, optional): 是否原地操作. Defaults to False.
    """

    def __init__(self, mean, std, inplace=False):
        self.mean = mean
        self.std = std
        self.inplace = inplace

    def __call__(self, image, target):
        """
        Args:
            image (Tensor): 要标准化的图像张量
            target (dict): 包含目标信息的字典，不做修改

        Returns:
            Tensor: 标准化后的图像
            dict: 原始目标信息
        """
        # 只对图像进行标准化，目标信息不变
        image = F.normalize(image, self.mean, self.std, self.inplace)
        return image, target

