import json
import os
import xml.etree.ElementTree as ET
from xml.dom import minidom

import random
from collections import defaultdict



def json_to_xml(json_path, output_dir):
    """
    将json格式的数据集转为xml格式的数据集

    """
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)

    # 读取JSON文件
    with open(json_path, 'r') as f:
        data = json.load(f)

    # 构建类别ID到名称的映射
    categories = {cat['id']: cat['name'] for cat in data['categories']}

    # 按图像ID分组标注
    image_anns = {}
    for ann in data['annotations']:
        image_id = ann['image_id']
        if image_id not in image_anns:
            image_anns[image_id] = []
        image_anns[image_id].append(ann)

    # 构建图像ID到图像信息的映射
    images_info = {img['id']: img for img in data['images']}

    # 为每张图像生成XML
    for img_id, anns in image_anns.items():
        img_info = images_info[img_id]
        filename = img_info['file_name']
        width = img_info['width']
        height = img_info['height']

        # 创建XML根节点
        root = ET.Element('annotation')

        # 添加基本信息
        ET.SubElement(root, 'folder').text = 'VOC'
        ET.SubElement(root, 'filename').text = filename

        # 添加图像尺寸
        size = ET.SubElement(root, 'size')
        ET.SubElement(size, 'width').text = str(width)
        ET.SubElement(size, 'height').text = str(height)
        ET.SubElement(size, 'depth').text = '3'  # 假设RGB图像

        ET.SubElement(root, 'segmented').text = '0'

        # 添加每个检测对象
        for ann in anns:
            obj = ET.SubElement(root, 'object')
            ET.SubElement(obj, 'name').text = categories[ann['category_id']]
            ET.SubElement(obj, 'pose').text = 'Unspecified'
            ET.SubElement(obj, 'truncated').text = '0'
            ET.SubElement(obj, 'difficult').text = '0'

            # 转换边界框格式: [x_min, y_min, width, height] -> [xmin, ymin, xmax, ymax]
            bbox = ann['bbox']
            xmin = bbox[0]
            ymin = bbox[1]
            xmax = xmin + bbox[2]
            ymax = ymin + bbox[3]

            # 确保坐标不超出图像范围
            xmin = max(0, min(xmin, width))
            ymin = max(0, min(ymin, height))
            xmax = max(0, min(xmax, width))
            ymax = max(0, min(ymax, height))

            # 添加边界框
            bndbox = ET.SubElement(obj, 'bndbox')
            ET.SubElement(bndbox, 'xmin').text = str(int(xmin))
            ET.SubElement(bndbox, 'ymin').text = str(int(ymin))
            ET.SubElement(bndbox, 'xmax').text = str(int(xmax))
            ET.SubElement(bndbox, 'ymax').text = str(int(ymax))

        # 生成XML字符串并美化输出
        xml_str = ET.tostring(root, encoding='utf-8')
        dom = minidom.parseString(xml_str)
        pretty_xml = dom.toprettyxml(indent='  ')

        # 写入文件 (使用图像ID作为文件名)
        xml_filename = os.path.splitext(filename)[0] + '.xml'
        xml_path = os.path.join(output_dir, xml_filename)
        with open(xml_path, 'w') as xml_file:
            xml_file.write(pretty_xml)


def write_filenames_without_ext(folder_path, output_file):
    """
    将文件夹内所有文件的文件名（不带后缀）写入到文本文件中

    参数:
        folder_path: 要扫描的文件夹路径
        output_file: 输出的文本文件路径
    """
    # 获取文件夹内所有文件名（不包括子目录）
    filenames = [f for f in os.listdir(folder_path)
                 if os.path.isfile(os.path.join(folder_path, f))]

    # 去掉文件后缀
    names_without_ext = [os.path.splitext(f)[0] for f in filenames]

    # 写入到文本文件
    with open(output_file, 'w') as f:
        for name in names_without_ext:
            f.write(name + '\n')

    print(f"成功写入 {len(names_without_ext)} 个文件名到 {output_file}")



if __name__ == "__main__":
    # # 示例用法
    # json_path = r"D:\Code\0-data\1-齿轮检测数据集\青山数据集\qingshan_dianquketi_v1.json"  # 输入JSON文件路径
    # output_dir = r"D:\Code\0-data\1-齿轮检测数据集\青山数据集\xml"  # 输出XML目录
    #
    # json_to_xml(json_path, output_dir)
    # print(f"转换完成！XML文件已保存至: {output_dir}")
    # 配置参数
    # input_folder = r"D:\Code\0-data\1-齿轮检测数据集\青山数据集\xml"  # 替换为你的文件夹路径
    # output_txt = r"D:\Code\0-data\1-齿轮检测数据集\青山数据集\all.txt"  # 输出的文本文件名
    #
    # write_filenames_without_ext(input_folder, output_txt)
    print()
