from PIL.Image import Image, fromarray
import PIL.ImageDraw as ImageDraw
import PIL.ImageFont as ImageFont
from PIL import ImageColor
import numpy as np
from typing import List, Optional, Dict, Tuple

STANDARD_COLORS = [
    'AliceBlue', 'Chartreuse', 'Aqua', 'Aquamarine', 'Azure', 'Beige', 'Bisque',
    'BlanchedAlmond', 'BlueViolet', 'BurlyWood', 'CadetBlue', 'AntiqueWhite',
    'Chocolate', 'Coral', 'CornflowerBlue', 'Cornsilk', 'Crimson', 'Cyan',
    'DarkCyan', 'DarkGoldenRod', 'DarkGrey', 'DarkKhaki', 'DarkOrange',
    'DarkOrchid', 'DarkSalmon', 'DarkSeaGreen', 'DarkTurquoise', 'DarkViolet',
    'DeepPink', 'DeepSkyBlue', 'DodgerBlue', 'FireBrick', 'FloralWhite',
    'ForestGreen', 'Fuchsia', 'Gainsboro', 'GhostWhite', 'Gold', 'GoldenRod',
    'Salmon', 'Tan', 'HoneyDew', 'HotPink', 'IndianRed', 'Ivory', 'Khaki',
    'Lavender', 'LavenderBlush', 'LawnGreen', 'LemonChiffon', 'LightBlue',
    'LightCoral', 'LightCyan', 'LightGoldenRodYellow', 'LightGray', 'LightGrey',
    'LightGreen', 'LightPink', 'LightSalmon', 'LightSeaGreen', 'LightSkyBlue',
    'LightSlateGray', 'LightSlateGrey', 'LightSteelBlue', 'LightYellow', 'Lime',
    'LimeGreen', 'Linen', 'Magenta', 'MediumAquaMarine', 'MediumOrchid',
    'MediumPurple', 'MediumSeaGreen', 'MediumSlateBlue', 'MediumSpringGreen',
    'MediumTurquoise', 'MediumVioletRed', 'MintCream', 'MistyRose', 'Moccasin',
    'NavajoWhite', 'OldLace', 'Olive', 'OliveDrab', 'Orange', 'OrangeRed',
    'Orchid', 'PaleGoldenRod', 'PaleGreen', 'PaleTurquoise', 'PaleVioletRed',
    'PapayaWhip', 'PeachPuff', 'Peru', 'Pink', 'Plum', 'PowderBlue', 'Purple',
    'Red', 'RosyBrown', 'RoyalBlue', 'SaddleBrown', 'Green', 'SandyBrown',
    'SeaGreen', 'SeaShell', 'Sienna', 'Silver', 'SkyBlue', 'SlateBlue',
    'SlateGray', 'SlateGrey', 'Snow', 'SpringGreen', 'SteelBlue', 'GreenYellow',
    'Teal', 'Thistle', 'Tomato', 'Turquoise', 'Violet', 'Wheat', 'White',
    'WhiteSmoke', 'Yellow', 'YellowGreen'
]


def draw_text(draw: ImageDraw.ImageDraw,
              box: list,
              cls: int,
              score: float,
              category_index: dict,
              color: Tuple[int, int, int],  # 改为RGB元组格式
              font: str = 'arial.ttf',
              font_size: int = 24) -> None:
    """将目标边界框和类别信息绘制到图片上"""
    try:
        font_obj = ImageFont.truetype(font, font_size)
    except IOError as e:
        print("Error loading font:", e)
        font_obj = ImageFont.load_default()

    left, top, right, bottom = box
    display_str = f"{category_index[str(cls)]}: {int(100 * score)}%"

    # 计算文本高度
    bbox = font_obj.getbbox(display_str)
    text_height = bbox[3] - bbox[1]
    display_str_height = text_height * 1.1  # 包含10%边距

    # 确定文本位置
    if top > display_str_height:
        text_top = top - display_str_height
        text_bottom = top
    else:
        text_top = bottom
        text_bottom = bottom + display_str_height

    # 绘制文本背景和文本
    text_width = bbox[2] - bbox[0]
    margin = int(text_width * 0.05)
    draw.rectangle(
        [(left, text_top), (left + text_width + 2 * margin, text_bottom)],
        fill=color  # 使用RGB元组
    )
    draw.text(
        (left + margin, text_top),
        display_str,
        fill=(0, 0, 0),  # 黑色文本
        font=font_obj
    )


