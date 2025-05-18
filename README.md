# For-skin: 피부 질환 예측 시스템
AI를 활용한 피부 질환 이미지 분석 및 진단 보조 시스템이다. 

YOLOv11n 모델을 기반으로 피부 질병을 예측하고, GPT를 활용해 질병별 진단 질문을 생성하여 최종 진단을 제공한다.
<br>
<br>


### 🚀 주요 기능
<img src="https://github.com/user-attachments/assets/5c374db4-fb3c-4859-b4b3-124c6801befb" width="600"/>

- 피부 사진 기반 질병 예측 (YOLOv11n 기반 모델)

- ChromaDB에 접근한 후 GPT를 활용하여 질병 진단 질문 자동 생성
<br>

### 🚀 실행 화면
- 피부 질환 예측 및 설문 후 최종 진단 
<p align="center">
  <img src="https://github.com/user-attachments/assets/06065806-c3fa-43f8-8584-98d8bc746fe6" width="45%"/>
  <img src="https://github.com/user-attachments/assets/c3832bb3-8908-4183-a876-1209118d88ed" width="45%"/>
</p>
<br>


### 🔨 기술 스택
<img src="https://github.com/user-attachments/assets/36d954e8-fdde-4fb3-9e40-410f0a2811ac" width="750"/>
<br>
<br>


### 🗂 프로젝트 구조 및 설명
```
For-skin/
├── main.py                  # FastAPI 서버 실행 파일
├── requirements.txt         # 의존 패키지 목록
├── config/                  # 설정 파일 (예: 모델 경로 등)
│   └── config.yaml
├── model/
│   └── best.pt              # 학습된 YOLOv11n 모델
├── scripts/                 # 모델 학습 및 유틸리티 스크립트
│   ├── diagnose_data.json       # 질병별 진단 질문 리스트
│   ├── preprocess2YOLOdata.py   # 데이터 전처리
│   ├── train_yolo11n.ipynb      # YOLOv11n 학습 노트북
│   ├── predict_test.py          # 이미지 예측 테스트
│   ├── view_bbox.py             # 예측 결과 시각화
│   └── create_chromadb.py       # 진단 질문용 DB 생성
├── streamlit_app/
│   └── app.py               # Streamlit UI 앱
```
<br>

### 🔧 설치 및 실행 방법
**1. Repository Clone**
```
git clone https://github.com/mingd00/For-skin.git
cd For-skin
```

**2. 가상환경 설정**
```
python -m venv venv
venv\Scripts\activate      # Window
# source venv/bin/activate     # (macOS / Linux)
```

**3. 패키지 설치**
```
pip install -r requirements.txt
```

**4. FastAPI 서버 실행**
```
uvicorn main:app --reload
```

**5. Streamlit 서버 실행**
```
streamlit run streamlit_app/app.py 
```

