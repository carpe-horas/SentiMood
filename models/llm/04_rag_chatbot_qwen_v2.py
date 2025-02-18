# chatbot.py

import os
import pandas as pd
import sys
from dotenv import load_dotenv
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate

# .env 파일 로드 (OpenAI API Key)
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("⚠️ OpenAI API Key가 없습니다. .env 파일을 확인하세요.")

# 말투 데이터셋 로드
style_data_path = os.path.join(os.path.dirname(__file__), "data/tone_dataset.csv")  # 경로 조정
df = pd.read_csv(style_data_path)

# 랜덤하게 5개의 예제 선택
style_examples = "\n".join([
    f"- 원본: {row['original']}\n  - 변환: {row['converted']}" 
    for _, row in df.sample(5).iterrows()
])

# LangChain ChatPromptTemplate 설정
prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(
        """당신은 청소년 고민 상담을 도와주는 AI 챗봇입니다.  
사용자가 편안하게 대화를 나눌 수 있도록, 친구처럼 자연스럽게 말해 주세요.  
응답을 생성할 때, 아래 스타일 예제를 참고해서 대화 스타일을 유지하세요.

**말투 스타일 예제 (Few-shot 데이터셋 기반)**:  
{style_examples}

**사용자 입력**:  
"""
    ),
    HumanMessagePromptTemplate.from_template("{user_input}")
])

# 벡터 DB 로드
vectorstore = FAISS.load_local("data/db/faiss", OpenAIEmbeddings(), allow_dangerous_deserialization=True)

# 대화 기반 검색을 위한 Retriever 설정
retriever = vectorstore.as_retriever()

# Memory 설정 (대화 이력 저장)
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True, output_key="answer")

# Conversational RAG 설정
llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.7)

conversation_rag = ConversationalRetrievalChain.from_llm(
    llm=llm,
    retriever=retriever,
    memory=memory,
    return_source_documents=True,
    combine_docs_chain_kwargs={"prompt": prompt}  # 프롬프트 반영
)

print("Conversational RAG 설정 완료!")


def get_relevant_rag_response(user_input):
    """RAG 검색 실행 후, 결과가 적절한지 판단"""
    response = conversation_rag.invoke({"question": user_input})
    answer = response["answer"]

    # 검색 결과가 의미 있는 경우만 반환
    if len(answer) > 5:  # 의미 있는 답변인지 간단히 체크 (길이 기준)
        return answer
    else:
        return None  # 의미 없는 경우 RAG 결과 사용 안 함


def chat_with_bot():
    """CLI 모드에서 챗봇 실행"""
    print("고민 상담 챗봇 시작! (종료는 'exit' 입력)")

    while True:
        user_input = input("👤 사용자: ")
        print("👤 사용자:", user_input)
        sys.stdout.flush()

        if user_input.lower() in ["exit", "quit"]:
            print("상담 챗봇 종료!")
            break

        # 항상 RAG 실행
        rag_response = get_relevant_rag_response(user_input)

        # ✅ 최종 프롬프트에 데이터 적용
        final_prompt = prompt.format(
            style_examples=style_examples,  # 말투 데이터셋 반영
            user_input=user_input
        )

        # LLM 호출 (RAG 응답이 있으면 포함)
        if rag_response:
            final_prompt += f"\n📂 참고할 상담 사례:\n{rag_response}"

        # LLM이 최종 응답 생성
        final_answer = llm.invoke(final_prompt)

        print("\n🤖 챗봇:\n", final_answer)
        sys.stdout.flush()


if __name__ == "__main__":
    chat_with_bot()
