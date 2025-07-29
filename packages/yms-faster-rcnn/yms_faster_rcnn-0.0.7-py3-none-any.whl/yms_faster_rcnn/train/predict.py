import os
import time
import json

import torch
from PIL import Image
import matplotlib.pyplot as plt

from torchvision import transforms

from yms_faster_rcnn.backbone.resnet50_fpn_model import resnet152_fpn_backbone
from yms_faster_rcnn.network_files import FasterRCNN, FastRCNNPredictor, AnchorsGenerator
from yms_faster_rcnn.train.draw_box_utils import draw_objs


def create_model(num_classes, backbone_pre_path=None, pre_model_path=None):
    # import torchvision
    # from torchvision.models.feature_extraction import create_feature_extractor
    # backbone = torchvision.models.efficientnet_b0(weights=None)
    # if backbone_pre_path is not None:
    #     weight = torch.load(backbone_pre_path, weights_only=True)
    #     backbone.load_state_dict(weight)
    # # print(backbone)
    # return_layers = {"features.3": "0",  # stride 8
    #                  "features.4": "1",  # stride 16
    #                  "features.8": "2"}  # stride 32
    # # 提供给fpn的每个特征层channel
    # in_channels_list = [40, 80, 1280]
    # new_backbone = create_feature_extractor(backbone, return_layers)
    # backbone_with_fpn = BackboneWithFPN(new_backbone,
    #                                     return_layers=return_layers,
    #                                     in_channels_list=in_channels_list,
    #                                     out_channels=256,
    #                                     extra_blocks=LastLevelMaxPool(),
    #                                     re_getter=False)

    backbone = resnet152_fpn_backbone(pretrain_path=backbone_pre_path,
                                      norm_layer=torch.nn.BatchNorm2d,
                                      trainable_layers=3)

    anchor_sizes = ((27,), (54,), (122,), (230,), (461,))
    aspect_ratios = ((0.9841, 1.0, 1.0162), (0.9291, 1.0, 1.0763), (0.7899, 1.0, 1.2659),
                     (0.7239, 1.0, 1.3814), (0.8511, 1.0, 1.1750))
    rpn_anchor_generator = AnchorsGenerator(
        anchor_sizes, aspect_ratios
    )
    # 训练自己数据集时不要修改这里的91，修改的是传入的num_classes参数
    model = FasterRCNN(backbone=backbone, num_classes=21, rpn_anchor_generator=rpn_anchor_generator)
    # model = FasterRCNN(backbone=backbone_with_fpn, num_classes=4, rpn_anchor_generator=rpn_anchor_generator)
    if pre_model_path is not None:
        weights_dict = torch.load(pre_model_path,
                                  map_location='cpu', weights_only=True)
        weights_dict = weights_dict["model"] if "model" in weights_dict else weights_dict
        missing_keys, unexpected_keys = model.load_state_dict(weights_dict, strict=False)
        if len(missing_keys) != 0 or len(unexpected_keys) != 0:
            print("missing_keys: ", missing_keys)
            print("unexpected_keys: ", unexpected_keys)

    # get number of input features for the classifier
    in_features = model.roi_heads.box_predictor.cls_score.in_features
    # replace the pre-trained head with a new one
    model.roi_heads.box_predictor = FastRCNNPredictor(in_features, num_classes)

    return model


# def create_model(num_classes):
#     # mobileNetv2+faster_RCNN
#     # backbone = MobileNetV2().features
#     # backbone.out_channels = 1280
#     #
#     # anchor_generator = AnchorsGenerator(sizes=((32, 64, 128, 256, 512),),
#     #                                     aspect_ratios=((0.5, 1.0, 2.0),))
#     #
#     # roi_pooler = torchvision.ops.MultiScaleRoIAlign(featmap_names=['0'],
#     #                                                 output_size=[7, 7],
#     #                                                 sampling_ratio=2)
#     #
#     # model = FasterRCNN(backbone=backbone,
#     #                    num_classes=num_classes,
#     #                    rpn_anchor_generator=anchor_generator,
#     #                    box_roi_pool=roi_pooler)
#
#     # resNet50+fpn+faster_RCNN
#     # 注意，这里的norm_layer要和训练脚本中保持一致
#     backbone = resnet50_fpn_backbone(norm_layer=torch.nn.BatchNorm2d)
#     model = FasterRCNN(backbone=backbone, num_classes=num_classes, rpn_score_thresh=0.5)
#
#     return model


def time_synchronized():
    torch.cuda.synchronize() if torch.cuda.is_available() else None
    return time.time()


def main():
    # get devices
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    print("using {} device.".format(device))

    # create model
    model = create_model(num_classes=4)

    # load train weights
    weights_path = r"F:\IDM_Downloads\VOCdevkit\b0-best_model.pth"
    assert os.path.exists(weights_path), "{} file dose not exist.".format(weights_path)
    weights_dict = torch.load(weights_path, map_location='cpu')
    weights_dict = weights_dict["model"] if "model" in weights_dict else weights_dict
    model.load_state_dict(weights_dict)
    model.to(device)

    # read class_indict
    label_json_path = 'classes.json'
    assert os.path.exists(label_json_path), "json file {} dose not exist.".format(label_json_path)
    with open(label_json_path, 'r') as f:
        class_dict = json.load(f)

    category_index = {str(v): str(k) for k, v in class_dict.items()}

    # load image
    original_img = Image.open(
        r"F:\IDM_Downloads\VOCdevkit\VOC2012\JPEGImages\1__H2_817171_IO-NIO198M_210119A0184-1-1.jpg")

    # from pil image to tensor, do not normalize image
    data_transform = transforms.Compose([transforms.ToTensor()])
    img = data_transform(original_img)
    # expand batch dimension
    img = torch.unsqueeze(img, dim=0)

    model.eval()  # 进入验证模式
    with torch.no_grad():
        # init
        img_height, img_width = img.shape[-2:]
        init_img = torch.zeros((1, 3, img_height, img_width), device=device)
        model(init_img)

        t_start = time_synchronized()
        predictions = model(img.to(device))[0]
        t_end = time_synchronized()
        print("inference+NMS time: {}".format(t_end - t_start))

        predict_boxes = predictions["boxes"].to("cpu").numpy()
        predict_classes = predictions["labels"].to("cpu").numpy()
        predict_scores = predictions["scores"].to("cpu").numpy()

        if len(predict_boxes) == 0:
            print("没有检测到任何目标!")

        plot_img = draw_objs(original_img,
                             predict_boxes,
                             predict_classes,
                             predict_scores,
                             category_index=category_index,
                             box_thresh=0.5,
                             line_thickness=3,
                             font='arial.ttf',
                             font_size=20)
        plt.imshow(plot_img)
        plt.show()
        # 保存预测的图片结果
        plot_img.save("test_result.jpg")


if __name__ == '__main__':
    main()
