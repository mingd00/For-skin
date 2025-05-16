import json
import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from dotenv import load_dotenv
from langchain.embeddings.openai import OpenAIEmbeddings

# 1. JSON 데이터 불러오기
with open("scripts/diagnose_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# 2. 텍스트 분할용 청킹 설정
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    separators=["\n\n", "\n", ".", "!", "?"]
)

# 3. 텍스트 청킹 및 문서 리스트 생성
documents = []
for item in data:
    text = item["text"]
    metadata = item.get("metadata", {})
    chunks = splitter.split_text(text)
    for chunk in chunks:
        documents.append({"text": chunk, "metadata": metadata})

# 4. Embedding 생성기 초기화(OpenAI Embeddings 사용 예)
# .env 파일에서 환경변수 읽어오기
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)

# 5. 텍스트와 메타데이터를 LangChain 문서 객체로 변환
from langchain.schema import Document

docs = [Document(page_content=doc["text"], metadata=doc["metadata"]) for doc in documents]

# 6. Chroma 벡터 DB 생성 (local persistence 경로 설정)
persist_directory = "./chroma_db"

vectordb = Chroma.from_documents(
    documents=docs,
    embedding=embeddings,
    persist_directory=persist_directory
)

# 7. DB 저장(디스크에 영속화)
vectordb.persist()

print("Chroma DB 생성 및 저장 완료")
