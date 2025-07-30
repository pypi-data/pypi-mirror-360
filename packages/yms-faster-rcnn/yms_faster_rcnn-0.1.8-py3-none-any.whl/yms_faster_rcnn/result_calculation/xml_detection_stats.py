import os
import argparse


def calculate_defect_stats(defect_txt_path, all_txt_path, result_xml_folder):
    """
    计算缺陷检测的检出、漏检、误检数量及相应比率

    参数:
        defect_txt_path: 包含有缺陷图片xml名(无后缀)的txt文件路径
        all_txt_path: 包含所有检测图片名(无后缀)的txt文件路径
        result_xml_folder: 存放检测结果xml文件的文件夹路径

    返回:
        包含各项统计结果的字典
    """
    # 读取有缺陷的图片名称列表
    with open(defect_txt_path, 'r', encoding='utf-8') as f:
        defect_names = [line.strip() for line in f if line.strip()]
    total_defects = len(defect_names)  # 总缺陷数量

    # 读取所有检测图片的名称列表
    with open(all_txt_path, 'r', encoding='utf-8') as f:
        all_names = [line.strip() for line in f if line.strip()]
    total_images = len(all_names)  # 总图片数量
    normal_images = total_images - total_defects # 正常图片数量

    # 获取检测结果文件夹中所有xml文件的名称(无后缀)
    # xml_files = [f for f in os.listdir(result_xml_folder) if f.endswith('.xml')]
    # result_names = [os.path.splitext(f)[0] for f in xml_files]
    with open(result_xml_folder, 'r', encoding='utf-8') as f:
        result_names = [line.strip() for line in f if line.strip()]
    total_results = len(result_names)  # 总检测结果数量

    # 计算各项指标
    detected = 0  # 检出数量：缺陷标注中有且检测结果中有
    for name in defect_names:
        if name in result_names:
            detected += 1

    missed = total_defects - detected  # 漏检数量：缺陷标注中有但检测结果中没有
    false_positive = 0  # 误检数量：缺陷标注中没有但检测结果中有

    for name in result_names:
        if name not in defect_names:
            false_positive += 1

    # 计算比率(处理除以零的情况)
    detection_rate = detected / total_defects if total_defects > 0 else 0.0
    miss_rate = missed / total_defects if total_defects > 0 else 0.0
    # 误检率：误检数量除以总总检测结果数量
    false_positive_rate = false_positive / normal_images if normal_images > 0 else 0.0

    return {
        'total_images': total_images,  # 总图片数量
        'total_defects': total_defects,  # 总缺陷数量
        'total_results': total_results,  # 总检测结果数量
        'normal_images': normal_images, # 正常图片的数量
        'detected': detected,  # 检出数量
        'missed': missed,  # 漏检数量
        'false_positive': false_positive,  # 误检数量
        'detection_rate': detection_rate,  # 检出率
        'miss_rate': miss_rate,  # 漏检率
        'false_positive_rate': false_positive_rate  # 误检率
    }


def print_and_save_stats(stats, output_file):
    """打印统计结果并保存到txt文件"""
    # 构建输出内容
    lines = [
        "=" * 60,
        "缺陷缺陷检测结果统计:",
        f"总图片数量: {stats['total_images']}",
        f"正常图片数量: {stats['normal_images']}",
        f"总缺陷陷图片数量: {stats['total_defects']}",
        f"总检测结果数量: {stats['total_results']}",
        "-" * 60,
        f"检出数量: {stats['detected']}",
        f"漏检数量: {stats['missed']}",
        f"误检数量: {stats['false_positive']}",
        "-" * 60,
        f"检出率: {stats['detection_rate']:.2%}",
        f"漏检率: {stats['miss_rate']:.2%}",
        f"误检率: {stats['false_positive_rate']:.2%}",
        "=" * 60
    ]

    # 打印到控制台
    for line in lines:
        print(line)

    # 保存到文件
    with open(output_file, 'w', encoding='utf-8') as f:
        for line in lines:
            f.write(line + '\n')
    print(f"\n统计结果已保存至: {output_file}")


def get_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='计算缺陷检测结果的检出、漏检、误检统计')
    parser.add_argument('--defect_txt', type=str,
                        default=r'F:\代码\dataset\VOCdevkit\VOC2012\有缺陷验证集.txt',
                        help='包含有缺陷图片xml名(无后缀)的txt文件路径')
    parser.add_argument('--all_txt', type=str,
                        default=r'F:\代码\dataset\VOCdevkit\VOC2012\ImageSets\Main\val.txt',
                        help='包含所有检测图片名(无后缀)的txt文件路径')
    parser.add_argument('--result_folder', type=str,
                        default=r'F:\代码\结果\第四次\检测结果.txt',
                        help='存放检测结果xml文件的文件夹路径')
    parser.add_argument('--output_file', type=str,
                        default=r'F:\代码\结果\第四次\统计结果.txt',
                        help='统计结果输出的txt文件路径')
    return parser.parse_args()


def main():
    args = get_args()

    # 验证文件和文件夹是否存在
    if not os.path.exists(args.defect_txt):
        print(f"错误: 缺陷标注txt文件 {args.defect_txt} 不存在!")
        return

    if not os.path.exists(args.all_txt):
        print(f"错误: 总图片文件 {args.all_txt} 不存在!")
        return

    if not os.path.exists(args.result_folder):
        print(f"错误: 检测结果文件夹 {args.result_folder} 不存在!")
        return

    # 创建输出目录（如果不存在）
    output_dir = os.path.dirname(args.output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    # 计算并打印统计结果
    stats = calculate_defect_stats(args.defect_txt, args.all_txt, args.result_folder)
    print_and_save_stats(stats, args.output_file)


if __name__ == "__main__":
    main()
