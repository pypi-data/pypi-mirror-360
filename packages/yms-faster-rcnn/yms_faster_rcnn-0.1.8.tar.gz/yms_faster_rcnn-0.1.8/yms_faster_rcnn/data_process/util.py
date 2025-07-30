# data_process/utils.py
import os
import random
import re
from collections import defaultdict


def natural_sort_key(s):
    """自然排序键生成函数，正确处理包含数字的字符串"""
    return [int(text) if text.isdigit() else text.lower() for text in re.split('(\d+)', s)]


def extract_category(name):
    """从文件名称中提取类别（假设格式为xxx_num）"""
    pattern = re.compile(r'^(.+)_\d+$')
    match = pattern.match(name)
    if match:
        return match.group(1)
    return name  # 如果不符合格式，将整个名称作为类别


def ensure_dir_exists(file_path):
    """确保文件所在目录存在，不存在则创建"""
    output_dir = os.path.dirname(file_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)


def read_lines(file_path):
    """读取文件内容，返回非空行的列表（已去除首尾空白）"""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"文件不存在: {file_path}")

    with open(file_path, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]


def write_lines(file_path, lines):
    """将列表内容写入文件，每行一个元素"""
    ensure_dir_exists(file_path)
    with open(file_path, 'w', encoding='utf-8') as f:
        for line in lines:
            f.write(line + '\n')


def group_by_category(names):
    """按类别分组文件名称"""
    category_groups = defaultdict(list)
    for name in names:
        category = extract_category(name)
        category_groups[category].append(name)
    return category_groups


def get_filenames_without_ext(folder_path):
    """获取文件夹内所有文件的文件名（不带后缀）"""
    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"文件夹不存在: {folder_path}")

    filenames = []
    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        if os.path.isfile(item_path):
            # 去除文件后缀，只保留文件名
            filename_without_ext = os.path.splitext(item)[0]
            filenames.append(filename_without_ext)
    return filenames


def split_by_category(names, train_ratio=0.7, seed=None):
    """
    按类别比例划分训练集和验证集
    """
    if seed is not None:
        random.seed(seed)

    # 按类别分组
    category_groups = group_by_category(names)

    # 随机排序类别
    categories = list(category_groups.keys())
    random.shuffle(categories)

    # 计算目标大小
    total = len(names)
    target_train_size = int(total * train_ratio)

    # 分配数据
    train_set = []
    val_set = []
    train_count = 0

    for category in categories:
        items = category_groups[category]
        items_count = len(items)

        if train_count + items_count <= target_train_size:
            train_set.extend(items)
            train_count += items_count
        else:
            val_set.extend(items)

    return train_set, val_set, category_groups