import os
import argparse
import random
import re
from collections import defaultdict


def split_images_by_category(input_txt, train_txt, val_txt, train_ratio=0.7):
    # 读取输入文件中的所有图片名称
    with open(input_txt, 'r') as f:
        image_names = [line.strip() for line in f.readlines()]

    # 按类别分组图片
    category_images = defaultdict(list)
    for name in image_names:
        # 提取类别（第一个下划线前的部分）
        if '_' in name:
            category = name.split('_', 1)[0]
            category_images[category].append(name)
        else:
            # 没有下划线的图片处理
            print(f"警告: 图片名称 '{name}' 不包含下划线，无法提取类别")
            category_images[name].append(name)  # 使用完整名称作为类别

    # 计算总图片数和类别数
    total_images = len(image_names)
    total_categories = len(category_images)
    print(f"总类别数: {total_categories}, 总图片数: {total_images}")

    # 将类别随机排序
    categories = list(category_images.keys())
    random.shuffle(categories)

    # 初始化训练集和验证集
    train_set = []
    val_set = []
    train_count = 0
    val_count = 0
    train_categories = []
    val_categories = []

    # 计算目标训练集大小
    target_train_size = int(total_images * train_ratio)

    # 分配类别到训练集或验证集
    for category in categories:
        images = category_images[category]
        num_images = len(images)

        # 如果当前训练集图片数 + 该类图片数 <= 目标大小，则加入训练集
        if train_count + num_images <= target_train_size:
            train_set.extend(images)
            train_count += num_images
            train_categories.append(category)
        else:
            # 如果加入训练集会超出目标大小，则加入验证集
            val_set.extend(images)
            val_count += num_images
            val_categories.append(category)

    # 计算最终比例
    actual_ratio = train_count / total_images
    print(f"\n训练集: {len(train_set)} 张图片 ({len(train_categories)} 个类别)")
    print(f"验证集: {len(val_set)} 张图片 ({len(val_categories)} 个类别)")
    print(f"实际分割比例: 训练集 {actual_ratio:.2%}, 验证集 {1 - actual_ratio:.2%}")

    # 写入训练集文件
    with open(train_txt, 'w') as f:
        for name in train_set:
            f.write(name + '\n')

    # 写入验证集文件
    with open(val_txt, 'w') as f:
        for name in val_set:
            f.write(name + '\n')

    # 返回划分结果
    return {
        "train_count": len(train_set),
        "val_count": len(val_set),
        "train_categories": train_categories,
        "val_categories": val_categories
    }


if __name__ == "__main__":
    input_txt = r'D:\Code\0-data\1-齿轮检测数据集\青山数据集\VOCdevkit\VOC2012\Annotations.txt'  # 输入文件：包含所有图片名称（不带后缀）
    train_txt = r'D:\Code\0-data\1-齿轮检测数据集\青山数据集\VOCdevkit\VOC2012\train.txt'  # 输出文件：训练集图片名称
    val_txt = r'D:\Code\0-data\1-齿轮检测数据集\青山数据集\VOCdevkit\VOC2012\val.txt'  # 输出文件：验证集图片名称

    # 设置随机种子确保可重复性
    random.seed(0)

    # 执行划分
    result = split_images_by_category(input_txt, train_txt, val_txt)

    # 打印类别划分详情
    print("\n=== 训练集类别 ===")
    print(", ".join(sorted(result["train_categories"])))

    print("\n=== 验证集类别 ===")
    print(", ".join(sorted(result["val_categories"])))
