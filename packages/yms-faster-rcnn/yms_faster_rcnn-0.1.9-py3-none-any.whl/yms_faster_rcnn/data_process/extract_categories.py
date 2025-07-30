import argparse
from yms_faster_rcnn.data_process.util import read_lines, write_lines, extract_category, natural_sort_key  # 导入工具函数


def get_image_categories(input_txt, output_txt):
    """
    从名称txt文件中提取图片类别，并输出到txt文件
    """
    # 读取图片名称
    image_names = read_lines(input_txt)

    # 提取类别
    categories = set()
    for name in image_names:
        category = extract_category(name)
        categories.add(category)

    # 按自然排序
    sorted_categories = sorted(categories, key=natural_sort_key)

    # 写入类别到txt文件
    write_lines(output_txt, sorted_categories)

    print(f"提取完成！")
    print(f"共发现 {len(sorted_categories)} 种图片类别")
    print(f"类别列表已保存至: {output_txt}")


def get_args():
    """解析命令行参数，包含默认路径"""
    parser = argparse.ArgumentParser(description='从名称txt文件中提取图片类别并输出')
    parser.add_argument('--input', type=str,
                        default=r'F:\代码\结果\第一次训练结果\检测结果.txt',
                        help='包含图片名称的txt文件路径（默认：./image_names.txt）')
    parser.add_argument('--output', type=str,
                        default=r'F:\代码\结果\第一次训练结果\检出类别.txt',
                        help='输出类别列表的txt文件路径（默认：./image_categories.txt）')
    return parser.parse_args()


def main():
    args = get_args()
    get_image_categories(args.input, args.output)


if __name__ == "__main__":
    main()