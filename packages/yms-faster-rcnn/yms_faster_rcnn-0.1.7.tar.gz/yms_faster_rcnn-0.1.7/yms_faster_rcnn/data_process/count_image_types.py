import os
import argparse
import re
from collections import defaultdict


def natural_sort_key(s):
    """自然排序键生成函数，正确处理包含数字的字符串"""
    return [int(text) if text.isdigit() else text.lower() for text in re.split('(\d+)', s)]


def count_file_types(folder_path):
    """
    统计文件夹中文件类型及每种类型的数量
    格式要求：xxx_num.任意后缀（xxx可包含数字和字符）
    """
    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"文件夹不存在: {folder_path}")

    # 正则表达式匹配 xxx_num.任意后缀 格式
    pattern = re.compile(r'^(.+)_\d+\..*$', re.IGNORECASE)

    # 存储每种类型的文件数量
    type_counts = defaultdict(int)
    total_files = 0  # 总文件数（不含子文件夹）
    matched_files = 0  # 匹配格式的文件数
    unmatched_files = []  # 不匹配格式的文件列表

    # 遍历文件夹
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isdir(file_path):  # 跳过子文件夹
            continue

        total_files += 1
        match = pattern.match(filename)

        if match:
            type_prefix = match.group(1).strip()
            type_counts[type_prefix] += 1
            matched_files += 1
        else:
            unmatched_files.append(filename)

    # 按自然排序对类型进行排序（支持数字正确排序）
    sorted_types = sorted(type_counts.items(), key=lambda x: natural_sort_key(x[0]))

    return {
        'total_types': len(type_counts),
        'type_details': dict(sorted_types),  # 每种类型的数量（已排序）
        'total_files': total_files,
        'matched_files': matched_files,
        'unmatched_files': unmatched_files
    }


def print_results(results):
    """打印统计结果"""
    print("=" * 80)
    print("文件类型统计结果 summary:")
    print(f"总文件数: {results['total_files']}")
    print(f"匹配格式文件数: {results['matched_files']}")
    print(f"总类型数: {results['total_types']}")
    print("-" * 80)
    print(f"{'类型前缀':<40} 数量")
    print("-" * 80)
    for type_name, count in results['type_details'].items():
        print(f"{type_name:<40} {count}")

    if results['unmatched_files']:
        print("-" * 80)
        print(f"不匹配格式的文件 ({len(results['unmatched_files'])} 个):")
        for filename in results['unmatched_files'][:5]:
            print(f"  - {filename}")
        if len(results['unmatched_files']) > 5:
            print(f"  ... 还有 {len(results['unmatched_files']) - 5} 个文件")
    print("=" * 80)


def export_results(results, output_file):
    """将统计结果导出到文本文件"""
    # 确保输出目录存在
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("文件类型统计结果\n")
        f.write(f"总文件数: {results['total_files']}\n")
        f.write(f"匹配格式文件数: {results['matched_files']}\n")
        f.write(f"总类型数: {results['total_types']}\n")
        f.write("-" * 80 + "\n")
        f.write(f"{'类型前缀':<40} 数量\n")
        f.write("-" * 80 + "\n")
        # 写入已排序的类型
        for type_name, count in results['type_details'].items():
            f.write(f"{type_name:<40} {count}\n")
        f.write("=" * 80 + "\n")
    print(f"\n统计结果已导出至: {output_file}")


def get_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='统计任意类型文件的数字字符混合前缀类型数量（格式：xxx_num.任意后缀）')
    parser.add_argument('--folder', type=str,
                        default=r'D:\Code\0-data\0-故障诊断结果输出\青山数据集输出\第一次结果',
                        help='包含文件的文件夹路径')
    parser.add_argument('--export', type=str,
                        help='导出结果到指定文本文件（可选）')
    return parser.parse_args()


def main():
    args = get_args()
    try:
        results = count_file_types(args.folder)
        print_results(results)

        # 导出结果（如果指定了导出文件）
        if args.export:
            export_results(results, args.export)

    except Exception as e:
        print(f"错误: {str(e)}")


if __name__ == "__main__":
    main()
