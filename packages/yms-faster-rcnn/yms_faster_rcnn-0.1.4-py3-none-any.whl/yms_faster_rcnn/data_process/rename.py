import re
from pathlib import Path


def rename_files(folder_path, old_xxx, new_xxx, extension=None):
    """
    重命名指定文件夹中特定xxx的文件，支持任意后缀

    参数:
        folder_path: 文件夹路径
        old_xxx: 需要替换的旧类别名
        new_xxx: 新的类别名
        extension: 可选参数，指定文件后缀(如'bmp'、'jpg')，不指定则处理所有类型
    """
    # 转换为Path对象以便于处理
    folder = Path(folder_path)

    # 检查文件夹是否存在
    if not folder.exists() or not folder.is_dir():
        print(f"错误: 文件夹 {folder_path} 不存在或不是有效目录")
        return

    # 构建文件匹配模式
    if extension:
        # 确保扩展名前有.
        if not extension.startswith('.'):
            extension = f'.{extension}'
        # 匹配指定后缀的文件
        file_pattern = f'*{extension}'
    else:
        # 匹配所有文件
        file_pattern = '*'

    # 构建正则表达式模式: xxx_num.后缀
    # 处理可能包含特殊字符的扩展名
    if extension:
        ext_pattern = re.escape(extension)
    else:
        ext_pattern = r'\.[^.]+$'  # 匹配任意后缀

    pattern = re.compile(rf'^{re.escape(old_xxx)}_(\d+){ext_pattern}$')

    # 统计找到的文件数和重命名的文件数
    found_count = 0
    renamed_count = 0

    # 遍历文件夹中符合条件的文件
    for file_path in folder.glob(file_pattern):
        # 跳过目录，只处理文件
        if file_path.is_dir():
            continue

        file_name = file_path.name

        # 尝试匹配文件名模式
        match = pattern.match(file_name)
        if match:
            found_count += 1
            num = match.group(1)
            # 获取文件后缀
            file_ext = file_path.suffix

            # 生成新的文件名
            new_file_name = f"{new_xxx}_{num}{file_ext}"
            new_file_path = file_path.with_name(new_file_name)

            # 避免文件名相同导致的错误
            if new_file_path == file_path:
                print(f"跳过: 新文件名与原文件名相同 - {file_name}")
                continue

            # 执行重命名
            try:
                file_path.rename(new_file_path)
                renamed_count += 1
                print(f"已重命名: {file_name} -> {new_file_name}")
            except Exception as e:
                print(f"重命名 {file_name} 时出错: {e}")

    # 显示统计结果
    print(f"\n处理完成:")
    print(f"找到符合条件的文件: {found_count} 个")
    print(f"成功重命名的文件: {renamed_count} 个")
    if found_count > renamed_count:
        print(f"警告: 有 {found_count - renamed_count} 个文件重命名失败")


if __name__ == "__main__":
    # 直接在这里指定参数
    folder_path = r"D:\Code\0-data\1-齿轮检测数据集\青山数据集\VOCdevkit\VOC2012\Annotations"
    old_xxx = "SE210179-2()-"
    new_xxx = "SE210179-2()"
    target_extension = None

    print("文件批量重命名工具")
    print("------------------")
    print(f"文件夹路径: {folder_path}")
    print(f"旧类别名: {old_xxx}")
    print(f"新类别名: {new_xxx}")
    print(f"处理的文件类型: {'所有类型' if target_extension is None else target_extension}")

    rename_files(folder_path, old_xxx, new_xxx, target_extension)