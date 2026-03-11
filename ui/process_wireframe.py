from paddleocr import PaddleOCR
import cv2
import numpy as np
from PIL import Image

# 1. OCR识别图片内容
ocr = PaddleOCR(use_angle_cls=True, lang="ch", show_log=False)
result = ocr.ocr("./wireframe.png", cls=True)

print("=== 图片内容识别结果 ===")
lines = []
if result and result[0]:
    items = sorted(result[0], key=lambda x: x[0][0][1])
    for item in items:
        text = item[1][0]
        confidence = item[1][1]
        lines.append(f"文本：{text}，置信度：{confidence:.2f}")
        print(f"- {text} (置信度: {confidence:.2f})")

# 2. 优化背景色
img = cv2.imread("./wireframe.png")
# 转换为HSV方便调整背景
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

# 识别当前灰白色背景的范围
lower_gray = np.array([0, 0, 200])
upper_gray = np.array([180, 30, 255])
mask = cv2.inRange(hsv, lower_gray, upper_gray)

# 替换背景为柔和的浅灰蓝色 (#f0f4f8)
bg_color_bgr = np.array([248, 244, 240]) # BGR格式对应#f0f4f8
img[mask > 0] = bg_color_bgr

# 增强文字对比度
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
alpha = 1.2 # 对比度系数
beta = 10 # 亮度系数
enhanced = cv2.convertScaleAbs(img, alpha=alpha, beta=beta)

# 保存处理后的图片
output_path = "./wireframe_optimized.png"
cv2.imwrite(output_path, enhanced)
print(f"\n=== 处理完成 ===")
print(f"优化后图片已保存到：{output_path}")
print("背景色已替换为浅灰蓝色#f0f4f8，文字对比度提升20%")
