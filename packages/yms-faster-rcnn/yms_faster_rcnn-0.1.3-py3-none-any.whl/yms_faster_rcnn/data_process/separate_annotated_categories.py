import argparse

from yms_faster_rcnn.data_process.util import read_lines, extract_category, natural_sort_key, write_lines


def separate_by_annotated_categories(annotated_txt, all_txt, has_annotated_txt, no_annotated_txt):
    """
    分离有标注类别和无标注类别的图片名称，并按名称递增排序
    """
    # 读取有标注的图片名称并提取其类别
    annotated_names = read_lines(annotated_txt)
    annotated_categories = {extract_category(name) for name in annotated_names}

    # 读取所有图片名称
    all_names = read_lines(all_txt)

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

    # 写入结果
    write_lines(has_annotated_txt, has_annotated_sorted)
    write_lines(no_annotated_txt, no_annotated_sorted)

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
                        default=r'D:\Code\0-data\1-齿轮检测数据集\青山数据集\VOCdevkit\VOC2012\has_annotated_categories.txt',
                        help='有标注类别图片输出txt文件路径')
    parser.add_argument('--no_output', type=str,
                        default=r'D:\Code\0-data\1-齿轮检测数据集\青山数据集\VOCdevkit\VOC2012\no_annotated_categories.txt',
                        help='无标注类别图片输出txt文件路径')
    return parser.parse_args()


def main():
    args = get_args()
    separate_by_annotated_categories(
        args.annotated,
        args.all,
        args.has_output,
        args.no_output
    )


if __name__ == "__main__":
    main()