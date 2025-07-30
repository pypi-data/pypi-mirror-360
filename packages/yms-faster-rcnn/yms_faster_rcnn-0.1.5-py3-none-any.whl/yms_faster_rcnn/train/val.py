"""
该脚本用于调用训练好的模型权重去计算验证集/测试集的COCO指标
以及每个类别的mAP(IoU=0.5)
"""

import json
import os

import numpy as np
import torch
from torch.utils.data import DataLoader
from tqdm import tqdm

from yms_faster_rcnn.train.train import create_model
from yms_faster_rcnn.train_utils.my_dataset import VOCDataSet

from yms_faster_rcnn.train_utils import get_coco_api_from_dataset, CocoEvaluator, transforms
import matplotlib.pyplot as plt


def summarize(self, catId=None):
    """
    Compute and display summary metrics for evaluation results.
    Note this functin can *only* be applied on the default parameter setting
    """

    def _summarize(ap=1, iouThr=None, areaRng='all', maxDets=100):
        p = self.params
        iStr = ' {:<18} {} @[ IoU={:<9} | area={:>6s} | maxDets={:>3d} ] = {:0.3f}'
        titleStr = 'Average Precision' if ap == 1 else 'Average Recall'
        typeStr = '(AP)' if ap == 1 else '(AR)'
        iouStr = '{:0.2f}:{:0.2f}'.format(p.iouThrs[0], p.iouThrs[-1]) \
            if iouThr is None else '{:0.2f}'.format(iouThr)

        aind = [i for i, aRng in enumerate(p.areaRngLbl) if aRng == areaRng]
        mind = [i for i, mDet in enumerate(p.maxDets) if mDet == maxDets]

        if ap == 1:
            # dimension of precision: [TxRxKxAxM]
            s = self.eval['precision']
            # IoU
            if iouThr is not None:
                t = np.where(iouThr == p.iouThrs)[0]
                s = s[t]

            if isinstance(catId, int):
                s = s[:, :, catId, aind, mind]
            else:
                s = s[:, :, :, aind, mind]

        else:
            # dimension of recall: [TxKxAxM]
            s = self.eval['recall']
            if iouThr is not None:
                t = np.where(iouThr == p.iouThrs)[0]
                s = s[t]

            if isinstance(catId, int):
                s = s[:, catId, aind, mind]
            else:
                s = s[:, :, aind, mind]

        if len(s[s > -1]) == 0:
            mean_s = -1
        else:
            mean_s = np.mean(s[s > -1])

        print_string = iStr.format(titleStr, typeStr, iouStr, areaRng, maxDets, mean_s)
        return mean_s, print_string

    stats, print_list = [0] * 13, [""] * 13
    stats[0], print_list[0] = _summarize(1)
    stats[1], print_list[1] = _summarize(1, iouThr=.5, maxDets=self.params.maxDets[2])
    stats[2], print_list[2] = _summarize(1, iouThr=.75, maxDets=self.params.maxDets[2])
    stats[3], print_list[3] = _summarize(1, areaRng='small', maxDets=self.params.maxDets[2])
    stats[4], print_list[4] = _summarize(1, areaRng='medium', maxDets=self.params.maxDets[2])
    stats[5], print_list[5] = _summarize(1, areaRng='large', maxDets=self.params.maxDets[2])
    stats[6], print_list[6] = _summarize(0, maxDets=self.params.maxDets[0])
    stats[7], print_list[7] = _summarize(0, maxDets=self.params.maxDets[1])
    stats[8], print_list[8] = _summarize(0, maxDets=self.params.maxDets[2])
    stats[9], print_list[9] = _summarize(0, areaRng='small', maxDets=self.params.maxDets[2])
    stats[10], print_list[10] = _summarize(0, areaRng='medium', maxDets=self.params.maxDets[2])
    stats[11], print_list[11] = _summarize(0, areaRng='large', maxDets=self.params.maxDets[2])
    stats[12], print_list[12] = _summarize(0, iouThr=.5, maxDets=self.params.maxDets[2])

    print_info = "\n".join(print_list)

    if not self.eval:
        raise Exception('Please run accumulate() first')

    return stats, print_info


def plot_pr_curve(result, category_index):
    """
    绘制P-R曲线的函数

    参数:
    - coco_eval: COCOeval类的实例，包含了评估结果数据
    - class_id: 可选参数，指定绘制某个类别的P-R曲线，如果为None则绘制所有类别的平均P-R曲线
    - iou_thr: 可选参数，指定IoU阈值，如果为None则使用默认的IoU阈值范围
    """

    plt.xlabel('recall')
    plt.ylabel('precision')
    plt.xlim(0, 1.0)
    plt.ylim(0, 1.01)
    plt.grid(True)
    for i in range(len(category_index)):
        recall = result.params.recThrs
        precision = result.eval['precision'][0, :, i, 0, 2]
        plt.plot(recall, precision, label=category_index[i+1])
    # plt.xlabel('recall')
    # plt.ylabel('precision')
    # plt.plot(recall, precision)
    plt.legend(loc='lower left')
    # plt.show()
    plt.savefig()


