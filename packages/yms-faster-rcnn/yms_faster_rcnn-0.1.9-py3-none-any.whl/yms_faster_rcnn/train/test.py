# import torch
# from torchsummary import summary
#
# from backbone import BackboneWithFPN, LastLevelMaxPool
# from backbone.resnet50_fpn_model import resnet152_fpn_backbone, resnet50_fpn_backbone
# from network_files import AnchorsGenerator, FasterRCNN, FastRCNNPredictor
#
#
# # from train import create_model
#
# def create_model(num_classes, backbone_pre_path=None, pre_model_path=None):
#     import torchvision
#     from torchvision.models.feature_extraction import create_feature_extractor
#     # backbone = torchvision.models.efficientnet_b0(weights=None)
#     # backbone = torchvision.models.mobilenet_v3_large(weights=None)
#     # backbone = torchvision.models.efficientnet_v2_s(weights=None)
#     # backbone = torchvision.models.efficientnet_v2_l(weights=None)
#     # backbone = torchvision.models.efficientnet_v2_m(weights=None)
#     # backbone = torchvision.models.efficientnet_b2(weights=None)
#     # backbone = torchvision.models.efficientnet_b3(weights=None)
#     # backbone = torchvision.models.efficientnet_b4(weights=None)
#     # backbone = torchvision.models.efficientnet_b5(weights=None)
#     backbone = torchvision.models.googlenet(weights=None, init_weights=True)
#     if pre_model_path is not None:
#         weight = torch.load(backbone_pre_path, weights_only=True)
#         backbone.load_state_dict(weight)
#
#     # efficientnet_b0
#     # return_layers = {"features.3": "0",  # stride 8
#     #                  "features.4": "1",  # stride 16
#     #                  "features.8": "2"}  # stride 32
#     # in_channels_list = [40, 80, 1280]
#
#     # mobilenet_v3_large
#     # return_layers = {"features.6": "0",  # stride 8
#     #                  "features.12": "1",  # stride 16
#     #                  "features.16": "2"}  # stride 32
#     # in_channels_list = [40, 112, 960]
#
#     # efficientnet_v2_s
#     # return_layers = {"features.3": "0",  # stride 8
#     #                  "features.4": "1",  # stride 16
#     #                  "features.7": "2"}  # stride 32
#     # in_channels_list = [64, 128, 1280]
#
#     # efficientnet_v2_l
#     # return_layers = {"features.3": "0",  # stride 8
#     #                  "features.4": "1",  # stride 16
#     #                  "features.8": "2"}  # stride 32
#     # in_channels_list = [96, 192, 1280]
#
#     # efficientnet_v2_m
#     # return_layers = {"features.3": "0",  # stride 8
#     #                  "features.4": "1",  # stride 16
#     #                  "features.8": "2"}  # stride 32
#     # in_channels_list = [80, 160, 1280]
#
#     # efficientnet_b2
#     # return_layers = {"features.3": "0",  # stride 8
#     #                  "features.4": "1",  # stride 16
#     #                  "features.8": "2"}  # stride 32
#     # in_channels_list = [48, 88, 1408]
#
#     # efficientnet_b3
#     # return_layers = {"features.3": "0",  # stride 8
#     #                  "features.4": "1",  # stride 16
#     #                  "features.8": "2"}  # stride 32
#     # in_channels_list = [48, 96, 1536]
#
#     # efficientnet_b4
#     # return_layers = {"features.3": "0",  # stride 8
#     #                  "features.4": "1",  # stride 16
#     #                  "features.8": "2"}  # stride 32
#     # in_channels_list = [56, 112, 1792]
#
#     # efficientnet_b5
#     # return_layers = {"features.3": "0",  # stride 8
#     #                  "features.4": "1",  # stride 16
#     #                  "features.8": "2"}  # stride 32
#     # in_channels_list = [64, 128, 2048]
#
#     # googleNet
#     # return_layers = {
#     #     "maxpool1": "0",  # 下采样为4
#     #     "maxpool2": "1",  # 下采样为8
#     #     "maxpool3": "2",  # 下采样为16
#     #     "maxpool4": "3"  # 下采样为32
#     # }
#     # in_channels_list = [64, 192, 480, 832]
#
#     # googleNet
#     return_layers = {
#         "maxpool2": "1",  # 下采样为8
#         "maxpool3": "2",  # 下采样为16
#         "maxpool4": "3"  # 下采样为32
#     }
#     in_channels_list = [192, 480, 832]
#
#     new_backbone = create_feature_extractor(backbone, return_layers)
#     backbone_with_fpn = BackboneWithFPN(new_backbone,
#                                         return_layers=return_layers,
#                                         in_channels_list=in_channels_list,
#                                         out_channels=256,
#                                         extra_blocks=LastLevelMaxPool(),
#                                         re_getter=False)
#     roi_pooler = torchvision.ops.MultiScaleRoIAlign(featmap_names=['0', '1', '2'],  # 在哪些特征层上进行RoIAlign pooling
#                                                     output_size=[7, 7],  # RoIAlign pooling输出特征矩阵尺寸
#                                                     sampling_ratio=2)  # 采样率
#
#     # backbone = resnet50_fpn_backbone(
#     #                                   norm_layer=torch.nn.BatchNorm2d,
#     #                                   trainable_layers=3)
#
#     anchor_sizes = ((27,), (54,), (122,), (230,), (461,))
#     aspect_ratios = ((0.9841, 1.0, 1.0162), (0.9291, 1.0, 1.0763), (0.7899, 1.0, 1.2659),
#                      (0.7239, 1.0, 1.3814), (0.8511, 1.0, 1.1750))
#     rpn_anchor_generator = AnchorsGenerator(
#         anchor_sizes, aspect_ratios
#     )
#     # 训练自己数据集时不要修改这里的91，修改的是传入的num_classes参数
#     # model = FasterRCNN(backbone=backbone, num_classes=91, rpn_anchor_generator=rpn_anchor_generator)  #
#     model = FasterRCNN(backbone=backbone_with_fpn, num_classes=num_classes, rpn_anchor_generator=rpn_anchor_generator
#                        , box_roi_pool=roi_pooler
#                        )
#
#     if pre_model_path is not None:
#         weights_dict = torch.load(pre_model_path,
#                                   map_location='cpu', weights_only=True)
#         weights_dict = weights_dict["model"] if "model" in weights_dict else weights_dict
#         missing_keys, unexpected_keys = model.load_state_dict(weights_dict, strict=False)
#         if len(missing_keys) != 0 or len(unexpected_keys) != 0:
#             print("missing_keys: ", missing_keys)
#             print("unexpected_keys: ", unexpected_keys)
#
#     # get number of input features for the classifier
#     in_features = model.roi_heads.box_predictor.cls_score.in_features
#     # replace the pre-trained head with a new one
#     model.roi_heads.box_predictor = FastRCNNPredictor(in_features, num_classes)
#
#     return model
#
#
# model = create_model(4)
#
# device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# model.to(device)
# total_params = 0
# for name, param in model.named_parameters():
#     # print(name, param.numel())
#     total_params += param.numel()
# params_in_M = total_params / 1000000
# params_in_G = total_params / 1000000000
# print("Total number of parameters:", total_params)
# print("Total number of parameters:", f"{params_in_M}M")
# print("Total number of parameters:", f"{params_in_G}G")
import json

