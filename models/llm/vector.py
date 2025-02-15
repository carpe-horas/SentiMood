# 벡터 DB 차원 확인

import faiss
import os
from langchain_huggingface import HuggingFaceEmbeddings

# 현재 스크립트 파일이 있는 디렉토리를 기준으로 BASE_DIR 설정
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# 모델 경로 설정 (현재 `data/models/Qwen2.5-3B`에 있음)
MODEL_PATH = os.path.normpath(os.path.join(BASE_DIR, "data", "models", "Qwen2.5-3B"))

# FAISS 벡터 DB 경로 설정
vector_db_path = os.path.normpath(os.path.join(BASE_DIR, "data", "db", "faiss"))

index_path = os.path.join(vector_db_path, "index.faiss")

if not os.path.exists(index_path):
    print(f"FAISS 인덱스 파일이 없습니다: {index_path}")
else:
    index = faiss.read_index(index_path)
    print(f"FAISS 벡터 차원: {index.d}")

# 현재 사용 중인 임베딩 모델 로드
embeddings = HuggingFaceEmbeddings()

# 임베딩 모델이 생성하는 벡터 차원 확인
test_vector = embeddings.embed_query("테스트 문장")
embedding_dimension = len(test_vector)

print(f"현재 임베딩 모델이 생성하는 벡터 차원: {embedding_dimension}")