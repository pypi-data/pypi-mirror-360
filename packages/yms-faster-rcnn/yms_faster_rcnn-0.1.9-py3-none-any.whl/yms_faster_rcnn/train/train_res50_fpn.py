import json
import os
from datetime import datetime

import torch
from torch.optim.lr_scheduler import ReduceLROnPlateau
from torch.utils.data import DataLoader

from yms_faster_rcnn.network_files import FasterRCNN, FastRCNNPredictor, AnchorsGenerator
from yms_faster_rcnn.backbone import resnet50_fpn_backbone
from yms_faster_rcnn.train_utils.my_dataset import VOCDataSet
from yms_faster_rcnn.train_utils import GroupedBatchSampler, create_aspect_ratio_groups, transforms
from yms_faster_rcnn.train_utils import train_eval_utils as utils



def create_model(num_classes, load_pretrain_weights=True):
    # 注意，这里的backbone默认使用的是FrozenBatchNorm2d，即不会去更新bn参数
    # 目的是为了防止batch_size太小导致效果更差(如果显存很小，建议使用默认的FrozenBatchNorm2d)
    # 如果GPU显存很大可以设置比较大的batch_size就可以将norm_layer设置为普通的BatchNorm2d
    # trainable_layers包括['layer4', 'layer3', 'layer2', 'layer1', 'conv1']， 5代表全部训练
    # resnet50 imagenet weights url: https://download.pytorch.org/models/resnet50-0676ba61.pth
    # r"/root/autodl-fs/dataset/model_data/resnet50.pth"
    backbone = resnet50_fpn_backbone(pretrain_path=r"F:\IDM_Downloads\模型\resnet50.pth",
                                     norm_layer=torch.nn.BatchNorm2d,
                                     trainable_layers=3)
    # 训练自己数据集时不要修改这里的91，
    anchor_sizes = ((24.57825,), (47.36648,), (58.26067,), (72.75418,), (85.0448,))
    aspect_ratios = ((1.3789759, 1.9460917, 2.260112),) * len(anchor_sizes)
    anchor_generator = AnchorsGenerator(sizes=anchor_sizes,
                                        aspect_ratios=aspect_ratios)
    # anchor_generator = AnchorsGenerator(sizes=((32, 64, 128, 256, 512),),
    #                                     aspect_ratios=((0.5, 1.0, 2.0),))
    model = FasterRCNN(min_size=800, max_size=800, rpn_anchor_generator=anchor_generator,
                       backbone=backbone, num_classes=91)

    if load_pretrain_weights:
        # 载入预训练模型权重r"/root/autodl-fs/dataset/model_data/fasterrcnn_resnet50_fpn_coco.pth"
        # https://download.pytorch.org/models/fasterrcnn_resnet50_fpn_coco-258fb6c6.pth
        weights_dict = torch.load(r"F:\IDM_Downloads\模型\fasterrcnn_resnet50_fpn_coco.pth",
                                  map_location='cpu', weights_only=True)
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
    # runs = datetime.now(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S')
    # wandb.require("core")
    # wandb.login(key="e502fedb5d4a0eb4babbdd4ff0b423d6a53ebfad")
    # wandb.init(project="Faster_RCNN", name=runs)
    # arti_model = wandb.Artifact('Faster_RCNN', type='model')
    # arti_txt = wandb.Artifact('txt', type='txt')
    save_path = args.output_dir
    label_json_path = 'classes.json'
    assert os.path.exists(label_json_path), "json file {} dose not exist.".format(label_json_path)
    with open(label_json_path, 'r') as f:
        class_dict = json.load(f)

    device = torch.device(args.device if torch.cuda.is_available() else "cpu")
    print("Using {} device training.".format(device.type))

    # 用来保存coco_info的文件
    results_file = "results{}.txt".format(datetime.now().strftime("%Y%m%d-%H%M%S"))
    results_file = os.path.join(save_path, results_file)

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
    train_dataset = VOCDataSet(VOC_root, '2012', data_transform["train"], "train.txt")
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
    nw = min([os.cpu_count(), batch_size if batch_size > 1 else 0, 8])  # number of workers
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
    val_dataset = VOCDataSet(VOC_root, '2012', data_transform["val"], "val.txt")
    val_data_set_loader = DataLoader(val_dataset,
                                     batch_size=1,
                                     shuffle=False,
                                     pin_memory=True,
                                     num_workers=nw,
                                     collate_fn=val_dataset.collate_fn)

    # create model num_classes equal background + 20 classes
    model = create_model(num_classes=args.num_classes + 1)
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
    #                                                step_size=3,
    #                                                gamma=0.33)

    # 定义优化器
    # initial_lr = args.lr
    # min_lr = 1e-6
    # # 定义学习率调度的 lambda 函数
    # lr_lambda = lambda epoch: max(min_lr, initial_lr * (0.5 ** (epoch // 3)))
    # # 创建 LambdaLR 调度器
    # lr_scheduler = torch.optim.lr_scheduler.LambdaLR(optimizer, lr_lambda)
    lr_scheduler = ReduceLROnPlateau(optimizer, mode='min', factor=0.1, patience=10)

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
    max_map = 0
    best_model = None

    for epoch in range(args.start_epoch, args.epochs):
        # train for one epoch, printing every 10 iterations
        mean_loss, lr = utils.train_one_epoch(model, optimizer, train_data_loader,
                                              device=device, epoch=epoch,
                                              print_freq=50, warmup=True,
                                              scaler=scaler)
        train_loss.append(mean_loss.item())
        learning_rate.append(lr)

        # update the learning rate
        lr_scheduler.step(mean_loss.item())
        # evaluate on the test dataset
        coco_info = utils.evaluate(model, val_data_set_loader, device=device, class_dict=class_dict)

        # write into txt
        with open(results_file, "a") as f:
            # 写入的数据包括coco指标还有loss和learning rate
            result_info = [f"{i:.4f}" for i in coco_info + [mean_loss.item()]] + [f"{lr:.6f}"]
            txt = "epoch:{} {}".format(epoch, '  '.join(result_info))
            f.write(txt + "\n")

        val_map.append(coco_info[1])  # pascal mAP
        recall.append(coco_info[12])
        map0595.append(coco_info[0])

        # wandb.log({'train_loss': mean_loss.item(), 'learning_rate': lr, 'map0595': coco_info[0],
        #            'map05': coco_info[1], 'recall': coco_info[8]})
        # save weights
        save_files = {
            'model': model.state_dict(),
            'optimizer': optimizer.state_dict(),
            'lr_scheduler': lr_scheduler.state_dict(),
            'epoch': epoch}
        if args.amp:
            save_files["scaler"] = scaler.state_dict()
        path = os.path.join(save_path, "resNetFpn-model-{}.pth".format(epoch))
        torch.save(save_files, path)
        if coco_info[1] > max_map:
            max_map = coco_info[1]
            best_model = path
        #     save_files = {
        #         'model': model.state_dict(),
        #         'optimizer': optimizer.state_dict(),
        #         'lr_scheduler': lr_scheduler.state_dict(),
        #         'epoch': epoch}
        #     if args.amp:
        #         save_files["scaler"] = scaler.state_dict()
        #     new_model_fine = "resNetFpn-model-{}-map_{}.pth".format(epoch, max_map)
        #     path = os.path.join("/kaggle/working/save_weights", new_model_fine)
        #     torch.save(save_files, path)
        #     if last_model is not None:
        #         os.remove(last_model)
        #     last_model = path'save_weights/'

    # plot loss and lr curve
    # plot_curve.plot_loss_and_lr(train_loss, learning_rate,
    #                             os.path.join(save_path,
    #                                          '.loss_and_lr{}.png'.format(datetime.now().strftime("%Y%m%d-%H%M%S"))),
    #                             upload=wandb)
    # plot_curve.plot_single(val_map, "mAP50", os.path.join(save_path, 'mAP50.png'), upload=wandb)
    # plot_curve.plot_single(recall, "recall", os.path.join(save_path, 'recall.png'), upload=wandb)
    # plot_curve.plot_single(map0595, 'map@05-95', os.path.join(save_path, 'map05-95.png'), upload=wandb)
    # arti_txt.add_file(results_file)
    # wandb.log_artifact(arti_txt)
    # if best_model is not None:
    #     arti_model.add_file(best_model)
    #     wandb.log_model(arti_model)
    # wandb.finish()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description=__doc__)

    # 训练设备类型
    parser.add_argument('--device', default='cuda:0', help='device')
    # 训练数据集的根目录(VOCdevkit)/root/autodl-fs/dataset
    parser.add_argument('--data-path', default=r'F:\IDM_Downloads', help='dataset')
    # 检测目标类别数(不包含背景)
    parser.add_argument('--num-classes', default=3, type=int, help='num_classes')
    # 文件保存地址/root/autodl-tmp/FasterRCNN
    parser.add_argument('--output-dir', default='./save_weights', help='path where to save')
    # 若需要接着上次训练，则指定上次训练保存权重文件地址
    parser.add_argument('--resume', default='', type=str, help='resume from checkpoint')
    # 指定接着从哪个epoch数开始训练
    parser.add_argument('--start_epoch', default=0, type=int, help='start epoch')
    # 训练的总epoch数
    parser.add_argument('--epochs', default=50, type=int, metavar='N',
                        help='number of total epochs to run')
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
    # 训练的batch size
    parser.add_argument('--batch_size', default=1, type=int, metavar='N',
                        help='batch size when training.')
    parser.add_argument('--aspect-ratio-group-factor', default=3, type=int)
    # 是否使用混合精度训练(需要GPU支持混合精度)
    parser.add_argument("--amp", default=True, help="Use torch.cuda.amp for mixed precision training")

    args = parser.parse_args()
    print(args)

    # 检查保存权重文件夹是否存在，不存在则创建
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    main(args)