def voc_ap(rec, prec, use_07_metric=False):
    """ ap = voc_ap(rec, prec, [use_07_metric])
    Compute VOC AP given precision and recall.
    If use_07_metric is true, uses the
    VOC 07 11 point method (default:False).
    """
    if use_07_metric:
        # 11 point metric
        ap = 0.
        for t in np.arange(0., 1.1, 0.1):
            if np.sum(rec >= t) == 0:
                p = 0
            else:
                p = np.max(prec[rec >= t])
            ap = ap + p / 11.
    else:
        # correct AP calculation
        # first append sentinel values at the end
        mrec = np.concatenate(([0.], rec, [1.]))
        mpre = np.concatenate(([0.], prec, [0.]))

        # compute the precision envelope
        for i in range(mpre.size - 1, 0, -1):
            mpre[i - 1] = np.maximum(mpre[i - 1], mpre[i])

        # to calculate area under PR curve, look for points
        # where X axis (recall) changes value
        i = np.where(mrec[1:] != mrec[:-1])[0]

        # and sum (\Delta recall) * prec
        ap = np.sum((mrec[i + 1] - mrec[i]) * mpre[i + 1])
    return ap


def result_to_voc_object(result, index, category_index):
    """
    将单个检测结果转为VOC格式的对象信息

    参数:
    - result: 单个检测结果，包含类别、边界框等信息，格式类似 {'category_id': int, 'bbox': [xmin, ymin, xmax, ymax]}
    - category_index: 类别索引字典，格式 {类别id: 类别名称}

    返回:
    - voc_object: VOC格式的对象信息字典，格式 {'name': 类别名称, 'difficult': 0, 'bndbox': {'xmin': int, 'ymin': int, 'xmax': int, 'ymax': int}}
    """
    category_id = result['labels'][index].item()
    class_name = category_index[category_id]
    bbox = result['boxes'][index]
    xmin, ymin, xmax, ymax = [int(x) for x in bbox]
    voc_object = {
        'name': class_name,
        'difficult': 0,
        'bndbox': {
            'xmin': xmin,
            'ymin': ymin,
            'xmax': xmax,
            'ymax': ymax
        }
    }
    return voc_object


def w_xml(res, coco, category_index, val_data):
    # 将res中的检测结果转为VOC标注格式并保存为.xml文件
    for image_id, detections in res.items():
        # 假设image_id能对应到实际的文件名，这里提取文件名（你可能需要根据实际情况调整获取文件名的方式）
        xml_filename = val_data.xml_list[image_id]
        # image_filename = f"{image_id}__H2_817171_IO-NIO198M_210119A0184-1-1.jpg"  # 这里示例的文件名格式只是模拟，需按实际调整
        image_filename = xml_filename.replace('.xml', '.jpg')
        xml_path = os.path.join(r'D:\Code\data\故障诊断结果输出', os.path.basename(xml_filename))  # 创建保存xml文件的目录，这里假设是output_xmls，按需调整
        os.makedirs(os.path.dirname(xml_path), exist_ok=True)
        image = coco.dataset['images'][image_id]
        xml_content = ['<annotation>',
                       f'  <folder>VOC2012</folder>',
                       f'  <filename>{os.path.basename(image_filename)}</filename>',
                       '  <size>',
                       f'    <width>{image["width"]}</width>',  # 这里假设image对象有size属性包含宽高，需按实际调整获取宽高方式
                       f'    <height>{image["height"]}</height>',
                       '    <depth>3</depth>',
                       '  </size>']
        # num = len(detections['labels'])
        for i in range(len(detections['labels'])):
            voc_object = result_to_voc_object(detections, i, category_index)
            xml_content.append('  <object>')
            xml_content.append(f'    <name>{voc_object["name"]}</name>')
            xml_content.append(f'    <difficult>{voc_object["difficult"]}</difficult>')
            xml_content.append('    <bndbox>')
            xml_content.append(f'      <xmin>{voc_object["bndbox"]["xmin"]}</xmin>')
            xml_content.append(f'      <ymin>{voc_object["bndbox"]["ymin"]}</ymin>')
            xml_content.append(f'      <xmax>{voc_object["bndbox"]["xmax"]}</xmax>')
            xml_content.append(f'      <ymax>{voc_object["bndbox"]["ymax"]}</ymax>')
            xml_content.append('    </bndbox>')
            xml_content.append('  </object>')

        xml_content.append('</annotation>')

        with open(xml_path, 'w') as f:
            f.write('\n'.join(xml_content))


