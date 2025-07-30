import argparse
import os
import time
from datetime import timedelta

import torch
from torch.optim.lr_scheduler import ReduceLROnPlateau
from torch.utils.data import DataLoader

from yms_faster_rcnn.backbone import resnet50_fpn_backbone
from yms_faster_rcnn.network_files import FasterRCNN, FastRCNNPredictor
from yms_faster_rcnn.train_utils import GroupedBatchSampler, create_aspect_ratio_groups, transforms
from yms_faster_rcnn.train_utils import plot_curve
from yms_faster_rcnn.train_utils import train_eval_utils as utils
from yms_faster_rcnn.train_utils.my_dataset import VOCDataSet


def create_model(num_classes, pretrain_path, coco_path=None):
    # 注意，这里的backbone默认使用的是FrozenBatchNorm2d，即不会去更新bn参数
    # 目的是为了防止batch_size太小导致效果更差(如果显存很小，建议使用默认的FrozenBatchNorm2d)
    # 如果GPU显存很大可以设置比较大的batch_size就可以将norm_layer设置为普通的BatchNorm2d
    # trainable_layers包括['layer4', 'layer3', 'layer2', 'layer1', 'conv1']， 5代表全部训练
    # resnet50 imagenet weights url: https://download.pytorch.org/models/resnet50-0676ba61.pth
    backbone = resnet50_fpn_backbone(pretrain_path=pretrain_path,
                                     norm_layer=torch.nn.BatchNorm2d,
                                     trainable_layers=3)
    # 训练自己数据集时不要修改这里的91，修改的是传入的num_classes参数
    model = FasterRCNN(backbone=backbone, num_classes=91, min_size=1000, max_size=1000)

    if coco_path is not None:
        # 载入预训练模型权重
        # https://download.pytorch.org/models/fasterrcnn_resnet50_fpn_coco-258fb6c6.pth
        weights_dict = torch.load(coco_path, map_location='cpu')
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
    os.makedirs(save_path, exist_ok=True)
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

    # load data_process data set
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
                         pretrain_path=args.backbone_path,
                         coco_path=args.coco_path)
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

    lr_scheduler = ReduceLROnPlateau(optimizer, mode='max', factor=0.1, patience=5, min_lr=1e-8)
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
    best_recall = None
    max_recall = -1
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

        if coco_info[12] > max_recall:
            max_recall = coco_info[12]
            if best_model is not None:
                os.remove(best_recall)
            best_recall = os.path.join(save_path, "best-recall-{}.pth".format(epoch))
            torch.save(save_files, best_recall)

    total_time = time.time() - start_time
    total_time_str = str(timedelta(seconds=int(total_time)))
    print('Training time {}'.format(total_time_str))
    print(f'the best model is:{best_model}, the last model is:{last_model}, the best recall model is:{best_recall}')
    os.rename(last_model, os.path.join(save_path, "last_model.pth"))
    os.rename(best_model, os.path.join(save_path, "best_model.pth"))
    os.rename(best_recall, os.path.join(save_path, "best_recall.pth"))
    # plot loss and lr curve
    plot_curve.plot_loss_and_lr(train_loss, learning_rate, os.path.join(save_path, 'loss_and_lr.png'))
    plot_curve.plot_single(val_map, "mAP@0.5", os.path.join(save_path, 'mAP50.png'))
    plot_curve.plot_single(recall, "Recall", os.path.join(save_path, 'Recall.png'))
    plot_curve.plot_single(map0595, 'mAP@0.5-0.95', os.path.join(save_path, 'mAP05-95.png'))


def parse_args(args=None):
    parser = argparse.ArgumentParser(description=__doc__)
    # 训练设备类型
    parser.add_argument('--device', default='cuda:0', help='device')
    # 训练数据集的根目录(VOCdevkit)
    parser.add_argument('--data-path', default=r'D:\Code\0-data\1-齿轮检测数据集\青山数据集', help='dataset')
    # 卷积网络预训练模型
    parser.add_argument('--backbone-path',
                        default=r'D:\Code\0-data\5-models-data\pretrained_model\efficientnet_b0.pth',
                        help='backbone path')
    # 在COCO数据集上的预训练模型
    parser.add_argument('--coco-path', default=None,
                        help='coco pre model')
    # coco数据集模型路径
    parser.add_argument('--json-path',
                        default=r'D:\Code\0-data\1-齿轮检测数据集\青山数据集\VOCdevkit\VOC2012\classes.json',
                        help='json path')
    # 检测目标类别数(不包含背景)
    parser.add_argument('--num-classes', default=1, type=int, help='num_classes')
    # 结果保存路径
    parser.add_argument('--output-dir',default='save_weights', help='path where to save', type=str)
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
    # 若需要接着上次训练，则指定上次训练保存权重文件地址
    parser.add_argument('--resume', default='', type=str, help='resume from checkpoint')
    # 指定接着从哪个epoch数开始训练
    parser.add_argument('--start_epoch', default=0, type=int, help='start epoch')


    parser.add_argument('--aspect-ratio-group-factor', default=3, type=int)
    # 是否使用混合精度训练(需要GPU支持混合精度)
    parser.add_argument("--amp", default=False, help="Use torch.cuda.amp for mixed precision training")

    return parser.parse_args(args if args else [])

if __name__ == "__main__":
    opts = parse_args()
    print(opts)
    main(opts)
