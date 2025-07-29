import os
import argparse
import re


def natural_sort_key(s):
    """自然排序键生成函数，用于正确排序包含数字的字符串"""
    return [int(text) if text.isdigit() else text.lower() for text in re.split('(\d+)', s)]


def extract_category(name):
    """从图片名称中提取类别（假设格式为xxx_num）"""
    pattern = re.compile(r'^(.+)_\d+$')
    match = pattern.match(name)
    if match:
        return match.group(1)
    return name  # 如果不符合格式，将整个名称作为类别


def get_image_categories(input_txt, output_txt):
    """
    从名称txt文件中提取图片类别，并输出到txt文件

    参数:
        input_txt: 包含图片名称的txt文件路径
        output_txt: 输出类别列表的txt文件路径
    """
    # 读取图片名称
    with open(input_txt, 'r', encoding='utf-8') as f:
        image_names = [line.strip() for line in f if line.strip()]

    # 提取类别
    categories = set()
    for name in image_names:
        category = extract_category(name)
        categories.add(category)

    # 按自然排序
    sorted_categories = sorted(categories, key=natural_sort_key)

    # 创建输出目录（如果不存在）
    output_dir = os.path.dirname(output_txt)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    # 写入类别到txt文件
    with open(output_txt, 'w', encoding='utf-8') as f:
        for category in sorted_categories:
            f.write(category + '\n')

    print(f"提取完成！")
    print(f"共发现 {len(sorted_categories)} 种图片类别")
    print(f"类别列表已保存至: {output_txt}")


def get_args():
    """解析命令行参数，包含默认路径"""
    parser = argparse.ArgumentParser(description='从名称txt文件中提取图片类别并输出')
    parser.add_argument('--input', type=str,
                        default=r'D:\Code\0-data\1-齿轮检测数据集\青山数据集\VOCdevkit\VOC2012\no_annotated_categories.txt',
                        help='包含图片名称的txt文件路径（默认：./image_names.txt）')
    parser.add_argument('--output', type=str,
                        default=r'D:\Code\0-data\1-齿轮检测数据集\青山数据集\VOCdevkit\VOC2012\正常图片类别.txt',
                        help='输出类别列表的txt文件路径（默认：./image_categories.txt）')
    return parser.parse_args()


def main():
    args = get_args()

    # 验证输入文件是否存在
    if not os.path.exists(args.input):
        print(f"错误: 输入文件 {args.input} 不存在!")
        return

    get_image_categories(args.input, args.output)


if __name__ == "__main__":
    main()