def main(parser_data):
    device = torch.device(parser_data.device if torch.cuda.is_available() else "cpu")
    print("Using {} device training.".format(device.type))

    data_transform = {
        "val": transforms.Compose([transforms.ToTensor()])
    }

    # read class_indict
    label_json_path = r'D:\Code\0-data\1-齿轮检测数据集\青山数据集\VOCdevkit\VOC2012\classes.json'
    assert os.path.exists(label_json_path), "json file {} dose not exist.".format(label_json_path)
    with open(label_json_path, 'r') as f:
        class_dict = json.load(f)

    category_index = {v: k for k, v in class_dict.items()}

    VOC_root = parser_data.data_path
    # check voc root
    if os.path.exists(os.path.join(VOC_root, "VOCdevkit")) is False:
        raise FileNotFoundError("VOCdevkit dose not in path:'{}'.".format(VOC_root))

    # 注意这里的collate_fn是自定义的，因为读取的数据包括image和targets，不能直接使用默认的方法合成batch
    batch_size = parser_data.batch_size
    nw = min([os.cpu_count(), batch_size if batch_size > 1 else 0, 8])  # number of workers
    print('Using %g dataloader workers' % nw)

    # load data_process data set
    val_dataset = VOCDataSet(VOC_root, "2012", data_transform["val"], "val.txt",
                             json_file=r'D:\Code\0-data\1-齿轮检测数据集\青山数据集\VOCdevkit\VOC2012\classes.json')
    val_dataset_loader = DataLoader(val_dataset,
                                    batch_size=1,
                                    shuffle=False,
                                    num_workers=nw,
                                    pin_memory=True,
                                    collate_fn=val_dataset.collate_fn)

    model = create_model(num_classes=2,pretrain_path=r'D:\Code\0-data\5-models-data\pretrained_model\resnet50.pth')
    # 载入你自己训练好的模型权重
    weights_path = parser_data.weights_path
    assert os.path.exists(weights_path), "not found {} file.".format(weights_path)
    weights_dict = torch.load(weights_path, map_location='cpu', weights_only=True)
    weights_dict = weights_dict["model"] if "model" in weights_dict else weights_dict
    model.load_state_dict(weights_dict)

    model.to(device)

    # evaluate on the test dataset
    coco = get_coco_api_from_dataset(val_dataset)
    iou_types = ["bbox"]
    coco_evaluator = CocoEvaluator(coco, iou_types)
    cpu_device = torch.device("cpu")
    model.eval()
    with torch.no_grad():
        for image, targets in tqdm(val_dataset_loader, desc="data_process..."):
            # 将图片传入指定设备device
            images = list(img.to(device) for img in image)

            # inference
            outputs = model(images)

            outputs = [{k: v.to(cpu_device) for k, v in t.items()} for t in outputs]
            res = {target["image_id"].item(): output for target, output in zip(targets, outputs)}
            coco_evaluator.update(res)
    coco_evaluator.synchronize_between_processes()

    # accumulate predictions from all images
    coco_evaluator.accumulate()
    coco_evaluator.summarize()

    coco_eval = coco_evaluator.coco_eval["bbox"]
    # calculate COCO info for all classes
    coco_stats, print_coco = summarize(coco_eval)
    plot_pr_curve(coco_eval, category_index)

    # calculate voc info for every classes(IoU=0.5)
    voc_map_info_list = []
    voc_recall_info_list = []
    for i in range(len(category_index)):
        stats, _ = summarize(coco_eval, catId=i)
        voc_map_info_list.append(" {:15}: {}".format(category_index[i + 1], stats[1]))
        voc_recall_info_list.append(" {:15}: {}".format(category_index[i + 1], stats[12]))

    print_voc = "\n".join(voc_map_info_list)
    print_voc_recall = "\n".join(voc_recall_info_list)
    print(print_voc)
    print(print_voc_recall)

    # 将验证结果保存至txt文件中
    with open("record_mAP.txt", "w") as f:
        record_lines = ["COCO results:",
                        print_coco,
                        "",
                        "mAP(IoU=0.5) for each category:",
                        print_voc,
                        "",
                        "recall(IoU=0.5) for each category:",
                        print_voc_recall
                        ]
        f.write("\n".join(record_lines))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description=__doc__)

    # 使用设备类型
    parser.add_argument('--device', default='cuda', help='device')

    # 检测目标类别数
    parser.add_argument('--num-classes', type=int, default=1, help='number of classes')

    # 数据集的根目录(VOCdevkit)
    parser.add_argument('--data-path', default=r'D:\Code\0-data\1-齿轮检测数据集\青山数据集', help='dataset root')

    # 训练好的权重文件
    parser.add_argument('--weights-path',
                        default=r'D:\Code\0-data\0-故障诊断结果输出\results\save_weights\best_model.pth',
                        type=str, help='training weights')

    # batch size
    parser.add_argument('--batch_size', default=1, type=int, metavar='N',
                        help='batch size when data_process.')

    args = parser.parse_args()

    main(args)
