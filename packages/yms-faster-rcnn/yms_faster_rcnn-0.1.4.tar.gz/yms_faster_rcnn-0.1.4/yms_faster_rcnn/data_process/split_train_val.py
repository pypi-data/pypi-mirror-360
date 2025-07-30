import os
import argparse
from yms_faster_rcnn.data_process.util import read_lines, write_lines, split_by_category, extract_category  # 导入工具函数


def split_images_by_category(input_txt, train_txt, val_txt, train_ratio=0.7, seed=0):
    # 读取输入文件中的所有图片名称
    image_names = read_lines(input_txt)

    # 按类别划分训练集和验证集
    train_set, val_set, category_groups = split_by_category(
        image_names,
        train_ratio=train_ratio,
        seed=seed
    )

    # 计算统计信息
    total_images = len(image_names)
    total_categories = len(category_groups)
    train_categories = {extract_category(name) for name in train_set}
    val_categories = {extract_category(name) for name in val_set}

    print(f"总类别数: {total_categories}, 总图片数: {total_images}")

    # 计算最终比例
    actual_ratio = len(train_set) / total_images
    print(f"\n训练集: {len(train_set)} 张图片 ({len(train_categories)} 个类别)")
    print(f"验证集: {len(val_set)} 张图片 ({len(val_categories)} 个类别)")
    print(f"实际分割比例: 训练集 {actual_ratio:.2%}, 验证集 {1 - actual_ratio:.2%}")

    # 写入训练集和验证集文件
    write_lines(train_txt, train_set)
    write_lines(val_txt, val_set)

    # 返回划分结果
    return {
        "train_count": len(train_set),
        "val_count": len(val_set),
        "train_categories": sorted(train_categories),
        "val_categories": sorted(val_categories)
    }


if __name__ == "__main__":
    input_txt = r'D:\Code\0-data\1-齿轮检测数据集\青山数据集\VOCdevkit\VOC2012\Annotations.txt'
    train_txt = r'D:\Code\0-data\1-齿轮检测数据集\青山数据集\VOCdevkit\VOC2012\有缺陷的训练集.txt'
    val_txt = r'D:\Code\0-data\1-齿轮检测数据集\青山数据集\VOCdevkit\VOC2012\有缺陷验证集.txt'

    # 执行划分
    result = split_images_by_category(input_txt, train_txt, val_txt, seed=0)

    # 打印类别划分详情
    print("\n=== 训练集类别 ===")
    print(", ".join(result["train_categories"]))

    print("\n=== 验证集类别 ===")
    print(", ".join(result["val_categories"]))