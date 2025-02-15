import os
import faiss
import pickle
import time
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings

# 현재 스크립트 파일 기준으로 BASE_DIR 설정
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# 파일 경로 설정
csv_file_path = os.path.normpath(os.path.join(BASE_DIR, "data", "total_kor_counsel_bot_clean.csv"))
vector_db_path = os.path.normpath(os.path.join(BASE_DIR, "data", "db", "faiss"))
index_qwen_faiss = os.path.join(vector_db_path, "index_qwen.faiss")
index_qwen_pkl = os.path.join(vector_db_path, "index_qwen.pkl")

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

# 배치 설정
batch_size = 2000  
num_batches = len(splits) // batch_size + (1 if len(splits) % batch_size != 0 else 0)

# 기존 벡터 DB가 있으면 로드
if os.path.exists(index_qwen_faiss) and os.path.exists(index_qwen_pkl):
    print("기존 벡터 DB 발견, 로드 중...")
    index = faiss.read_index(index_qwen_faiss)
    
    with open(index_qwen_pkl, "rb") as f:
        stored_metadata = pickle.load(f)

    # 진행한 배치 개수 확인
    completed_batches = len(stored_metadata) // batch_size
    print(f"이전 진행 상태 감지: {completed_batches}/{num_batches} 배치 완료됨.")
else:
    print("새로운 벡터 DB 생성 시작...")
    index = None
    stored_metadata = []
    completed_batches = 0

# 중단된 배치 이후부터 재시작
for i in range(completed_batches, num_batches):
    batch = splits[i * batch_size : (i + 1) * batch_size]
    print(f"\n배치 {i+1}/{num_batches} - {len(batch)}개 청크 벡터화 중...")

    start_time = time.time()  
    vectorstore = FAISS.from_documents(documents=batch, embedding=qwen_embeddings)
    end_time = time.time()
    print(f"벡터화 완료 (소요 시간: {end_time - start_time:.2f}초)")

    # 기존 인덱스와 병합
    if index is None:
        index = vectorstore.index
    else:
        index.merge_from(vectorstore.index)

    # 메타데이터 저장
    stored_metadata.extend([doc.metadata for doc in batch])

    # 중간 저장 (중단 후 이어서 진행 가능)
    faiss.write_index(index, index_qwen_faiss)
    with open(index_qwen_pkl, "wb") as f:
        pickle.dump(stored_metadata, f)

    print(f"중간 저장 완료: {index_qwen_faiss}, {index_qwen_pkl}")

# 최종 벡터 DB 저장
faiss.write_index(index, index_qwen_faiss)
with open(index_qwen_pkl, "wb") as f:
    pickle.dump(stored_metadata, f)

print(f"\n최종 벡터 DB 저장 완료: {index_qwen_faiss}, {index_qwen_pkl}")

# 저장된 벡터 DB의 차원 확인
if os.path.exists(index_qwen_faiss):
    index = faiss.read_index(index_qwen_faiss)
    print(f"FAISS 벡터 차원: {index.d}")  
else:
    print(f"FAISS 인덱스 파일을 찾을 수 없습니다: {index_qwen_faiss}")
