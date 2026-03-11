from PIL import Image, ImageDraw, ImageFilter
import sys

def optimize_background(input_path, output_path):
    # 打开原图
    img = Image.open(input_path).convert("RGBA")
    width, height = img.size
    
    # 创建新的背景图层：深色科技蓝渐变
    background = Image.new("RGBA", (width, height), (0, 0, 0, 255))
    draw = ImageDraw.Draw(background)
    
    # 绘制径向渐变，从顶部深蓝色到底部更深的蓝色
    for y in range(height):
        # 颜色渐变：顶部 #0a192f 到 底部 #020c1b
        r = int(10 + (2 - 10) * y / height)
        g = int(25 + (12 - 25) * y / height)
        b = int(47 + (27 - 47) * y / height)
        draw.line([(0, y), (width, y)], fill=(r, g, b, 255))
    
    # 把原图画到背景上，保留原有的线条和文字
    result = Image.alpha_composite(background, img)
    
    # 转换为RGB保存为PNG
    result.convert("RGB").save(output_path, "PNG")
    print(f"优化后的图片已保存到: {output_path}")

if __name__ == "__main__":
    input_file = "./wireframe.png"
    output_file = "./optimized_wireframe.png"
    optimize_background(input_file, output_file)
