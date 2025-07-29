import os
import argparse
import re



def natural_sort_key(s):
    """自然排序键生成函数，正确处理包含数字的字符串"""
    return [int(text) if text.isdigit() else text.lower() for text in re.split('(\d+)', s)]


def extract_category(name):
    """从图片名称中提取类别（假设格式为xxx_num）"""
    pattern = re.compile(r'^(.+)_\d+$')
    match = pattern.match(name)
    if match:
        return match.group(1)
    return name  # 如果不符合格式，将整个名称作为类别


def separate_by_annotated_categories(annotated_txt, all_txt, has_annotated_txt, no_annotated_txt):
    """
    分离有标注类别和无标注类别的图片名称，并按名称递增排序

    参数:
        annotated_txt: 有标注的图片名称txt文件路径
        all_txt: 全部图片名称txt文件路径
        has_annotated_txt: 有标注类别图片输出txt路径
        no_annotated_txt: 无标注类别图片输出txt路径
    """
    # 读取有标注的图片名称并提取其类别
    with open(annotated_txt, 'r', encoding='utf-8') as f:
        annotated_names = [line.strip() for line in f if line.strip()]

    annotated_categories = set()
    for name in annotated_names:
        category = extract_category(name)
        annotated_categories.add(category)

    # 读取所有图片名称
    with open(all_txt, 'r', encoding='utf-8') as f:
        all_names = [line.strip() for line in f if line.strip()]

    # 分离有标注类别和无标注类别的图片
    has_annotated = []
    no_annotated = []

    for name in all_names:
        category = extract_category(name)
        if category in annotated_categories:
            has_annotated.append(name)
        else:
            no_annotated.append(name)

    # 按名称递增排序（自然排序）
    has_annotated_sorted = sorted(has_annotated, key=natural_sort_key)
    no_annotated_sorted = sorted(no_annotated, key=natural_sort_key)

    # 创建输出目录（如果不存在）
    for output_path in [has_annotated_txt, no_annotated_txt]:
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

    # 写入有标注类别的图片名称
    with open(has_annotated_txt, 'w', encoding='utf-8') as f:
        for name in has_annotated_sorted:
            f.write(name + '\n')

    # 写入无标注类别的图片名称
    with open(no_annotated_txt, 'w', encoding='utf-8') as f:
        for name in no_annotated_sorted:
            f.write(name + '\n')

    # 输出统计信息
    total = len(all_names)
    print(f"处理完成！")
    print(f"总图片数量: {total}")
    print(f"有标注类别的图片数量: {len(has_annotated_sorted)} ({len(has_annotated_sorted) / total:.2%})")
    print(f"无标注类别的图片数量: {len(no_annotated_sorted)} ({len(no_annotated_sorted) / total:.2%})")
    print(f"有标注类别图片已保存至: {has_annotated_txt}")
    print(f"无标注类别图片已保存至: {no_annotated_txt}")


def get_args():
    """解析命令行参数，包含默认路径"""
    parser = argparse.ArgumentParser(description='分离有标注类别和无标注类别的图片名称（按名称排序）')
    parser.add_argument('--annotated', type=str,
                        default=r'D:\Code\0-data\1-齿轮检测数据集\青山数据集\VOCdevkit\VOC2012\Annotations.txt',
                        help='有标注的图片名称txt文件路径（默认：./annotated_images.txt）')
    parser.add_argument('--all', type=str,
                        default=r'D:\Code\0-data\1-齿轮检测数据集\青山数据集\VOCdevkit\VOC2012\JPEGImages.txt',
                        help='全部图片名称txt文件路径（默认：./all_images.txt）')
    parser.add_argument('--has_output', type=str,
                        default=r'D:\Code\0-data\1-齿轮检测数据集\青山数据集\VOCdevkit\VOC2012/has_annotated_categories.txt',
                        help='有标注类别图片输出txt文件路径（默认：./has_annotated_categories.txt）')
    parser.add_argument('--no_output', type=str,
                        default=r'D:\Code\0-data\1-齿轮检测数据集\青山数据集\VOCdevkit\VOC2012/no_annotated_categories.txt',
                        help='无标注类别图片输出txt文件路径（默认：./no_annotated_categories.txt）')
    return parser.parse_args()


def main():
    args = get_args()

    # 验证输入文件是否存在
    if not os.path.exists(args.annotated):
        print(f"错误: 有标注图片文件 {args.annotated} 不存在!")
        return

    if not os.path.exists(args.all):
        print(f"错误: 全部图片文件 {args.all} 不存在!")
        return

    separate_by_annotated_categories(
        args.annotated,
        args.all,
        args.has_output,
        args.no_output
    )


if __name__ == "__main__":
    main()
