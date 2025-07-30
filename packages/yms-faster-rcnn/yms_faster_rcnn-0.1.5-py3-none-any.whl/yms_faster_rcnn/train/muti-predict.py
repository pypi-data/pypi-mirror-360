import argparse
import os
import time
import json
from xml.dom import minidom

import torch
from PIL import Image
import matplotlib.pyplot as plt

from torchvision import transforms
from yms_faster_rcnn.train.draw_box_utils import my_draw_objs
from yms_faster_rcnn.train.predict import create_model
import xml.etree.ElementTree as ET

def time_synchronized():
    torch.cuda.synchronize() if torch.cuda.is_available() else None
    return time.time()


def create_xml_annotation(image_path, boxes, classes, scores, output_path, class_dict, box_thresh=0.5):
    """创建XML标注文件"""
    # 读取图片信息
    img = Image.open(image_path)
    width, height = img.size
    depth = 3  # 假设为RGB图片

    # 创建XML根节点
    annotation = ET.Element("annotation")

    # 添加文件夹信息
    folder = ET.SubElement(annotation, "folder")
    folder.text = os.path.basename(os.path.dirname(image_path))

    # 添加文件名信息
    filename = ET.SubElement(annotation, "filename")
    filename.text = os.path.basename(image_path)

    # 添加路径信息
    path = ET.SubElement(annotation, "path")
    path.text = image_path

    # 添加源信息
    source = ET.SubElement(annotation, "source")
    database = ET.SubElement(source, "database")
    database.text = "Unknown"

    # 添加图片尺寸信息
    size = ET.SubElement(annotation, "size")
    w = ET.SubElement(size, "width")
    w.text = str(width)
    h = ET.SubElement(size, "height")
    h.text = str(height)
    d = ET.SubElement(size, "depth")
    d.text = str(depth)

    # 添加 segmented 标签
    segmented = ET.SubElement(annotation, "segmented")
    segmented.text = "0"

    # 符合阈值的目标数量
    valid_objects = 0

    # 添加每个目标的标注信息
    for box, cls, score in zip(boxes, classes, scores):
        if score < box_thresh:  # 过滤低置信度结果
            continue

        valid_objects += 1
        obj = ET.SubElement(annotation, "object")

        # 类别名称
        name = ET.SubElement(obj, "name")
        class_name = class_dict.get(str(cls), "unknown")
        name.text = class_name

        # pose
        pose = ET.SubElement(obj, "pose")
        pose.text = "Unspecified"

        # 截断信息
        truncated = ET.SubElement(obj, "truncated")
        truncated.text = "0"

        # difficult
        difficult = ET.SubElement(obj, "difficult")
        difficult.text = "0"

        # 边界框
        bndbox = ET.SubElement(obj, "bndbox")
        xmin = ET.SubElement(bndbox, "xmin")
        xmin.text = str(int(round(box[0])))
        ymin = ET.SubElement(bndbox, "ymin")
        ymin.text = str(int(round(box[1])))
        xmax = ET.SubElement(bndbox, "xmax")
        xmax.text = str(int(round(box[2])))
        ymax = ET.SubElement(bndbox, "ymax")
        ymax.text = str(int(round(box[3])))

        # 置信度
        confidence = ET.SubElement(obj, "confidence")
        confidence.text = str(round(score, 4))

    # 只有当存在有效目标时才保存XML文件
    if valid_objects > 0:
        # 格式化XML并保存
        rough_string = ET.tostring(annotation, 'utf-8')
        reparsed = minidom.parseString(rough_string)
        pretty_xml = reparsed.toprettyxml(indent="  ")

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(pretty_xml)
        return True  # 成功生成标注
    else:
        return False  # 没有有效目标，不生成标注


