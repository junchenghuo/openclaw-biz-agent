#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PIL import Image, ImageDraw, ImageFont
import os

# 8国时钟数据
countries = [
    {"name": "中国北京", "tz": "UTC+8", "flag": "CN"},
    {"name": "美国纽约", "tz": "UTC-5", "flag": "US"},
    {"name": "英国伦敦", "tz": "UTC+0", "flag": "GB"},
    {"name": "日本东京", "tz": "UTC+9", "flag": "JP"},
    {"name": "德国柏林", "tz": "UTC+1", "flag": "DE"},
    {"name": "澳大利亚悉尼", "tz": "UTC+11", "flag": "AU"},
    {"name": "法国巴黎", "tz": "UTC+1", "flag": "FR"},
    {"name": "俄罗斯莫斯科", "tz": "UTC+3", "flag": "RU"},
]

# 图片设置
card_width = 300
card_height = 180
gap = 20
cols = 4
rows = 2

width = cols * card_width + (cols + 1) * gap
height = rows * card_height + (rows + 1) * gap + 100

# 创建图片
img = Image.new('RGB', (width, height), '#f5f7fa')
draw = ImageDraw.Draw(img)

# 使用系统字体
try:
    title_font = ImageFont.truetype("/System/Library/Fonts/ArialHB.ttc", 36)
    country_font = ImageFont.truetype("/System/Library/Fonts/ArialHB.ttc", 22)
    time_font = ImageFont.truetype("/System/Library/Fonts/ArialHB.ttc", 32)
    tz_font = ImageFont.truetype("/System/Library/Fonts/ArialHB.ttc", 16)
    flag_font = ImageFont.truetype("/System/Library/Fonts/ArialHB.ttc", 28)
except:
    title_font = ImageFont.load_default()
    country_font = ImageFont.load_default()
    time_font = ImageFont.load_default()
    tz_font = ImageFont.load_default()
    flag_font = ImageFont.load_default()

# 绘制标题
title = "World Clock - 8 Countries"
title_bbox = draw.textbbox((0, 0), title, font=title_font)
title_width = title_bbox[2] - title_bbox[0]
draw.text(((width - title_width) // 2, 30), title, fill='#1a1a2e', font=title_font)

subtitle = "Error: < 1 second | Real-time"
subtitle_bbox = draw.textbbox((0, 0), subtitle, font=tz_font)
subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
draw.text(((width - subtitle_width) // 2, 75), subtitle, fill='#666666', font=tz_font)

# 绘制时钟卡片
for idx, country in enumerate(countries):
    row = idx // cols
    col = idx % cols
    
    x = gap + col * (card_width + gap)
    y = 110 + row * (card_height + gap)
    
    # 卡片背景
    draw.rounded_rectangle([x, y, x + card_width, y + card_height], radius=15, fill='#ffffff', outline='#e0e0e0', width=1)
    
    # 国旗代码
    draw.text((x + 20, y + 20), country["flag"], fill='#0066cc', font=flag_font)
    
    # 国家名称
    draw.text((x + 80, y + 25), country["name"], fill='#1a1a2e', font=country_font)
    
    # 时区
    draw.text((x + 80, y + 52), country["tz"], fill='#666666', font=tz_font)
    
    # 时间占位符
    time_text = "--:--:--"
    draw.text((x + 20, y + 95), time_text, fill='#0066cc', font=time_font)

# 底部说明
footer = "Note: Real time will be provided by backend API"
footer_bbox = draw.textbbox((0, 0), footer, font=tz_font)
footer_width = footer_bbox[2] - footer_bbox[0]
draw.text(((width - footer_width) // 2, height - 30), footer, fill='#999999', font=tz_font)

# 保存图片
output_path = '/Users/imac/midCreate/openclaw-workspaces/ai-team/projects/世界时钟-20260315-01/deliverables/product/世界时钟-20260315-01-项目产品原型图-01.png'
img.save(output_path)
print(f"原型图-01 created: {output_path}")

# 创建02版本 - 移动端布局
img2 = Image.new('RGB', (400, 800), '#f5f7fa')
draw2 = ImageDraw.Draw(img2)

draw2.text((20, 20), "World Clock", fill='#1a1a2e', font=title_font)
draw2.text((20, 65), "Error < 1s | Real-time", fill='#666666', font=tz_font)

for idx, country in enumerate(countries):
    y = 110 + idx * 85
    
    draw2.rounded_rectangle([20, y, 380, y + 75], radius=10, fill='#ffffff', outline='#e0e0e0', width=1)
    
    draw2.text((30, y + 20), country["flag"], fill='#0066cc', font=flag_font)
    draw2.text((75, y + 15), country["name"], fill='#1a1a2e', font=country_font)
    draw2.text((75, y + 42), country["tz"], fill='#666666', font=tz_font)
    draw2.text((250, y + 20), "--:--:--", fill='#0066cc', font=time_font)

output_path2 = '/Users/imac/midCreate/openclaw-workspaces/ai-team/projects/世界时钟-20260315-01/deliverables/product/世界时钟-20260315-01-项目产品原型图-02.png'
img2.save(output_path2)
print(f"原型图-02 created: {output_path2}")
