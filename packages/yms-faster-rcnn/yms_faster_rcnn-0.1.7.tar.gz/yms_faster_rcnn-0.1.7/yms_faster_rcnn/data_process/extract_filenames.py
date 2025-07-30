import argparse
from yms_faster_rcnn.data_process.util import get_filenames_without_ext, natural_sort_key, write_lines  # 导入工具函数


def extract_sorted_filenames(folder_path, output_txt):
    """
    读取文件夹内所有文件的文件名（不含后缀），按名称递增排序后写入txt文件
    """
    # 获取文件名（不带后缀）
    filenames = get_filenames_without_ext(folder_path)

    # 按名称递增排序（支持包含数字的自然排序）
    filenames_sorted = sorted(filenames, key=natural_sort_key)

    # 将排序后的文件名写入txt文件
    write_lines(output_txt, filenames_sorted)
    print(f"成功提取并排序 {len(filenames_sorted)} 个文件名到: {output_txt}")


def get_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='提取文件夹内文件名（不含后缀）到txt文件')
    parser.add_argument('--folder', type=str,
                        default=r'F:\代码\结果\第二次\验证结果',
                        help='要读取的文件夹路径')
    parser.add_argument('--output', type=str,
                        default=r'F:\代码\结果\第二次\检测结果.txt',
                        help='输出的txt文件路径（例如：./filenames.txt）')
    return parser.parse_args()


def main():
    args = get_args()
    try:
        extract_sorted_filenames(args.folder, args.output)
    except Exception as e:
        print(f"发生错误: {str(e)}")


if __name__ == "__main__":
    main()