def draw_masks(image: Image,
               masks: np.ndarray,
               colors: List[Tuple[int, int, int]],  # RGB元组列表
               thresh: float = 0.7,
               alpha: float = 0.5) -> Image:
    np_image = np.array(image)
    masks = np.where(masks > thresh, True, False)
    img_to_draw = np.copy(np_image)

    for mask, color in zip(masks, colors):
        img_to_draw[mask] = color  # 直接使用RGB元组

    out = np_image * (1 - alpha) + img_to_draw * alpha
    return fromarray(out.astype(np.uint8))


def _get_colors(classes: np.ndarray) -> Tuple[List[Tuple[int, int, int]], List[int]]:
    """获取两种格式的颜色：RGB元组(用于填充)和整数(用于线条)"""
    rgb_colors = []
    int_colors = []
    for cls in classes:
        color_name = STANDARD_COLORS[cls % len(STANDARD_COLORS)]
        r, g, b = ImageColor.getrgb(color_name)
        rgb_colors.append((r, g, b))
        int_colors.append(int(r) << 16 | int(g) << 8 | int(b))  # 转换为整数格式
    return rgb_colors, int_colors


def draw_objs(image: Image,
              boxes: Optional[np.ndarray] = None,
              classes: Optional[np.ndarray] = None,
              scores: Optional[np.ndarray] = None,
              masks: Optional[np.ndarray] = None,
              category_index: Optional[dict] = None,
              box_thresh: float = 0.1,
              mask_thresh: float = 0.5,
              line_thickness: int = 8,
              font: str = 'arial.ttf',
              font_size: int = 24,
              draw_boxes_on_image: bool = True,
              draw_masks_on_image: bool = False) -> Image:
    """将目标边界框、类别信息、mask信息绘制在图片上"""
    # 验证必要参数
    if boxes is None or classes is None or scores is None or category_index is None:
        return image.copy()

    # 过滤低概率目标
    idxs = np.greater(scores, box_thresh)
    boxes = boxes[idxs]
    classes = classes[idxs]
    scores = scores[idxs]
    masks = masks[idxs] if masks is not None else None

    if len(boxes) == 0:
        return image.copy()

    # 获取两种格式的颜色
    rgb_colors, int_colors = _get_colors(classes)
    draw = ImageDraw.Draw(image)

    if draw_boxes_on_image:
        for box, cls, score, rgb_color, int_color in zip(boxes, classes, scores, rgb_colors, int_colors):
            left, top, right, bottom = box
            # 绘制边界框(使用整数格式颜色)
            draw.line(
                [(left, top), (left, bottom), (right, bottom), (right, top), (left, top)],
                width=line_thickness,
                fill=int_color  # 修复：使用整数格式颜色
            )
            # 绘制文本(使用RGB元组颜色)
            draw_text(draw, box.tolist(), int(cls), float(score), category_index, rgb_color, font, font_size)

    if draw_masks_on_image and masks is not None:
        image = draw_masks(image, masks, rgb_colors, mask_thresh)

    return image


def my_draw_objs(image: Image,
                 boxes: Optional[np.ndarray] = None,
                 classes: Optional[np.ndarray] = None,
                 scores: Optional[np.ndarray] = None,
                 masks: Optional[np.ndarray] = None,
                 category_index: Optional[dict] = None,
                 box_thresh: float = 0.1,
                 mask_thresh: float = 0.5,
                 line_thickness: int = 8,
                 font: str = 'arial.ttf',
                 font_size: int = 24,
                 image_name: Optional[str] = None,
                 draw_boxes_on_image: bool = True,
                 draw_masks_on_image: bool = False) -> Image:
    """带图像名称的绘制函数"""
    # 复用draw_objs的核心逻辑
    image = draw_objs(
        image, boxes, classes, scores, masks, category_index,
        box_thresh, mask_thresh, line_thickness, font, font_size,
        draw_boxes_on_image, draw_masks_on_image
    )

    # 绘制图像名称
    if image_name:
        draw = ImageDraw.Draw(image)
        try:
            name_font = ImageFont.truetype(font, 40)
        except IOError:
            name_font = ImageFont.load_default()
        draw.text((10, 20), image_name, fill=0x00FF00, font=name_font)

    return image