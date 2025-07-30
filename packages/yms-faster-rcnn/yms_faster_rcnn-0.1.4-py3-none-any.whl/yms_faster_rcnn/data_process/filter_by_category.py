import argparse
from yms_faster_rcnn.data_process.util import natural_sort_key, extract_category, read_lines, write_lines  # 导入工具函数


def filter_files_by_category(category_txt, input_txt, output_txt):
    """
    根据类别txt文件，筛选出输入txt中属于这些类别的文件名称
    """
    # 读取类别列表
    categories = set(read_lines(category_txt))

    # 读取所有文件名称
    all_names = read_lines(input_txt)

    # 筛选属于目标类别的文件
    matched_files = [
        name for name in all_names
        if extract_category(name) in categories
    ]

    # 按自然顺序排序
    matched_files_sorted = sorted(matched_files, key=natural_sort_key)

    # 写入筛选结果
    write_lines(output_txt, matched_files_sorted)

    # 输出统计信息
    print(f"筛选完成！")
    print(f"总文件数量: {len(all_names)}")
    print(f"匹配到的文件数量: {len(matched_files_sorted)}")
    print(f"结果已保存至: {output_txt}")


def get_args():
    """解析命令行参数，包含默认路径"""
    parser = argparse.ArgumentParser(description='根据类别筛选文件并输出')
    parser.add_argument('--categories', type=str,
                        default=r'D:\Code\0-data\1-齿轮检测数据集\青山数据集\VOCdevkit\VOC2012\验证集类别.txt',
                        help='包含类别列表的txt文件路径')
    parser.add_argument('--input', type=str,
                        default=r'D:\Code\0-data\1-齿轮检测数据集\青山数据集\VOCdevkit\VOC2012\JPEGImages.txt',
                        help='包含所有文件名称的txt文件路径')
    parser.add_argument('--output', type=str,
                        default=r'D:\Code\0-data\1-齿轮检测数据集\青山数据集\VOCdevkit\VOC2012\ImageSets\Main\val.txt',
                        help='输出筛选结果的txt文件路径')
    return parser.parse_args()


def main():
    args = get_args()
    filter_files_by_category(args.categories, args.input, args.output)


if __name__ == "__main__":
    main()