def main():
    # 解析命令行参数
    args = get_args()

    # 创建输出文件夹
    os.makedirs(args.output_xml_folder, exist_ok=True)

    # get devices
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    print("using {} device.".format(device))

    # create model
    model = create_model(num_classes=2)

    # 加载训练权重
    assert os.path.exists(args.weights_path), f"{args.weights_path} file dose not exist."
    weights_dict = torch.load(args.weights_path, map_location='cpu')
    weights_dict = weights_dict["model"] if "model" in weights_dict else weights_dict
    model.load_state_dict(weights_dict)
    model.to(device)
    model.eval()  # 进入验证模式

    # 加载类别字典
    assert os.path.exists(args.label_json), f"json file {args.label_json} dose not exist."
    with open(args.label_json, 'r') as f:
        class_dict = json.load(f)

    category_index = {str(v): str(k) for k, v in class_dict.items()}

    # 读取需要处理的图片名列表
    assert os.path.exists(args.txt_path), f"txt file {args.txt_path} dose not exist."
    with open(args.txt_path, 'r') as f:
        image_names = [line.strip() for line in f if line.strip()]

    # 定义数据转换
    data_transform = transforms.Compose([transforms.ToTensor()])

    # 处理每个图片
    total_count = len(image_names)
    for i, image_name in enumerate(image_names, 1):  # 从1开始计数
        # 显示进度信息
        processed = i
        remaining = total_count - i
        progress = (processed / total_count) * 100
        print(f"\n===== 进度: {processed}/{total_count} ({progress:.1f}%)，还剩 {remaining} 张 =====")
        # 尝试不同的图片后缀
        found = False
        for ext in args.img_exts:
            image_file = image_name + ext
            image_path = os.path.join(args.img_folder, image_file)
            if os.path.exists(image_path):
                found = True
                break

        if not found:
            print(f"图片 {image_name} 未找到，跳过...")
            continue

        try:
            # 加载图片
            original_img = Image.open(image_path)

            # 将PIL图片转换为张量
            img = data_transform(original_img)
            # 扩展批次维度
            img = torch.unsqueeze(img, dim=0)

            with torch.no_grad():
                t_start = time.time()
                predictions = model(img.to(device))[0]
                t_end = time.time()
                print(f"处理 {image_file}，推理时间: {t_end - t_start:.4f}秒")

                predict_boxes = predictions["boxes"].to("cpu").numpy()
                predict_classes = predictions["labels"].to("cpu").numpy()
                predict_scores = predictions["scores"].to("cpu").numpy()

                # if len(predict_boxes) == 0:
                #     print(f"图片 {image_file} 没有检测到任何目标!")

                # 生成XML标注文件
                xml_output_path = os.path.join(args.output_xml_folder, f"{image_name}.xml")
                generated = create_xml_annotation(
                    image_path=image_path,
                    boxes=predict_boxes,
                    classes=predict_classes,
                    scores=predict_scores,
                    output_path=xml_output_path,
                    class_dict=class_dict,
                    box_thresh=args.box_thresh
                )

                if generated:
                    print(f"已生成XML标注: {xml_output_path}")
                else:
                    print(f"图片 {image_file} 没有检测到符合阈值的目标，不生成标注")

        except Exception as e:
            print(f"处理图片 {image_file} 时出错: {str(e)}")


def get_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='图片目标检测并生成XML标注')

    # 必要参数
    parser.add_argument('--txt_path', type=str,
                        default=r'F:\代码\dataset\VOCdevkit\VOC2012\ImageSets\Main\val.txt',
                        help='包含图片名的txt文件路径')
    parser.add_argument('--img_folder', type=str,
                        default=r'F:\代码\dataset\VOCdevkit\VOC2012\JPEGImages',
                        help='图片文件夹路径')
    parser.add_argument('--output_xml_folder', type=str,
                        default=r'F:\代码\结果\第一次训练结果\xml',
                        help='XML标注文件输出文件夹')
    parser.add_argument('--weights_path', type=str,
                        default=r'F:\代码\train_output\save_weights\best_model.pth',
                        help='模型权重文件路径')
    parser.add_argument('--label_json', type=str,
                        default=r'F:\代码\dataset\VOCdevkit\VOC2012\classes.json',
                        help='类别映射json文件路径')

    # 可选参数
    parser.add_argument('--num_classes', type=int, default=2,
                        help='分类类别数量，默认2')
    parser.add_argument('--box_thresh', type=float, default=0.5,
                        help='边界框置信度阈值，默认0.5')
    parser.add_argument('--img_exts', type=str, nargs='+',
                        default=['.jpg', '.png', '.bmp'],
                        help='图片文件可能的后缀，默认: .jpg .jpeg .png .bmp')

    return parser.parse_args()


if __name__ == '__main__':
    main()
