import os
import argparse
import re


def natural_sort_key(s):
    """自然排序键生成函数，用于正确排序包含数字的字符串"""
    return [int(text) if text.isdigit() else text.lower() for text in re.split('(\d+)', s)]


def extract_category(name):
    """从文件名称中提取类别（假设格式为xxx_num_num）"""
    pattern = re.compile(r'^(.+)_\d+$')
    match = pattern.match(name)
    if match:
        return match.group(1)
    return name  # 如果不符合格式，将整个名称作为类别


def filter_files_by_category(category_txt, input_txt, output_txt):
    """
    根据类别txt文件，筛选出输入txt中属于这些类别的文件名称

    参数:
        category_txt: 包含类别列表的txt文件路径
        input_txt: 包含所有文件名称的txt文件路径
        output_txt: 输出筛选结果的txt文件路径
    """
    # 读取类别列表
    with open(category_txt, 'r', encoding='utf-8') as f:
        categories = {line.strip() for line in f if line.strip()}

    # 读取所有文件名称
    with open(input_txt, 'r', encoding='utf-8') as f:
        all_names = [line.strip() for line in f if line.strip()]

    # 筛选属于目标类别的文件
    matched_files = []
    for name in all_names:
        file_category = extract_category(name)
        if file_category in categories:
            matched_files.append(name)

    # 按自然顺序排序
    matched_files_sorted = sorted(matched_files, key=natural_sort_key)

    # 创建输出目录（如果不存在）
    output_dir = os.path.dirname(output_txt)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    # 写入筛选结果
    with open(output_txt, 'w', encoding='utf-8') as f:
        for name in matched_files_sorted:
            f.write(name + '\n')

    # 输出统计信息
    print(f"筛选完成！")
    print(f"总文件数量: {len(all_names)}")
    print(f"匹配到的文件数量: {len(matched_files_sorted)}")
    print(f"结果已保存至: {output_txt}")


def get_args():
    """解析命令行参数，包含默认路径"""
    parser = argparse.ArgumentParser(description='根据类别筛选文件并输出')
    parser.add_argument('--categories', type=str,
                        default=r'D:\Code\0-data\1-齿轮检测数据集\青山数据集\VOCdevkit\VOC2012\ImageSets\train_categories.txt',
                        help='包含类别列表的txt文件路径（默认：./categories.txt）')
    parser.add_argument('--input', type=str,
                        default=r'D:\Code\0-data\1-齿轮检测数据集\青山数据集\VOCdevkit\VOC2012\JPEGImages.txt',
                        help='包含所有文件名称的txt文件路径（默认：./all_files.txt）')
    parser.add_argument('--output', type=str,
                        default=r'D:\Code\0-data\1-齿轮检测数据集\青山数据集\VOCdevkit\VOC2012\ImageSets\Main\train.txt',
                        help='输出筛选结果的txt文件路径（默认：./matched_files.txt）')
    return parser.parse_args()


def main():
    args = get_args()

    # 验证输入文件是否存在
    if not os.path.exists(args.categories):
        print(f"错误: 类别文件 {args.categories} 不存在!")
        return

    if not os.path.exists(args.input):
        print(f"错误: 输入文件 {args.input} 不存在!")
        return

    filter_files_by_category(args.categories, args.input, args.output)


if __name__ == "__main__":
    main()
