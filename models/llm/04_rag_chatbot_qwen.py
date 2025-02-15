import os
import sys
import torch
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from langchain_huggingface import HuggingFacePipeline
from langchain_huggingface import HuggingFaceEmbeddings  # ✅ OpenAIEmbeddings() 대신 사용

# 현재 스크립트 파일이 있는 디렉토리를 기준으로 BASE_DIR 설정
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# 모델 경로 설정 (현재 `data/models/Qwen2.5-3B`에 있음)
MODEL_PATH = os.path.normpath(os.path.join(BASE_DIR, "data", "models", "Qwen2.5-3B"))

# FAISS 벡터 DB 경로 설정
vector_db_path = os.path.normpath(os.path.join(BASE_DIR, "data", "db", "faiss"))

# 모델 폴더 확인
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"모델 폴더를 찾을 수 없습니다: {MODEL_PATH}")

# 모델 및 토크나이저 로드 (로컬 파일 전용)
print(f"로컬 Qwen2.5-3B 모델 로드 중... ({MODEL_PATH})")

try:
    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, local_files_only=True)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_PATH,
        torch_dtype=torch.float32,
        device_map="cpu",
        local_files_only=True
    )
    print("로컬 모델 로드 완료")
except Exception as e:
    print(f"모델 로드 중 오류 발생: {e}")
    sys.exit(1)

# 텍스트 생성 파이프라인 설정 (추론 모드)
hf_pipeline = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    max_new_tokens=256,
    temperature=0.7,
    repetition_penalty=1.2
)

# LangChain의 HuggingFacePipeline으로 감싸기
llm = HuggingFacePipeline(pipeline=hf_pipeline)

# ✅ FAISS 벡터 DB 로드 (HuggingFaceEmbeddings 사용)
vectorstore = FAISS.load_local(vector_db_path, HuggingFaceEmbeddings(), allow_dangerous_deserialization=True)

# 대화 기반 검색을 위한 Retriever 설정
retriever = vectorstore.as_retriever()

# 메모리 설정 (대화 히스토리 저장) + output_key 설정
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True, output_key="answer")

# 챗봇 프롬프트 설정
prompt = PromptTemplate.from_template(
    """당신은 고민을 들어주고 공감하며 상담을 도와주는 사춘기 청소년 대상 전문 AI 챗봇입니다.  
사용자가 고민을 이야기하면 **친절하고 따뜻한 말투**로 공감한 후,  
항상 **추가적인 적절한 질문을 던져** 대화를 자연스럽게 이어가세요. 
만약 사용자의 고민과 유사한 상담 사례가 있다면, 해당 내용을 기반으로 도움을 주세요. 
그러나 직접적인 해결책을 강요하지 말고, 사용자가 스스로 답을 찾을 수 있도록 도와주세요.  
사용자가 편안하게 속마음을 이야기할 수 있도록 친근한 표현을 사용하세요.
청소년의 친구 같은 말투를 사용하세요.  

**상담 원칙**  
- 사용자의 감정을 **먼저 인정하고** 따뜻한 말로 반응합니다. 
- **무조건** 마지막에는 열린 질문을 던져, 사용자가 계속 이야기할 수 있도록 합니다.  
- 사용자의 고민을 듣고 **같이 공감하며 질문을 던져** 대화를 이어갑니다.  
- 사용자의 경험을 **그대로 이해하고, 왜곡하지 않습니다.**  
- **사용자가 직접 경험한 일만** 바탕으로 대화를 이어갑니다.  
- **추측하지 않고**, 사용자의 말에서 나온 정보만 사용하여 답변합니다. 
- 사용자의 감정을 우선적으로 반영하며, **잘못된 해석을 하지 않습니다.**  
- 사용자가 겪은 일이 아니라면 **명확한 질문을 던지고 확인합니다.** 
- 단순한 정보 전달이 아닌, **친근하고 자연스럽게 대화하는 방식**을 사용합니다.  
- RAG 검색 결과를 참고하되, **무조건 정보를 나열하지 말고** 사용자의 감정에 초점을 맞춰 답변합니다.  
- 너무 논리적인 설명을 나열하지 말고, 자연스럽게 대화를 이어갑니다.
- "전문가와 상담하세요" 같은 기계적인 표현을 최소화하고, 사용자가 스스로 털어놓도록 유도합니다. 
- 없는 이야기를 지어서 말하

**이렇게 답변하지 마세요!**  
- "많은 사람들이 그렇습니다. 상담을 받아보세요." (너무 일반적)  
- "기분이 안 좋은 이유는 여러 가지가 있습니다."(공감 부족)  
- "해결 방법은 이러이러합니다." (강요하는 느낌) 
- "힘든 일이 있을 수 있어요. 잘 해결되길 바랍니다." (대화 단절) 

**좋은 상담 예시**  
👤 사용자: "나 너무 힘들어."  
🤖 챗봇: "그렇군요.. 요즘 많이 지치셨겠어요. 무슨 일이 있으셨나요? 제가 들어드릴게요. 😊"  

👤 사용자: "학교에서 친구랑 싸웠어."  
🤖 챗봇: "저런.. 속상하셨겠어요. 친구와 다투면 마음이 많이 복잡해지죠. 어떤 일 때문에 다투게 되었나요?"  

👤 사용자: "길 가다가 넘어졌어."  
잘못된 응답: "아, 친구가 다쳐서 속상하시겠어요."  (잘못된 해석)  
올바른 응답: "많이 놀라셨겠어요. 어디 다친 곳은 없나요?"  (사용자의 경험 그대로 반영)  
---

💬 **사용자의 고민:**  
{question}  

📂 **참고할 상담 사례:**  
{context}  

🤖 **챗봇 응답:**  
"""
)

# Conversational RAG 설정 (검색 + 대화) + output_key 설정
conversation_rag = ConversationalRetrievalChain.from_llm(
    llm=llm,
    retriever=retriever,
    memory=memory,
    return_source_documents=True,
    combine_docs_chain_kwargs={"prompt": prompt},
    output_key="answer"
)

print("Conversational RAG 챗봇 설정 완료")
print("\n챗봇과 대화를 시작하세요. (종료하려면 'exit' 또는 'quit' 입력)\n")

# 챗봇 실행 함수 (사용자 입력을 받아 계속 대화)
def chat_with_bot():
    while True:
        user_input = input("\n당신: ")

        if user_input.lower() in ["exit", "quit"]:
            print("\n대화를 종료합니다. 다음에 또 만나요.\n")
            break

        # 챗봇 응답
        response = conversation_rag.invoke({"question": user_input})
        answer = response["answer"]

        print("\n챗봇:\n", answer)


# 대화 실행
if __name__ == "__main__":
    chat_with_bot()
