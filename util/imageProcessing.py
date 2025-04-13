import logging
import os
import mss
import mss.tools
from PIL import Image
from collections import deque
try:
    from util.loadSetting import getConfigDict
except ModuleNotFoundError:
    from loadSetting import getConfigDict


def rotate_left_90(matrix):
    # 反转每一行
    reversed_rows = [row[::-1] for row in matrix]
    # 转置并转换为列表的列表
    rotated = [list(row) for row in zip(*reversed_rows)]
    return rotated


# 遍历arrow下所有图片
arrow_data = {
    'W': [],
    'A': [],
    'S': [],
    'D': []
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


def determine_arrow_direction(image_path = '' , img = None):
    if not img:
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

def arrow_str_fast(imgss):
    result = ''
    for idx, imgs in enumerate(imgss):
        if imgs is None:
            result += '\n'
            continue
        for img in imgs:
            result += determine_arrow_direction(img=img)
        if idx != len(imgss) - 1:
            result += '\n'
    return result

def process_images_core(img, target_size=(15, 15)):
    imgs = []
    if img is None:
        return imgs
    width, height = img.size
    pixels = img.load()
    # 初始化访问矩阵和区域列表
    visited = [[False for _ in range(width)] for _ in range(height)]
    regions = []
    # 判断白色像素
    def is_white(pixel):
        return pixel > 200
    # 遍历所有像素寻找连通区域
    for y in range(height):
        for x in range(width):
            if not visited[y][x] and is_white(pixels[x, y]):  # type: ignore
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
        resized_img = region_img.resize(
            target_size, Image.Resampling.NEAREST)
        imgs.append(resized_img)
    return imgs

def process_images(directory='./temp/split_images', target_size=(15, 15), fast_mode = False, imgs:list = []):
    """
    处理指定目录下的所有n.bmp图片,切割连续白色区域并保存到对应编号的文件夹

    参数：
    input_dir - 输入目录路径(包含0.bmp, 1.bmp等数字命名的图片)
    target_size - 缩放目标尺寸,默认6x6像素
    """
    if not fast_mode:
        for filename in os.listdir(directory):
            if not filename.endswith('.bmp'):
                continue
            # 创建输出文件夹
            base_name = filename.split('.')[0]
            output_dir = os.path.join(directory, base_name)
            os.makedirs(output_dir, exist_ok=True)
            # 打开并转换图像
            img = Image.open(os.path.join(directory, filename)).convert('L')
            # 处理图像并保存结果
            imgs = process_images_core(img, target_size)
            for index, resized_img in enumerate(imgs):
                # 保存结果
                resized_img.save(os.path.join(output_dir, f"{index}.bmp"))
    else:
        imgss = []
        for img in imgs:
            imgss.append(process_images_core(img, target_size))
        return imgss


def split_image(image_path='./temp/screenshot_binary.bmp', save_dir='./temp/split_images', fast_mode = False, img = None):
    imgs = []
    # 打开图片并转换为灰度图
    if not fast_mode:
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
        logging.warning("未找到符合条件的列")
        return

    # 在目标列及其右侧两列中查找所有有效竖列
    columns_to_check = [c for c in range(target_col, min(target_col+3, width))]
    segments = []
    for col in columns_to_check:
        current_segments = []
        start = -1
        for row in range(height):
            pixel = img.getpixel((col, row))
            if pixel == 255:
                if start == -1:
                    start = row
                # 处理行结束或遇到黑像素的情况
                if row == height-1 or img.getpixel((col, row+1)) != 255:
                    if row - start + 1 >= 15:
                        current_segments.append((col, start, row))
                    start = -1
            else:
                if start != -1:
                    if (row-1) - start + 1 >= 15:
                        current_segments.append((col, start, row-1))
                    start = -1
        segments.extend(current_segments)

    # 按起始行排序并过滤高度相近的竖列（保留最左侧）
    sorted_segments = sorted(segments, key=lambda x: x[1])
    filtered_segments = []
    current_group = []
    for seg in sorted_segments:
        if not current_group:
            current_group.append(seg)
        else:
            if seg[1] - current_group[0][1] < 5:
                current_group.append(seg)
            else:
                # 选择当前组中最左侧的竖列
                filtered_segments.append(
                    min(current_group, key=lambda x: x[0]))
                current_group = [seg]
    if current_group:
        filtered_segments.append(min(current_group, key=lambda x: x[0]))

    # 小列补全
    # 计算小列平均高度
    avg_height = sum([seg[2] - seg[1] for seg in filtered_segments]) / len(filtered_segments)
    new_filtered_segments = []
    spacings = []
    idx_temp = 0
    # 记录补全的idx
    idx_ext_list = []
    # 从第二个开始遍历小列,如果和上一个小列的间距大于小列平均高度,则在中间插入一个小列
    for idx, (col, s_row, e_row) in enumerate(filtered_segments):
        # 跳过第一个
        if idx == 0:
            new_filtered_segments.append((col, s_row, e_row))
            continue
        prev_col, prev_s_row, prev_e_row = filtered_segments[idx - 1]
        spacing = s_row - prev_e_row
        if spacing > avg_height:
            # 根据spacings计算平均间隔,如果不存在默认为9
            avg_spacing = sum(spacings) / len(spacings) if spacings else 9
            # 计算能插几个小列(小列高度+平均间隔)
            num_inserted = int(spacing / (avg_height + avg_spacing))
            # 插入小列
            for i in range(num_inserted):
                idx_temp += 1
                idx_ext_list.append(idx_temp)
                # 取整
                s_new = int(prev_e_row + ((i + 1) * avg_spacing) + (i * avg_height))
                e_new = s_new + int(avg_height) - 1
                new_filtered_segments.append((col, s_new, e_new))
        else:
            idx_temp += 1
            spacings.append(spacing)
        new_filtered_segments.append((col, s_row, e_row))
    filtered_segments = new_filtered_segments

    # 创建保存目录
    if not fast_mode:
        os.makedirs(save_dir, exist_ok=True)

    found_col_end_list = []
    # 处理每个有效竖列
    for idx, (col, s_row, e_row) in enumerate(filtered_segments):
        found_row = -1
        found_col_end = -1
        imgs.append(None)

        # 如果不在idx_ext_list中,在竖列高度范围内寻找有效行
        if not idx in idx_ext_list:
            for row in range(s_row -1, e_row + 2):
                consecutive = 0
                # 从当前竖列位置向右扫描
                for c in range(col + 1, width):
                    if img.getpixel((c, row)) == 255:
                        consecutive += 1
                        if consecutive >= 15:
                            found_col_end = c
                    else:
                        break  # 遇到黑像素停止
                # 确认找到足够长度的连续白像素
                if consecutive >= 15:
                    found_row = row
                    break
            if found_col_end != -1:
                found_col_end_list.append(found_col_end)
        else:
            # 如果是补全的小列
            # 第一行作为小行,用之前小行的平均宽度
            found_col_end = int(sum(found_col_end_list) / len(found_col_end_list)) if found_col_end_list else 32
            found_row = s_row

        if found_row != -1:
            # 计算裁剪区域（PIL坐标系）
            left = found_col_end + 3 + 8  # 小列右侧偏移量
            upper_mid = (found_row + ((e_row - found_row) / 2)
                         if (e_row - found_row) > 15
                         else s_row + ((e_row - s_row) / 2))
            upper = int(upper_mid)  # 取下半区域
            right = width  # 右边界exclusive
            lower = e_row + 1

            # 执行裁剪并保存
            cropped_img = img.crop((left, upper, right, lower))
            if fast_mode:
                imgs[idx] = cropped_img
            else:
                cropped_img.save(os.path.join(save_dir, f'{idx}.bmp'))
    return imgs


def hex_to_rgb(hex_color):
    """
    将16位颜色代码转换为RGB格式
    :param hex_color: 16位颜色代码,例如'#FF5733'
    :return: RGB元组,例如(255, 87, 51)
    """
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def color_to_grayscale(color, threshold=None, target_colors = [hex_to_rgb(c) for c in '#DAC177,#DF7567,#50AFC8,#74A15F,#BEBEBE,#BAB9A1,#E4D0AA'.split(',')]):
    """
    将颜色转换为灰度值,如果颜色在指定范围内,则返回255(白色),否则返回0(黑色)。

    参数:
    color (tuple): RGB颜色值。
    threshold (int): 允许的颜色范围。
    """

    for target in target_colors:
        if all(abs(c1 - c2) <= threshold for c1, c2 in zip(color, target)):
            return 255  # 白色
    return 0  # 黑色

def binarize_image_core(threshold, colors, img):
    """
    将图片按规则二值化。

    参数:
    threshold (int): 颜色匹配的阈值。
    colors (list): 目标颜色列表。
    img (PIL.Image): PIL图片对象。
    """
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
            gray_value = color_to_grayscale((r, g, b), threshold, colors)
            # 设置新的像素值
            img_binary.putpixel((x, y), gray_value)
    return img_binary

def binarize_image(input_path='./temp/screenshot_cropped.png', output_path='./temp/screenshot_binary.bmp', threshold=None, config = None, fast_mode = False, img = None):
    """
    将PNG图片按规则二值化并保存为BMP格式。

    参数:
    input_path (str): 读取PNG图片的路径。
    output_path (str): 保存BMP图片的路径。
    threshold (int): 颜色匹配的阈值。
    """
    if config is None:
        config = getConfigDict()
    colors = [hex_to_rgb(c) for c in config['COLORS'].split(',')]
    if threshold is None:
        threshold = int(config['THRESHOLD'])
    if fast_mode:
        return binarize_image_core(threshold, colors, img)
    try:
        # 打开图片
        with Image.open(input_path) as img:
            # 将图片转换为RGB模式
            img_rgb = img.convert('RGB')

            # 创建一个新的图片用于存储二值化结果
            img_binary = binarize_image_core(threshold, colors, img_rgb)

            # 保存图片
            img_binary.save(output_path, 'BMP')

            logging.debug(f"图片已成功二值化并保存到 {output_path}")
    except Exception as e:
        logging.warning(f"处理图片时发生错误: {e}")


def crop_image(input_path='./temp/screenshot_resized.png', output_path='./temp/screenshot_cropped.png', left=None, top=None, right=None, bottom=None, config = None,fast_mode = False, img = None):
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
    if config is None:
        config = getConfigDict()
    if left is None:
        left = int(config['LEFT'])
    if top is None:
        top = int(config['TOP'])
    if right is None:
        right = int(config['RIGHT'])
    if bottom is None:
        bottom = int(config['BOTTOM'])
    if fast_mode:
        return img.crop((left, top, right, bottom))
    # 打开图片
    if input_path == output_path:
        output_path += '.crop_tmp'
    with Image.open(input_path) as img:
        # 截取图片
        cropped_img = img.crop((left, top, right, bottom))
        # 保存图片
        cropped_img.save(output_path, 'PNG')
        logging.debug(f"图片已成功截取并保存到 {output_path}")
    # 如果末尾是'.crop_tmp',则删除原文件
    if output_path.endswith('.crop_tmp'):
        os.remove(input_path)
        os.rename(output_path, input_path)

def resize_image_core(img):
    # 计算新的尺寸，保持宽高比
    original_width, original_height = img.size
    aspect_ratio = original_height / original_width
    new_height = 720
    new_width = int(new_height / aspect_ratio)
    # 调整图片尺寸
    try:
        resized_img = img.resize((new_width, new_height), Image.LANCZOS)
    except:
        resized_img = img.resize((new_width, new_height), Image.ANTIALIAS)
    return resized_img

def resize_image(input_path='./temp/screenshot.png', output_path='./temp/screenshot_resized.png'):
    """
    等比例地将PNG图片的高度缩放到720像素并保存。

    参数:
    input_path (str): 读取PNG图片的路径。
    output_path (str): 保存PNG图片的路径。
    """
    # 打开图片
    with Image.open(input_path) as img:
        resized_img = resize_image_core(img)
        # 保存图片
        resized_img.save(output_path, 'PNG')
        logging.debug(f"图片已成功缩放并保存到 {output_path}")


def capture_screenshot(save_path='./temp/screenshot.png',fast_mode=False):
    """
    获取屏幕截图并保存为PNG格式到指定路径

    :param save_path: 保存截图的路径
    """
    # 如果save_path包含'temp/'且fast_mode为False且temp目录不存在,则创建temp目录
    if not fast_mode and 'temp/' in save_path and not os.path.exists('./temp'):
        os.makedirs('./temp')
    with mss.mss() as sct:
        # 获取屏幕的尺寸
        monitor = sct.monitors[1]

        # 获取屏幕截图
        screenshot = sct.grab(monitor)

        if fast_mode:
            image = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
            return image

        # 保存截图为PNG格式
        mss.tools.to_png(screenshot.rgb, screenshot.size, output=save_path)

def fast_arrow(config, img = None):
    if img is None:
        img = capture_screenshot(fast_mode=True)
    img = resize_image_core(img)
    img = crop_image(img=img, fast_mode=True, config=config)
    img = binarize_image(img=img, fast_mode=True, config=config)
    imgs = split_image(img=img, fast_mode=True)
    imgss = process_images(fast_mode=True, imgs=imgs)
    return arrow_str_fast(imgss)

if __name__ == "__main__":
    import time
    # 记录开始时间
    # time.sleep(5)
    start_time = time.time()
    print(fast_arrow(getConfigDict(),Image.open('./temp/screenshot.png')))
    print(f'耗时: {time.time() - start_time} 秒')
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
