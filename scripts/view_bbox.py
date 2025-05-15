import json
from pathlib import Path
from PIL import Image, ImageDraw
import matplotlib.pyplot as plt
import yaml

# === 파일 경로 설정 ===
# config.yaml 파일 읽기
with open('config/config.yaml', 'r', encoding='utf-8') as file:
    config = yaml.safe_load(file)
    
label_path = Path(config['paths']['extract_zip']) / "labels"
image_path = Path(config['paths']['extract_zip']) / "images"

# 파일 정렬
image_files = sorted((image_path / "흑색점").glob("*.png"))  
label_files = sorted((label_path / "흑색점").glob("*.json"))

# 첫 번째 이미지와 라벨 파일 선택
label_path = label_files[0] if label_files else None
image_path = image_files[0] if image_files else None

# === 라벨 파일 로딩 ===
with open(label_path, encoding='utf-8') as f:
    data = json.load(f)

annotation = data['annotations'][0]

# === 이미지 로딩 ===
img = Image.open(image_path).convert("RGB")

# === 바운딩 박스 정보 ===
draw = ImageDraw.Draw(img)
x = annotation['bbox']['xpos']
y = annotation['bbox']['ypos']
w = annotation['bbox']['width']
h = annotation['bbox']['height']
draw.rectangle([x, y, x + w, y + h], outline='red', width=3)

# === 시각화 ===
plt.figure(figsize=(3, 3))
plt.imshow(img)
plt.axis('off')
plt.show()
