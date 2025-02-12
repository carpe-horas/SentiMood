# Ai-RobotPet






### 폴더구조
```
📦 AI-ROBOTPET
├── 📂 data
│   ├── 📂 raw
│   ├── 📂 db # 벡터db
│   └── 📄 total_kor_counsel_bot_clean.csv  # 원본 상담 데이터
├── 📂 models
│   ├── 📄 01_jsonl_to_csv.ipynb  # JSONL 데이터를 CSV로 변환
│   ├── 📄 02_save_vector_db.ipynb  # 상담 데이터를 벡터DB로 변환하여 저장
│   ├── 📄 03_load_vector_db.ipynb  # 저장된 벡터DB 로드하여 활용
│   └── 📄 04_rag_chatbot.ipynb  # RAG 챗봇 구현 코드
├── 📄 .env  
├── 📄 .gitattributes  # Git 속성 설정
├── 📄 .gitignore  
├── 📄 README.md  
└── 📄 requirements.txt  # 프로젝트 의존성 패키지 목록


```

### 실행 방법
1. git clone
2. 가상환경 실행
3. 라이브러리 설치
```bash
pip install -r requirements.txt
```

### .env
- 아래 내용 기입하여 별도 생성 필요
```bash
OPENAI_API_KEY=
```