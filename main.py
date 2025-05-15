from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel
from langchain.vectorstores import Chroma
from langchain.embeddings.openai import OpenAIEmbeddings
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image, UnidentifiedImageError
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from ultralytics import YOLO
from dotenv import load_dotenv
import json
import os
import io

app = FastAPI()

# CORS 허용 (Streamlit과 연동)
origins = ["http://127.0.0.1:8501"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# 모델 로드
model = YOLO('model/best.pt')

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    if file is None:
        raise HTTPException(status_code=400, detail="파일이 업로드되지 않았습니다.")

    try:
        image_bytes = await file.read()
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

    except UnidentifiedImageError:
        raise HTTPException(status_code=400, detail="이미지 파일을 인식할 수 없습니다.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"파일 처리 중 오류: {str(e)}")

    try:
        # YOLO 예측
        result = model.predict(image)
        r = result[0]

        predictions = []
        for box in r.boxes:
            cls_id = int(box.cls)
            cls_name = r.names[cls_id]
            confidence = float(box.conf)
            predictions.append({
                "class": cls_name,
                "confidence": confidence
            })

        return {"predictions": predictions}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"예측 중 오류: {str(e)}")
    

# Chroma DB 위치와 임베딩 초기화
persist_directory = "./chroma_db"

# api key 호출 
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)

# Chroma 벡터 DB 로드
vectordb = Chroma(
    persist_directory=persist_directory,
    embedding_function=embeddings
)

# Retriever 생성 
retriever = vectordb.as_retriever(search_kwargs={"k": 1})

# OpenAI GPT 대화형 모델 초기화
llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)

# RetrievalQA 체인 생성 (검색 후 요약/생성)
qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)

# 요청 모델 정의
# 입력 모델: 질병명만 받음
class DiseaseRequest(BaseModel):
    disease_name: str

@app.post("/generate_questions")
async def generate_questions(request: DiseaseRequest):
    disease_name = request.disease_name
    query = f"""
    당신은 의학 전문가입니다.
    "{disease_name}"이라는 피부 질환에 대해 진단하기 위한 질문 3가지를 생성해주세요.

    조건:
    - 각 질문은 사용자가 "예"라고 대답했을 때 "{disease_name}"일 가능성이 높아지도록 작성하세요.
    - 부정 표현(예: 아닌가요?)은 절대 사용하지 마세요.
    - 질문 외에 아무 설명도 하지 마세요.
    - 질문은 마크다운 없이 순수 텍스트로 출력하세요.
    - 이건 퀴즈가 아니라 환자에게 물어보는 질병 진단용입니다. 
    - '예', '아니오' 중 하나로 답할 수 있는 질문을 하세요.
    - 출력은 반드시 다음 형식을 따르세요:
    ["질문1", "질문2", "질문3"]
    """
    try:
        answer = qa_chain.run(query)
        
        # 문자열로 오면 JSON 파싱
        questions = json.loads(answer) if isinstance(answer, str) else answer
        
        return {"disease": disease_name, "questions": questions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

class DiseaseRequest(BaseModel):
    disease_name: str

@app.post("/get_disease_info")
async def get_disease_info(request: DiseaseRequest):
    disease_name = request.disease_name

    query = f"""
    피부 질환 '{disease_name}'에 대한 정보를 요약해주세요. 다음 항목을 포함해 주세요:
    정의: (1~2줄)
    주요 원인: (1~2줄)
    치료 방법: (1~2줄)
    항목별로 번호를 붙여서 요약하세요.
    """

    try:
        response = qa_chain.run(query)
        return {"info": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))