import torch

from yms_faster_rcnn.backbone import BackboneWithFPN, LastLevelMaxPool
from yms_faster_rcnn.network_files import FasterRCNN, FastRCNNPredictor, AnchorsGenerator


def read_image_id_mapping(json_path):
    """
    读取JSON文件，返回图片名称到image_id的映射字典
    """
    with open(json_path, 'r') as f:
        data = json.load(f)
    image_id_mapping = {}
    for image_info in data['images']:
        image_id_mapping[image_info['file_name']] = image_info['id']
    return image_id_mapping


# info = read_image_id_mapping(r'D:\Code\data\齿轮检测数据集\VOC\VOCdevkit\VOC2012\annotations.json')
# print(info)



def create_model(num_classes, backbone_pre_path=None, pre_model_path=None):
    import torchvision
    from torchvision.models.feature_extraction import create_feature_extractor
    backbone = torchvision.models.efficientnet_b0(weights=None)
    # backbone = torchvision.models.mobilenet_v3_large(weights=None)
    # backbone = torchvision.models.efficientnet_v2_s(weights=None)
    # backbone = torchvision.models.efficientnet_v2_l(weights=None)
    # backbone = torchvision.models.efficientnet_v2_m(weights=None)
    # backbone = torchvision.models.efficientnet_b2(weights=None)
    # backbone = torchvision.models.efficientnet_b3(weights=None)
    # backbone = torchvision.models.efficientnet_b4(weights=None)
    # backbone = torchvision.models.efficientnet_b5(weights=None)
    # backbone = torchvision.models.googlenet(weights=None, init_weights=True)
    if pre_model_path is not None:
        weight = torch.load(backbone_pre_path, weights_only=True)
        backbone.load_state_dict(weight)

    # efficientnet_b0
    return_layers = {"features.3": "0",  # stride 8
                     "features.4": "1",  # stride 16
                     "features.8": "2"}  # stride 32
    in_channels_list = [40, 80, 1280]

    # mobilenet_v3_large
    # return_layers = {"features.6": "0",  # stride 8
    #                  "features.12": "1",  # stride 16
    #                  "features.16": "2"}  # stride 32
    # in_channels_list = [40, 112, 960]

    # efficientnet_v2_s
    # return_layers = {"features.3": "0",  # stride 8
    #                  "features.4": "1",  # stride 16
    #                  "features.7": "2"}  # stride 32
    # in_channels_list = [64, 128, 1280]

    # efficientnet_v2_l
    # return_layers = {"features.3": "0",  # stride 8
    #                  "features.4": "1",  # stride 16
    #                  "features.8": "2"}  # stride 32
    # in_channels_list = [96, 192, 1280]

    # efficientnet_v2_m
    # return_layers = {"features.3": "0",  # stride 8
    #                  "features.4": "1",  # stride 16
    #                  "features.8": "2"}  # stride 32
    # in_channels_list = [80, 160, 1280]

    # efficientnet_b2
    # return_layers = {"features.3": "0",  # stride 8
    #                  "features.4": "1",  # stride 16
    #                  "features.8": "2"}  # stride 32
    # in_channels_list = [48, 88, 1408]

    # efficientnet_b3
    # return_layers = {"features.3": "0",  # stride 8
    #                  "features.4": "1",  # stride 16
    #                  "features.8": "2"}  # stride 32
    # in_channels_list = [48, 96, 1536]

    # efficientnet_b4
    # return_layers = {"features.3": "0",  # stride 8
    #                  "features.4": "1",  # stride 16
    #                  "features.8": "2"}  # stride 32
    # in_channels_list = [56, 112, 1792]

    # efficientnet_b5
    # return_layers = {"features.3": "0",  # stride 8
    #                  "features.4": "1",  # stride 16
    #                  "features.8": "2"}  # stride 32
    # in_channels_list = [64, 128, 2048]

    # googleNet
    # return_layers = {
    #     "maxpool1": "0",  # 下采样为4
    #     "maxpool2": "1",  # 下采样为8
    #     "maxpool3": "2",  # 下采样为16
    #     "maxpool4": "3"  # 下采样为32
    # }
    # in_channels_list = [64, 192, 480, 832]

    # googleNet
    # return_layers = {
    #     "maxpool2": "1",  # 下采样为8
    #     "maxpool3": "2",  # 下采样为16
    #     "maxpool4": "3"  # 下采样为32
    # }
    # in_channels_list = [192, 480, 832]

    new_backbone = create_feature_extractor(backbone, return_layers)
    backbone_with_fpn = BackboneWithFPN(new_backbone,
                                        return_layers=return_layers,
                                        in_channels_list=in_channels_list,
                                        out_channels=256,
                                        extra_blocks=LastLevelMaxPool(),
                                        re_getter=False)
    roi_pooler = torchvision.ops.MultiScaleRoIAlign(featmap_names=['0', '1', '2'],  # 在哪些特征层上进行RoIAlign pooling
                                                    output_size=[7, 7],  # RoIAlign pooling输出特征矩阵尺寸
                                                    sampling_ratio=2)  # 采样率

    # backbone = resnet50_fpn_backbone(pretrain_path=backbone_pre_path,
    #                                  norm_layer=torch.nn.BatchNorm2d,
    #                                  trainable_layers=3)
    # backbone = resnet50_fpn_backbone(norm_layer=torch.nn.BatchNorm2d,
    #                                  trainable_layers=3)

    anchor_sizes = ((27,), (54,), (122,), (230,), (461,))
    aspect_ratios = ((0.9841, 1.0, 1.0162), (0.9291, 1.0, 1.0763), (0.7899, 1.0, 1.2659),
                     (0.7239, 1.0, 1.3814), (0.8511, 1.0, 1.1750))
    rpn_anchor_generator = AnchorsGenerator(
        anchor_sizes, aspect_ratios
    )
    # 训练自己数据集时不要修改这里的91，修改的是传入的num_classes参数
    # model = FasterRCNN(backbone=backbone, num_classes=91, rpn_anchor_generator=rpn_anchor_generator)  #rpn_anchor_generator=rpn_anchor_generator
    model = FasterRCNN(backbone=backbone_with_fpn, num_classes=num_classes, rpn_anchor_generator=rpn_anchor_generator
    , box_roi_pool=roi_pooler, max_size=1000, min_size=1000
    )

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


