import os
import pandas as pd
import faiss
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings

# 현재 스크립트 파일 기준으로 BASE_DIR 설정
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# 파일 경로 설정
csv_file_path = os.path.normpath(os.path.join(BASE_DIR, "data", "total_kor_counsel_bot_clean.csv"))
vector_db_path = os.path.normpath(os.path.join(BASE_DIR, "data", "db", "faiss"))

# CSV 파일 로드
loader = CSVLoader(file_path=csv_file_path, encoding="utf-8")
data = loader.load()
print(f"{len(data)}개의 상담 데이터 로드 완료.")

# 텍스트 분할 (청크 단위)
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
splits = text_splitter.split_documents(data)
print(f"데이터 분할 완료: 총 {len(splits)}개의 청크 생성됨.")

# Qwen2.5-3B 모델에 맞는 임베딩 (768차원)
qwen_embeddings = HuggingFaceEmbeddings(model_name="Qwen/Qwen2.5-3B")

# FAISS 벡터 DB 생성 (768차원)
vectorstore = FAISS.from_documents(documents=splits, embedding=qwen_embeddings)

# 벡터 DB 로컬 저장 (index_qwen.faiss)
vectorstore.save_local(vector_db_path, index_name="index_qwen")

print(f"벡터 DB 저장 완료: {os.path.join(vector_db_path, 'index_qwen.faiss')}")

# 저장된 벡터 DB의 차원 확인
index_path = os.path.join(vector_db_path, "index_qwen.faiss")

if os.path.exists(index_path):
    index = faiss.read_index(index_path)
    print(f"FAISS 벡터 차원: {index.d}")  # 768이어야 정상
else:
    print(f"FAISS 인덱스 파일을 찾을 수 없습니다: {index_path}")
