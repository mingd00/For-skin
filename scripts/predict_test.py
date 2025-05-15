from ultralytics import YOLO

def predict_image(model, img_name):
    """
    주어진 이미지에 대해 YOLO 모델로 예측하고 결과를 출력하는 함수

    Parameters:
    - model: 학습된 YOLO 모델 객체 (예: YOLO('model/best.pt'))
    - img_name: 예측할 이미지 이름 (예: 광선각화증)
    """
    result = model.predict(source=f'scripts/test_data/{img_name}.png')
    r = result[0]

    # 예측된 클래스 ID 및 이름
    class_ids = r.boxes.cls.cpu().numpy()
    class_names = [r.names[int(c)] for c in class_ids]

    print("예측된 클래스들:", class_names)

    # 각 박스별 클래스, confidence 출력
    for box in r.boxes:
        cls_id = int(box.cls)
        cls_name = r.names[cls_id]
        confidence = float(box.conf)
        print(f"클래스: {cls_name}, 신뢰도: {confidence:.2f}")
        
        
model = YOLO('model/best.pt')
predict_image(model, '비립종') # 모델, 이미지 이름 
