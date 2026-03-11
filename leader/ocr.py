import pytesseract
from PIL import Image

def extract_text_tesseract(image_path: str, lang: str = "eng") -> str:
    image = Image.open(image_path)
    config = "--psm 6 --oem 3"
    text = pytesseract.image_to_string(image, lang=lang, config=config)
    return text.strip()

if __name__ == "__main__":
    wireframe_text = extract_text_tesseract("wireframe.png")
    print("=== wireframe.png 提取内容 ===")
    print(wireframe_text)
    print("\n=== q.png 提取内容 ===")
    q_text = extract_text_tesseract("q.png")
    print(q_text)
