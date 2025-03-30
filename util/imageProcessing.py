import os
import mss
import mss.tools
from PIL import Image
import numpy as np

from PIL import Image
import os


def split_image(image_path='./temp/screenshot_binary.bmp', save_dir='./temp/split_images'):
    # 打开图片并转换为灰度图
    img = Image.open(image_path).convert('L')
    width, height = img.size

    # 寻找第一列满足连续15个白像素的列
    target_col = -1
    for col in range(width):
        consecutive = 0
        for row in range(height):
            if img.getpixel((col, row)) == 255:
                consecutive += 1
                if consecutive >= 15:
                    target_col = col
                    break
            else:
                consecutive = 0
        if target_col != -1:
            break

    if target_col == -1:
        print("未找到符合条件的列")
        return

    # 在目标列中查找所有连续白像素段（高度≥15）
    segments = []
    start = -1
    for row in range(height):
        pixel = img.getpixel((target_col, row))
        if pixel == 255:
            if start == -1:
                start = row
            # 检查是否到达底部或遇到黑像素
            if row == height-1 or img.getpixel((target_col, row+1)) != 255:
                if row - start + 1 >= 15:
                    segments.append((start, row))
                start = -1
        else:
            if start != -1:
                if (row-1) - start + 1 >= 15:
                    segments.append((start, row-1))
                start = -1

    # 创建保存目录
    os.makedirs(save_dir, exist_ok=True)

    # 处理每个小列段
    for idx, (s_row, e_row) in enumerate(segments):
        found_row = -1
        found_col_end = -1

        # 在行区间内查找首个符合条件的行
        for row in range(s_row, e_row + 1):
            consecutive = 0
            # 从target_col开始向右扫描
            for c in range(target_col, width):
                if img.getpixel((c, row)) == 255:
                    consecutive += 1
                    if consecutive >= 15:
                        found_col_end = c
                    # 继续循环直到遇到黑色像素
                else:
                    break  # 遇到黑色像素停止
            # 当达到足够长度时标记位置
            if consecutive >= 15:
                found_row = row
                break  # 找到后跳出循环

        if found_row != -1:
            # 计算裁剪区域（PIL坐标系）
            left = found_col_end + 3 + 8 # 小列右侧,战备图标左下角小图标
            upper = (found_row + ((e_row - found_row) / 2)) if (e_row - found_row) > 15 else  (s_row + ((e_row - s_row) / 2))# 取下半
            right = width     # PIL中右边界是exclusive
            lower = e_row + 1

            # 裁剪并保存图片
            cropped_img = img.crop((left, upper, right, lower))
            cropped_img.save(os.path.join(save_dir, f'{idx}.bmp'))


def color_to_grayscale(color, threshold=30):
    """
    将颜色转换为灰度值,如果颜色在指定范围内,则返回255(白色),否则返回0(黑色)。

    参数:
    color (tuple): RGB颜色值。
    threshold (int): 允许的颜色范围。
    """
    target_colors = [
        (218, 193, 119),
        (223, 117, 103),
        (80, 175, 200),
        (116, 161, 95),
        (190, 190, 190)
    ]

    for target in target_colors:
        if all(abs(c1 - c2) <= threshold for c1, c2 in zip(color, target)):
            return 255  # 白色
    return 0  # 黑色


def binarize_image(input_path='./temp/screenshot_cropped.png', output_path='./temp/screenshot_binary.bmp', threshold=35):
    """
    将PNG图片按规则二值化并保存为BMP格式。

    参数:
    input_path (str): 读取PNG图片的路径。
    output_path (str): 保存BMP图片的路径。
    threshold (int): 颜色匹配的阈值。
    """
    try:
        # 打开图片
        with Image.open(input_path) as img:
            # 将图片转换为RGB模式
            img_rgb = img.convert('RGB')

            # 创建一个新的图片用于存储二值化结果
            img_binary = Image.new('L', img_rgb.size)

            # 遍历每个像素
            for x in range(img_rgb.width):
                for y in range(img_rgb.height):
                    # 获取当前像素的颜色
                    r, g, b = img_rgb.getpixel((x, y))
                    # 将颜色转换为灰度值
                    gray_value = color_to_grayscale((r, g, b), threshold)
                    # 设置新的像素值
                    img_binary.putpixel((x, y), gray_value)

            # 保存图片
            img_binary.save(output_path, 'BMP')

            print(f"图片已成功二值化并保存到 {output_path}")
    except Exception as e:
        print(f"处理图片时发生错误: {e}")


def crop_image(input_path='./temp/screenshot_resized.png', output_path='./temp/screenshot_cropped.png', left=0, top=0, right=220, bottom=450):
    """
    截取PNG图片的左上角区域并保存。

    参数:
    input_path (str): 读取PNG图片的路径。
    output_path (str): 保存PNG图片的路径。
    left (int): 截取区域的左边界。
    top (int): 截取区域的上边界。
    right (int): 截取区域的右边界。
    bottom (int): 截取区域的下边界。
    """
    # 打开图片
    with Image.open(input_path) as img:
        # 截取图片
        cropped_img = img.crop((left, top, right, bottom))
        # 保存图片
        cropped_img.save(output_path, 'PNG')
        print(f"图片已成功截取并保存到 {output_path}")


def resize_image(input_path='./temp/screenshot.png', output_path='./temp/screenshot_resized.png'):
    """
    缩放PNG图片到1280x720并保存。

    参数:
    input_path (str): 读取PNG图片的路径。
    output_path (str): 保存PNG图片的路径。
    """
    # 打开图片
    with Image.open(input_path) as img:
        # 计算新的尺寸，保持宽高比
        original_width, original_height = img.size
        aspect_ratio = original_width / original_height
        new_width = 1280
        new_height = int(new_width / aspect_ratio)
        # 如果计算出的高度大于720，则调整高度并重新计算宽度
        if new_height > 720:
            new_height = 720
            new_width = int(new_height * aspect_ratio)
        # 调整图片尺寸
        try:
            resized_img = img.resize((new_width, new_height), Image.LANCZOS)
        except:
            resized_img = img.resize((new_width, new_height), Image.ANTIALIAS)
        # 保存图片
        resized_img.save(output_path, 'PNG')
        print(f"图片已成功缩放并保存到 {output_path}")


def capture_screenshot(save_path='./temp/screenshot.png'):
    """
    获取屏幕截图并保存为PNG格式到指定路径

    :param save_path: 保存截图的路径
    """
    with mss.mss() as sct:
        # 获取屏幕的尺寸
        monitor = sct.monitors[1]

        # 获取屏幕截图
        screenshot = sct.grab(monitor)

        # 保存截图为PNG格式
        mss.tools.to_png(screenshot.rgb, screenshot.size, output=save_path)


if __name__ == "__main__":
    import time
    # 记录开始时间
    # time.sleep(5)
    start_time = time.time()
    # capture_screenshot()
    resize_image()
    crop_image()

    binarize_image()
    split_image()
    print(f'耗时: {time.time() - start_time} 秒')
