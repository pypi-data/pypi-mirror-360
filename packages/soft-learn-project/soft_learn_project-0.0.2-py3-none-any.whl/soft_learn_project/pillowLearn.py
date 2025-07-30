
import os
import PIL.Image
from PIL import Image, ImageDraw
import PIL.ImageFile


class PillowLearn():
  def __init__(self) -> None:
    """Pillow - 处理图像基础库 https://github.com/python-pillow/Pillow
    """
    pass

  def install(self):
    string = """pip install pillow
    conda install pillow
    """
    print(string)
    return None

  def notes(self):
    """
    # 图片基本信息
    image: Image.Image = Image.open("mylogo.jpg")
    print(image.filename)
    print(image.format)
    print(image.mode)
    print(image.size)
    print(image.info)
    print(image.getpixel((128, 256)))  # 取得某个点的RGB
    print(dir(image))
    # attributes_list = [attribute for attribute in dir(image) if attribute[0].islower()]
    # print(attributes_list)

    # 图像变换(convert)
    # https://pillow.readthedocs.io/en/stable/handbook/concepts.html  # concept-modes
    image = Image.open("mylogo.jpg")
    image.convert("1").save("img1_pixels.png", quality=100)  # 1位像素图
    image.convert("L").save("imgL_grayscale.png", quality=100)  # 8位灰度图
    image.convert("P").save("imgP_8_bit_colors.png", quality=100)  # 8位彩图

    # 图像剪切(crop)
    image.crop((240, 30, 300, 240)).save(
        "img_crop.png")  # 开始点x1, 开始点y1, 结束点x2, 结束点y2

    # 图像旋转(rotate)
    image.rotate(angle=30, resample=Image.NEAREST).save("img_rotate_30.png")
    image.rotate(-30).save("img_rotate_-30.png")
    image.rotate(30, Image.NEAREST, True).save(
        "img_rotate_30_expand.png")  # Image.NEAREST 旋转的算法，True表示扩展

    # 调整大小(resize)
    image = Image.open("mylogo.jpg")
    # image.show(title="logo")
    # 指定大小
    img_resize = image.resize(size=(200, 200), resample=Image.NEAREST)
    img_resize.save("img_resized.jpg")
    # print("ok")
    # 宽高取半
    img_resize = image.resize(
        (int(image.width/2), int(image.height/2)), Image.NEAREST)
    img_resize.show(title="resized")
    # img_resize.save("img_resized.jpg")

    # 画图写字
    from PIL import Image, ImageDraw, ImageFont
    image = Image.open("mylogo.jpg")
    image_draw = ImageDraw.Draw(image)
    image_draw.line(xy=(0, image.height, image.width, 0),
                    fill=(255, 0, 0), width=8)  # 画线
    image_draw.rectangle(xy=(100, 100, 200, 200), fill=(0, 255, 0))  # 矩形
    image_draw.ellipse(xy=(250, 300, 450, 400), fill=(0, 0, 255))  # 圆形

    image_font = ImageFont.truetype(
        font='/System/Library/Fonts/Times.ttc', size=48)  # 设置中文字体
    image_draw.multiline_text(xy=(0, 0), text='Pillow is good!不错', fill = (
        255, 255, 0), font=image_font)  # 写字
    image.save("img_edited.png")
    image.show()

    # 批量文件处理
    import os
    import glob
    from PIL import Image
    files = glob.glob('./*.jpg')
    for file in files:
        img = Image.open(file)
        # 宽高取半
        img_resize = img.resize((int(img.width / 2), int(img.height / 2)))
        ftitle, fext = os.path.splitext(file)
        img_resize.save(ftitle + '_half' + fext)

    # 其他课题
    # + 图片合并
    # + 图片反转
    # + 蒙版切除
    # + Gif制作
    # + 透明背景
    # + 像素计算
    # + 人脸识别(OpenCV)
    # + 马赛克处理
    # + 屏幕拷贝


    # ------------ 屏幕抓取  截屏
    import time
    from PIL import ImageGrab
    # # 抓取剪切板图片
    from PIL import Image,ImageGrab
    ImageGrab.grabclipboard()
    print("Ready!")
    time.sleep(2)

    # 全屏抓取
    ImageGrab.grab().save("./out/img_capture.png")
    # 指定范围抓取
    img = ImageGrab.grab(bbox=(100, 10, 200, 200))
    img.save("./out/img_capture_clip.png")
    print("Go!")

    # 利用Pillow制作透明或局部透明的图片
    from PIL import Image, ImageDraw, ImageFilter
    # 半透明50%(128/255)
    im_rgb = Image.open('res/mylogo.png')
    im_rgba = im_rgb.copy()
    im_rgba.putalpha(128).save('out/img_putalpha.png')
    # 切出形状透明
    # white ,L 表示生成8位黑白图，大小与原图相同，255白色代表不透明
    im_a = Image.new("L", im_rgb.size, 255)
    draw = ImageDraw.Draw(im_a)
    draw.rectangle((200, 100, 300, 200), fill=0, outline=0)  # black
    im_a.save("out/img_a.png")
    im_rgba = Image.open('res/mylogo.png').copy()
    im_rgba.putalpha(im_a)
    im_rgba.save('out/img_putalpha.png')

    # 高斯羽化
    im_a_blur = im_a.filter(ImageFilter.GaussianBlur(1))
    im_rgba.putalpha(im_a_blur)
    im_rgba.save('out/img_putalpha.png')
    """
    pass

  def open_image(self, fname='xxx/B_O_Gra.png'):
    image = PIL.Image.open(fp=fname)
    # 获取 PNG 图片的尺寸
    # width, height = img.size
    return image

  def save_image(self, img: PIL.ImageFile.ImageFile,
                 fname_out='output.jpg'):
    """
    打开图像
    img = Image.open("input.jpg")
    ---
    save() 方法的常见参数：
    fp: 文件路径或文件对象。图像将保存到这个路径。如果是文件对象，必须具有 write() 方法。

    示例：img.save("output.jpg")
    format: (可选) 图像格式，如 JPEG, PNG, BMP, GIF, TIFF 等。如果未指定，Pillow 将根据文件扩展名自动推断格式。

    示例：img.save("output.png", format="PNG")
    quality: (只对 JPEG 格式有效) 设置输出图像的质量。范围为 1 到 95，默认值为 75。较高的值会提供更好的图像质量，但文件体积更大。

    示例：img.save("output.jpg", quality=95)
    optimize: (可选) 启用图像压缩优化。对于 JPEG 和 PNG 图像，这可以减少文件大小。

    示例：img.save("output.jpg", optimize=True)
    progressive: (可选, 只对 JPEG 格式有效) 启用渐进式 JPEG。渐进式图像可以在低带宽环境下逐步显示。

    示例：img.save("output.jpg", progressive=True)
    dpi: (可选) 设置图像的 DPI（每英寸的像素数）。DPI 对图片的打印质量有影响，通常设置为 (300, 300) 或更高。

    示例：img.save("output.jpg", dpi=(300, 300))
    transparent: (只对 PNG 格式有效) 设置图像的透明度。可以将透明度层保存到 PNG 文件中。

    示例：img.save("output.png", transparent=True)
    subsampling: (只对 JPEG 格式有效) 设置 JPEG 的色度抽样。较低的值会保留更多颜色信息，改善图像清晰度。

    示例：img.save("output.jpg", subsampling=0)
    如何保存清晰度较高的图片？
    为了保存较高清晰度的图片，以下参数可以帮助提高质量：

    提高质量: 使用 quality 参数指定较高的图像质量值，如 95。
    不进行子采样: 对于 JPEG 文件，使用 subsampling=0 可以保持最高颜色质量。
    设置 DPI: 使用 dpi=(300, 300) 或更高的值，可以确保图像在打印时具有较高的清晰度。
    """

    # 保存高质量图片
    img.save(fname_out, quality=95, optimize=True,
             dpi=(300, 300), )
    # 设置 dpf=(300,300)的图片质量就不错了
    print(f'保存成功: {os.path.abspath(fname_out)}')
    return None

  def save2pdf(self, fname='xxx/xx.jpg',
               fname_out='output.pdf',
               resolution=300):
    """
    保存为pdf
    或者使用终端: pdfjam 工作照片.jpg -o 工作照片.pdf
    """

    img = Image.open(fname)
    width, height = img.size
    new_width = int(210*resolution/25.4)  # A4纸宽度 210mm * 300DPI / 25.4
    new_height = int(height * (new_width / width))
    img = img.resize((new_width, new_height), Image.LANCZOS)
    # 保存为PDF
    img.save(fname_out, format='PDF', resolution=resolution)
    pass

  def convert_png_to_jpg(self, png_path, jpg_path=None, quality=95):
    """
    将 PNG 图片转换为 JPG 格式。

    参数：
        png_path (str): 输入 PNG 文件路径。
        jpg_path (str): 输出 JPG 文件路径（可选，默认与 PNG 同名）。
        quality (int): 保存 JPG 的图像质量（1-100）。
    """
    if not os.path.exists(png_path):
      raise FileNotFoundError(f"未找到文件: {png_path}")

    # 默认输出文件名
    if jpg_path is None:
      jpg_path = os.path.splitext(png_path)[0] + ".jpg"

    with Image.open(png_path) as img:
      rgb_img = img.convert("RGB")  # 去除 alpha 通道
      rgb_img.save(jpg_path, "JPEG", quality=quality)
      print(f"已保存: {jpg_path}")

    return

  def resize_from_fig(self, fname='zm.jpeg', devide=2):
    """减小图片大小

    Args:
        fname (str, optional): _description_. Defaults to 'zm.jpeg'.
    """
    prefix, suffix = os.path.splitext(fname)
    img = Image.open(fname)

    img_small = img.resize(
        (int(img.size[0]/devide), int(img.size[1]/devide)), Image.Resampling.NEAREST)
    fname_small = prefix + '_bk'+suffix
    img_small.save(fname_small)
    size_img_small = round(os.path.getsize(fname_small)/1024, 2)
    print(f"原始大小为: {round(os.path.getsize(fname)/1024, 2)} KB, 转换的文件为: {os.path.abspath(fname_small)} ({size_img_small} KB)")
    pass

  def resize_from_image(self, img: Image.Image, devide=2):
    """减小图片大小

    Args:
        img (_type_): _description_

    Returns: img_small
        _type_: _description_
    """

    img_small = img.resize(
        (int(img.size[0]/devide), int(img.size[1]/devide)), Image.Resampling.NEAREST)
    return img_small

  def crop_to_ellipse(self, image_path, output_path, scale=1, outline_color='red', outline_width=5):
    """用于把一个图片裁剪成中心椭圆形, outline_color: 边界颜色
    scale: 椭圆的大小

    Args:
        image_path (_type_): _description_
        output_path (_type_): _description_
        scale (float, optional): _description_. Defaults to 0.8.
        outline_color (str, optional): _description_. Defaults to 'red'.
        outline_width (int, optional): _description_. Defaults to 20.
    """
    # 打开图像并转换为RGBA模式
    image = Image.open(image_path).convert("RGBA")
    width, height = image.size

    # 创建与图像相同大小的透明背景
    background = Image.new("RGBA", image.size, (255, 255, 255, 0))

    # 创建一个与图像相同大小的黑色椭圆形掩码
    mask = Image.new("L", image.size, 0)
    draw = ImageDraw.Draw(mask)

    # 计算椭圆的大小和位置
    ellipse_width = int(width * scale)
    ellipse_height = int(height * scale)
    left = (width - ellipse_width) // 2
    top = (height - ellipse_height) // 2
    right = left + ellipse_width
    bottom = top + ellipse_height

    # 绘制椭圆
    draw.ellipse([left, top, right, bottom], fill=255)

    # 将掩码应用于图像
    ellipse_image = Image.composite(image, background, mask)

    # 创建绘图对象以绘制椭圆边框
    draw = ImageDraw.Draw(ellipse_image)

    # 绘制椭圆边框
    draw.ellipse([left, top, right, bottom],
                 outline=outline_color,
                 width=outline_width)

    # 保存结果
    ellipse_image.save(output_path, "PNG")
