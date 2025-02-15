import os
import faiss
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
index_qwen_path = os.path.join(vector_db_path, "index_qwen.faiss")
pkl_qwen_path = os.path.join(vector_db_path, "index_qwen.pkl")

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
batch_size = 2000  # 메모리 문제 방지 (2000개씩 처리)
num_batches = len(splits) // batch_size + (1 if len(splits) % batch_size != 0 else 0)

# 새로운 FAISS 인덱스 생성
index = None
all_metadatas = []

for i in range(num_batches):
    batch = splits[i * batch_size : (i + 1) * batch_size]
    print(f"배치 {i+1}/{num_batches} - {len(batch)}개 청크 벡터화 중...")

    start_time = time.time()  
    vectorstore = FAISS.from_documents(documents=batch, embedding=qwen_embeddings)
    end_time = time.time()
    print(f"벡터화 완료 (소요 시간: {end_time - start_time:.2f}초)")

    # 기존 인덱스와 병합
    if index is None:
        index = vectorstore.index
        all_metadatas.extend(vectorstore.docstore._dict.values())  
    else:
        index.merge_from(vectorstore.index)
        all_metadatas.extend(vectorstore.docstore._dict.values())  

    # 중간 저장
    faiss.write_index(index, index_qwen_path)
    vectorstore.save_local(vector_db_path, index_name="index_qwen")
    print(f"중간 저장 완료: {index_qwen_path}, {pkl_qwen_path}")

# 최종 벡터 DB 저장
faiss.write_index(index, index_qwen_path)
vectorstore.save_local(vector_db_path, index_name="index_qwen")
print(f"최종 벡터 DB 저장 완료: {index_qwen_path}, {pkl_qwen_path}")

# 저장된 벡터 DB의 차원 확인
if os.path.exists(index_qwen_path):
    index = faiss.read_index(index_qwen_path)
    print(f"FAISS 벡터 차원: {index.d}")  
else:
    print(f"FAISS 인덱스 파일을 찾을 수 없습니다: {index_qwen_path}")
