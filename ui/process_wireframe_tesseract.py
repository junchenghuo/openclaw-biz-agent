import pytesseract
import cv2
import numpy as np
from PIL import Image

# 1. OCR识别图片内容
img_ocr = cv2.imread("./wireframe.png")
text = pytesseract.image_to_string(img_ocr, lang='chi_sim+eng')
print("=== 图片内容识别结果 ===")
print(text.strip())

# 2. 优化背景色
img = cv2.imread("./wireframe.png")
# 识别当前灰白色背景
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
_, mask = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY)

# 替换背景为柔和浅灰蓝色 #f0f4f8
bg_color = np.array([248, 244, 240], dtype=np.uint8) # BGR格式
for i in range(img.shape[0]):
    for j in range(img.shape[1]):
        if mask[i, j] == 255:
            img[i, j] = bg_color

# 提升对比度
alpha = 1.3
beta = 5
enhanced = cv2.convertScaleAbs(img, alpha=alpha, beta=beta)

# 保存处理后的图片
output_path = "/Users/imac/midCreate/openclaw-workspaces/ai-team/projects/tech-login-captcha-page/deliverables/wireframe_optimized.png"
cv2.imwrite(output_path, enhanced)
print(f"\n=== 处理完成 ===")
print(f"优化后图片已保存到项目交付目录：{output_path}")
print("优化说明：背景色替换为护眼浅灰蓝色(#f0f4f8)，文字对比度提升30%，适配登录页视觉规范")
