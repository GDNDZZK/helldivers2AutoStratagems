import os
import mss
import mss.tools
from PIL import Image
from collections import deque
try:
    from util.loadSetting import getConfigDict
except ModuleNotFoundError:
    from loadSetting import getConfigDict
config = getConfigDict()
def rotate_left_90(matrix):
    # 反转每一行
    reversed_rows = [row[::-1] for row in matrix]
    # 转置并转换为列表的列表
    rotated = [list(row) for row in zip(*reversed_rows)]
    return rotated

# 遍历arrow下所有图片
arrow_data = {
    'W' : [],
    'A' : [],
    'S' : [],
    'D' : []
}
for filename in os.listdir('./arrow'):
    # 转换为二维数组放入w_arrow_list
    img = Image.open('./arrow/' + filename).convert('L')
    img_array = list(img.getdata())
    img_array = [img_array[i:i+img.width]
                 for i in range(0, len(img_array), img.width)]
    arrow_data['W'].append(img_array)
    img_array = rotate_left_90(img_array)
    arrow_data['A'].append(img_array)
    img_array = rotate_left_90(img_array)
    arrow_data['S'].append(img_array)
    img_array = rotate_left_90(img_array)
    arrow_data['D'].append(img_array)

def determine_arrow_direction(image_path):
    img = Image.open(image_path).convert('L')
    img_array = list(img.getdata())
    img_array = [img_array[i:i+img.width]
                 for i in range(0, len(img_array), img.width)]
    # 计算匹配程度(示例数组是0的地方变成1扣2分,1的地方变成0不扣分,和原本一样加一分)

    def sum_score(img_array, arrow):
        score = 0
        for i in range(len(img_array)):
            for j in range(len(img_array)):
                if img_array[i][j] == arrow[i][j]:
                    score += 1
                elif img_array[i][j] == 1 and arrow[i][j] == 0:
                    score -= 1
        return score
    max_score = -100000
    result = ''
    for tag, arrow_list in arrow_data.items():
        for arrow in arrow_list:
            score = sum_score(img_array, arrow)
            if score > max_score:
                max_score = score
                result = tag
    if max_score < 150:
        result = ''
    return result


def arrow_str(input_dir='./temp/split_images'):
    result = ''
    end_dirname = [i for i in os.listdir(
        input_dir) if os.path.isdir(os.path.join(input_dir, i))][-1]
    # 输入目录,遍历每一个子文件夹,跳过文件
    for dirname in os.listdir(input_dir):
        if not os.path.isdir(os.path.join(input_dir, dirname)):
            continue
        # 遍历子文件夹中每一个bmp文件
        for filename in sorted(os.listdir(os.path.join(input_dir, dirname)), key=lambda x: int(os.path.splitext(x)[0])):
            if not filename.lower().endswith('.bmp'):
                continue
            result += determine_arrow_direction(
                os.path.join(input_dir, dirname, filename))
        # 如果不是最后一行则添加换行
        if dirname != end_dirname:
            result += '\n'
    # 移除最后一个换行
    return result


def process_images(directory='./temp/split_images', target_size=(15, 15)):
    """
    处理指定目录下的所有n.bmp图片,切割连续白色区域并保存到对应编号的文件夹

    参数：
    input_dir - 输入目录路径(包含0.bmp, 1.bmp等数字命名的图片)
    target_size - 缩放目标尺寸,默认6x6像素
    """

    for filename in os.listdir(directory):
        if not filename.endswith('.bmp'):
            continue
        # 创建输出文件夹
        base_name = filename.split('.')[0]
        output_dir = os.path.join(directory, base_name)
        os.makedirs(output_dir, exist_ok=True)
        # 打开并转换图像
        img = Image.open(os.path.join(directory, filename)).convert('RGB')
        width, height = img.size
        pixels = img.load()
        # 初始化访问矩阵和区域列表
        visited = [[False for _ in range(width)] for _ in range(height)]
        regions = []
        # 判断白色像素（可根据实际情况调整阈值）
        def is_white(pixel):
            return pixel[0] > 200 and pixel[1] > 200 and pixel[2] > 200
        # 遍历所有像素寻找连通区域
        for y in range(height):
            for x in range(width):
                if not visited[y][x] and is_white(pixels[x, y]): # type: ignore
                    # BFS遍历连通区域
                    queue = deque()
                    queue.append((x, y))
                    visited[y][x] = True
                    region_points = []
                    while queue:
                        x0, y0 = queue.popleft()
                        region_points.append((x0, y0))
                        # 检查8邻域
                        for dx, dy in [(-1, -1), (-1, 0), (-1, 1),
                                       (0, -1),          (0, 1),
                                       (1, -1),  (1, 0), (1, 1)]:
                            nx, ny = x0 + dx, y0 + dy
                            if 0 <= nx < width and 0 <= ny < height and not visited[ny][nx] and is_white(pixels[nx, ny]): # type: ignore
                                visited[ny][nx] = True
                                queue.append((nx, ny))
                    # 过滤小区域
                    if len(region_points) >= 25:
                        # 计算包围盒
                        min_x = min(x for x, y in region_points)
                        max_x = max(x for x, y in region_points)
                        min_y = min(y for x, y in region_points)
                        max_y = max(y for x, y in region_points)
                        regions.append((min_x, min_y, max_x, max_y))
        # 按从左到右、从上到下排序
        regions.sort(key=lambda r: (r[0], r[1]))
        # 处理每个有效区域
        for index, (x1, y1, x2, y2) in enumerate(regions):
            # 裁剪并缩放
            region_img = img.crop((x1, y1, x2 + 1, y2 + 1))
            resized_img = region_img.resize(target_size, Image.Resampling.NEAREST)
            # 保存结果
            resized_img.save(os.path.join(output_dir, f"{index}.bmp"))


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
            left = found_col_end + 3 + 8  # 小列右侧,战备图标左下角小图标
            upper = (found_row + ((e_row - found_row) / 2)) if (e_row -
                                                                found_row) > 15 else (s_row + ((e_row - s_row) / 2))  # 取下半
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
        (190, 190, 190),
        (186, 185, 161),
        (228, 208, 170),
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


def crop_image(input_path='./temp/screenshot_resized.png', output_path='./temp/screenshot_cropped.png', left=int(config['LEFT']), top=int(config['TOP']), right=int(config['RIGHT']), bottom=int(config['BOTTOM'])):
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
    process_images()
    print(arrow_str())
    print(f'耗时: {time.time() - start_time} 秒')
    pass
