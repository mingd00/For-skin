import zipfile
import shutil
import json
from pathlib import Path
from tqdm import tqdm
import random
import yaml

# === 경로 설정 ===

# config.yaml 파일 읽기
with open('config/config.yaml', 'r', encoding='utf-8') as file:
    config = yaml.safe_load(file)

# 경로 불러오기
SKIN_TUMOR_IMG = Path(config['paths']['skin_tumor_img'])
SKIN_TUMOR_LABEL = Path(config['paths']['skin_tumor_label'])
EXTRACT_ZIP_PATH = Path(config['paths']['extract_zip'])
YOLO_SKIN_DATASET = Path(config['paths']['yolo_skin_dataset'])

# === YOLO 디렉토리 생성 ===
for sub in ["images/train", "images/val", "labels/train", "labels/val"]:
    (YOLO_SKIN_DATASET / sub).mkdir(parents=True, exist_ok=True)

# === 1. 압축 해제 함수 ===
def EXTRACT_ZIP(zip_path: Path, extract_to: Path):
    with zipfile.ZipFile(zip_path, 'r') as zf:
        zf.extractall(extract_to)

# === 2. 압축 해제 (이미지 + 라벨) ===
print("압축 해제 중...")

# 데이터셋 (TS_*, TL_* 압축 파일)
for zip_file in tqdm(sorted(SKIN_TUMOR_IMG.glob("TS_*.zip"))):
    cls_name = zip_file.stem.replace("TS_", "")
    EXTRACT_ZIP(zip_file, EXTRACT_ZIP_PATH / "images" / cls_name)

for zip_file in tqdm(sorted(SKIN_TUMOR_LABEL.glob("TL_*.zip"))):
    cls_name = zip_file.stem.replace("TL_", "")
    EXTRACT_ZIP(zip_file, EXTRACT_ZIP_PATH / "labels" / cls_name)

# === 3. YOLO 형식으로 재구성 ===
print("YOLO 데이터셋 구성 중...")
classes = sorted([d.name for d in (EXTRACT_ZIP_PATH / "images").iterdir() if d.is_dir()])
class_to_index = {cls: idx for idx, cls in enumerate(classes)}
print("클래스 매핑:", class_to_index)

for cls in tqdm(classes):
    img_folder = EXTRACT_ZIP_PATH / "images" / cls
    label_folder = EXTRACT_ZIP_PATH / "labels" / cls

    # 이미지 정렬
    images = sorted(list(img_folder.glob("*.png")))

    # 로컬 시드 기반 셔플
    rng = random.Random(42)
    rng.shuffle(images)

    # 총 800개의 데이터를 8:2로 분할
    train_imgs = images[:640]
    val_imgs = images[640:]

    for split, split_imgs in [("train", train_imgs), ("val", val_imgs)]:
        for img_path in split_imgs:
            img_name = f"{cls}_{img_path.stem}{img_path.suffix}"
            dst_img = YOLO_SKIN_DATASET / "images" / split / img_name
            dst_lbl = YOLO_SKIN_DATASET / "labels" / split / img_name.replace(img_path.suffix, ".txt")

            shutil.copy(img_path, dst_img)  # 이미지 복사
            
            # 라벨 파일 생성
            json_path = label_folder / (img_path.stem + ".json")

            if json_path.exists():
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                annotations = data.get("annotations", [])
                with open(dst_lbl, "w", encoding='utf-8') as out:
                    for ann in annotations:
                        diagnosis = ann['diagnosis_info']['diagnosis_name']
                        class_id = class_to_index.get(diagnosis, -1)
                        if class_id == -1:
                            continue  # 해당 클래스가 없으면 skip

                        bbox = ann['bbox']
                        img_w = ann['photograph']['width']
                        img_h = ann['photograph']['height']

                        xpos = bbox['xpos']
                        ypos = bbox['ypos']
                        bw = bbox['width']
                        bh = bbox['height']

                        x_center = (xpos + bw / 2) / img_w
                        y_center = (ypos + bh / 2) / img_h
                        norm_bw = bw / img_w
                        norm_bh = bh / img_h

                        out.write(f"{class_id} {x_center:.6f} {y_center:.6f} {norm_bw:.6f} {norm_bh:.6f}\n")
            else:
                # json 라벨이 없을 경우 빈 txt 파일 생성
                with open(dst_lbl, "w") as f:
                    f.write("")

# === 4. YAML 파일 생성 ===
yaml_data = {
    'train': str(YOLO_SKIN_DATASET / 'images/train'),
    'val': str(YOLO_SKIN_DATASET / 'images/val'),
    'nc': len(classes),  # 클래스 개수
    'names': classes     # 클래스 이름들
}

yaml_file = YOLO_SKIN_DATASET / 'data.yaml'
with open(yaml_file, 'w', encoding='utf-8') as file:
    yaml.dump(yaml_data, file, default_flow_style=False, allow_unicode=True)

print("✅ YOLO 데이터셋 준비 완료!")
