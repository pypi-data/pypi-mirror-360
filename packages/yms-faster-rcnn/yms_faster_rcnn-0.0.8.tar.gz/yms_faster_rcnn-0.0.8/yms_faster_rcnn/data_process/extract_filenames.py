import os
import argparse
import re


def natural_sort_key(s):
    """自然排序键生成函数，用于正确排序包含数字的字符串"""
    # 将字符串分割为数字和非数字部分
    return [int(text) if text.isdigit() else text.lower() for text in re.split('(\d+)', s)]


def extract_sorted_filenames(folder_path, output_txt):
    """
    读取文件夹内所有文件的文件名（不含后缀），按名称递增排序后写入txt文件

    参数:
        folder_path: 要读取的文件夹路径
        output_txt: 输出的txt文件路径
    """
    # 验证文件夹是否存在
    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"文件夹不存在: {folder_path}")

    # 获取文件夹内所有文件（不包括子文件夹）
    filenames = []
    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        # 只处理文件，跳过子文件夹
        if os.path.isfile(item_path):
            # 去除文件后缀，只保留文件名
            filename_without_ext = os.path.splitext(item)[0]
            filenames.append(filename_without_ext)

    # 按名称递增排序（支持包含数字的自然排序）
    filenames_sorted = sorted(filenames, key=natural_sort_key)

    # 创建输出目录（如果不存在）
    output_dir = os.path.dirname(output_txt)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    # 将排序后的文件名写入txt文件
    with open(output_txt, 'w', encoding='utf-8') as f:
        for name in filenames_sorted:
            f.write(name + '\n')

    print(f"成功提取并排序 {len(filenames_sorted)} 个文件名到: {output_txt}")


def get_args():
    """解析    解析命令行参数
    """
    parser = argparse.ArgumentParser(description='提取文件夹内文件名（不含后缀）到txt文件')
    parser.add_argument('--folder', type=str,
                        default=r'D:\Code\0-data\1-齿轮检测数据集\青山数据集\VOCdevkit\VOC2012\Annotations',
                        help='要读取的文件夹路径')
    parser.add_argument('--output', type=str,
                        default=r'D:\Code\0-data\1-齿轮检测数据集\青山数据集\VOCdevkit\VOC2012\Annotations.txt',
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
