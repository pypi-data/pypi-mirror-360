import os
import time
from datetime import timedelta

import torch
import wandb
from torch.optim.lr_scheduler import ReduceLROnPlateau
from torch.utils.data import DataLoader

from yms_faster_rcnn.backbone import BackboneWithFPN, LastLevelMaxPool
from yms_faster_rcnn.train_utils.my_dataset import VOCDataSet
from yms_faster_rcnn.network_files import FasterRCNN, FastRCNNPredictor, AnchorsGenerator
from yms_faster_rcnn.train_utils import GroupedBatchSampler, create_aspect_ratio_groups, transforms
from yms_faster_rcnn.train_utils import plot_curve
from yms_faster_rcnn.train_utils import train_eval_utils as utils


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
    , box_roi_pool=roi_pooler
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


def main(args):

    save_path = args.output_dir
    device = torch.device(args.device if torch.cuda.is_available() else "cpu")
    print("Using {} device training.".format(device.type))

    # 用来保存coco_info的文件
    results_file = os.path.join(save_path, 'results.txt')

    data_transform = {
        "train": transforms.Compose([transforms.ToTensor(),
                                     transforms.RandomHorizontalFlip(0.5)]),
        "val": transforms.Compose([transforms.ToTensor()])
    }

    VOC_root = args.data_path
    # check voc root
    if os.path.exists(os.path.join(VOC_root, "VOCdevkit")) is False:
        raise FileNotFoundError("VOCdevkit dose not in path:'{}'.".format(VOC_root))

    # load train data set
    # VOCdevkit -> VOC2012 -> ImageSets -> Main -> train.txt
    train_dataset = VOCDataSet(VOC_root, '2012', data_transform["train"], "train.txt", json_file=args.json_path)
    train_sampler = None

    # 是否按图片相似高宽比采样图片组成batch
    # 使用的话能够减小训练时所需GPU显存，默认使用
    if args.aspect_ratio_group_factor >= 0:
        train_sampler = torch.utils.data.RandomSampler(train_dataset)
        # 统计所有图像高宽比例在bins区间中的位置索引
        group_ids = create_aspect_ratio_groups(train_dataset, k=args.aspect_ratio_group_factor)
        # 每个batch图片从同一高宽比例区间中取
        train_batch_sampler = GroupedBatchSampler(train_sampler, group_ids, args.batch_size)

    # 注意这里的collate_fn是自定义的，因为读取的数据包括image和targets，不能直接使用默认的方法合成batch
    batch_size = args.batch_size

    nw = min([os.cpu_count(), batch_size if batch_size > 1 else 0, 16])  # number of workers
    print('Using %g dataloader workers' % nw)
    if train_sampler:
        # 如果按照图片高宽比采样图片，dataloader中需要使用batch_sampler
        train_data_loader = DataLoader(train_dataset,
                                       batch_sampler=train_batch_sampler,
                                       pin_memory=True,
                                       num_workers=nw,
                                       collate_fn=train_dataset.collate_fn)
    else:
        train_data_loader = DataLoader(train_dataset,
                                       batch_size=batch_size,
                                       shuffle=True,
                                       pin_memory=True,
                                       num_workers=nw,
                                       collate_fn=train_dataset.collate_fn)

    # load validation data set
    # VOCdevkit -> VOC2012 -> ImageSets -> Main -> val.txt
    val_dataset = VOCDataSet(VOC_root, '2012', data_transform["val"], "val.txt", json_file=args.json_path)
    val_data_set_loader = DataLoader(val_dataset,
                                     batch_size=1,
                                     shuffle=False,
                                     pin_memory=True,
                                     num_workers=nw,
                                     collate_fn=val_dataset.collate_fn)

    # create model num_classes equal background + 20 classes
    model = create_model(num_classes=args.num_classes + 1,
                         backbone_pre_path=args.backbone_path,
                         pre_model_path=args.coco_path)
    # print(model)
    model.to(device)
    # define optimizer
    params = [p for p in model.parameters() if p.requires_grad]
    optimizer = torch.optim.SGD(params,
                                lr=args.lr,
                                momentum=args.momentum,
                                weight_decay=args.weight_decay)

    scaler = torch.cuda.amp.GradScaler() if args.amp else None

    # learning rate scheduler
    # lr_scheduler = torch.optim.lr_scheduler.StepLR(optimizer,
    #                                                step_size=5,
    #                                                gamma=0.5)

    lr_scheduler = ReduceLROnPlateau(optimizer, mode='max', factor=0.5, patience=3, min_lr=1e-6)
    # lr_scheduler = OneCycleLR(optimizer, max_lr=0.01, steps_per_epoch=len(train_data_loader), epochs=args.epochs)

    # 如果指定了上次训练保存的权重文件地址，则接着上次结果接着训练
    if args.resume != "":
        checkpoint = torch.load(args.resume, map_location='cpu')
        model.load_state_dict(checkpoint['model'])
        optimizer.load_state_dict(checkpoint['optimizer'])
        lr_scheduler.load_state_dict(checkpoint['lr_scheduler'])
        args.start_epoch = checkpoint['epoch'] + 1
        if args.amp and "scaler" in checkpoint:
            scaler.load_state_dict(checkpoint["scaler"])
        print("the training process from epoch{}...".format(args.start_epoch))

    train_loss = []
    learning_rate = []
    val_map = []
    map0595 = []
    recall = []
    max_map = -1
    best_model = None
    last_model = None
    print("Start training")
    start_time = time.time()
    for epoch in range(args.start_epoch, args.epochs):
        # train for one epoch, printing every 10 iterations
        mean_loss, lr = utils.train_one_epoch(model, optimizer, train_data_loader,
                                              device=device, epoch=epoch,
                                              print_freq=50, warmup=True,
                                              scaler=scaler)
        train_loss.append(mean_loss.item())
        learning_rate.append(lr)

        # update the learning rate
        # lr_scheduler.step()
        # evaluate on the test dataset
        coco_info = utils.evaluate(model, val_data_set_loader, device=device)

        # write into txt
        with open(results_file, "a") as f:
            # 写入的数据包括coco指标还有loss和learning rate
            result_info = [f"{i:.4f}" for i in coco_info + [mean_loss.item()]] + [f"{lr:.6f}"]
            txt = "epoch:{} {}".format(epoch, '  '.join(result_info))
            f.write(txt + "\n")

        val_map.append(coco_info[1])  # pascal mAP
        recall.append(coco_info[12])
        map0595.append(coco_info[0])
        lr_scheduler.step(coco_info[1])

        # save weights
        save_files = {
            'model': model.state_dict(),
            'optimizer': optimizer.state_dict(),
            'lr_scheduler': lr_scheduler.state_dict(),
            'epoch': epoch}
        if args.amp:
            save_files["scaler"] = scaler.state_dict()
        model_path = os.path.join(save_path, "model-{}.pth".format(epoch))
        torch.save(save_files, model_path)
        if last_model is not None:
            os.remove(last_model)
        last_model = model_path
        if coco_info[1] > max_map:
            max_map = coco_info[1]
            if best_model is not None:
                os.remove(best_model)
            best_model = os.path.join(save_path, "best-model-{}.pth".format(epoch))
            torch.save(save_files, best_model)
    total_time = time.time() - start_time
    total_time_str = str(timedelta(seconds=int(total_time)))
    print('Training time {}'.format(total_time_str))
    print('the best model is:{}, the last model is:{}'.format(best_model, last_model))
    os.rename(last_model, os.path.join(save_path, "last_model.pth"))
    os.rename(best_model, os.path.join(save_path, "best_model.pth"))
    # plot loss and lr curve
    plot_curve.plot_loss_and_lr(train_loss, learning_rate, os.path.join(save_path, 'loss_and_lr.png'), upload=wandb)
    plot_curve.plot_single(val_map, "mAP@0.5", os.path.join(save_path, 'mAP50.png'), upload=wandb)
    plot_curve.plot_single(recall, "Recall", os.path.join(save_path, 'Recall.png'), upload=wandb)
    plot_curve.plot_single(map0595, 'mAP@0.5-0.95', os.path.join(save_path, 'mAP05-95.png'), upload=wandb)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description=__doc__)

    # 训练设备类型
    parser.add_argument('--device', default='cuda:0', help='device')
    # 训练数据集的根目录(VOCdevkit)/root/autodl-fs/dataset /kaggle/input/voc0712/VOC_dataset
    parser.add_argument('--data-path', default=r'D:\Code\0-data\1-齿轮检测数据集\青山数据集', help='dataset')
    # backbone预训练模型路径 '/root/autodl-fs/dataset/pre-model/resnet50.pth'
    parser.add_argument('--backbone-path',
                        default=r'D:\Code\0-data\5-models-data\pretrained_model\efficientnet_b0.pth',
                        help='backbone path')
    # coco数据集模型路径 '/root/autodl-fs/dataset/pre-model/fasterrcnn_resnet50_fpn_coco.pth'
    parser.add_argument('--coco-path', default=None,
                        help='coco pre model')
    # coco数据集模型路径
    parser.add_argument('--json-path',
                        default=r'D:\Code\0-data\1-齿轮检测数据集\青山数据集\VOCdevkit\VOC2012\classes.json', help='json path')
    # 检测目标类别数(不包含背景)
    parser.add_argument('--num-classes', default=1, type=int, help='num_classes')
    # 文件保存地址/root/autodl-fs/output '/kaggle/working/output_{}'.format(
    #                             datetime.now(timezone(timedelta(hours=8))).strftime('%m-%d-%H-%M'))
    parser.add_argument('--output-dir',
                        default='save_weights'
                        , help='path where to save')
    # 若需要接着上次训练，则指定上次训练保存权重文件地址
    parser.add_argument('--resume', default='', type=str, help='resume from checkpoint')
    # 指定接着从哪个epoch数开始训练
    parser.add_argument('--start_epoch', default=0, type=int, help='start epoch')
    # 训练的总epoch数
    parser.add_argument('--epochs', default=70, type=int, metavar='N',
                        help='number of total epochs to run')
    # 训练的batch size
    parser.add_argument('--batch_size', default=3, type=int, metavar='N',
                        help='batch size when training.')
    # 学习率
    parser.add_argument('--lr', default=0.01, type=float,
                        help='initial learning rate, 0.02 is the default value for training '
                             'on 8 gpus and 2 images_per_gpu')
    # SGD的momentum参数
    parser.add_argument('--momentum', default=0.9, type=float, metavar='M',
                        help='momentum')
    # SGD的weight_decay参数
    parser.add_argument('--wd', '--weight-decay', default=1e-4, type=float,
                        metavar='W', help='weight decay (default: 1e-4)',
                        dest='weight_decay')

    parser.add_argument('--aspect-ratio-group-factor', default=3, type=int)
    # 是否使用混合精度训练(需要GPU支持混合精度)
    parser.add_argument("--amp", default=False, help="Use torch.cuda.amp for mixed precision training")

    args = parser.parse_args()
    print(args)

    # 检查保存权重文件夹是否存在，不存在则创建
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    main(args)
