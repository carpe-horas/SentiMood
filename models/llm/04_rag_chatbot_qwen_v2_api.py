# chatbot_api.py (Flask API 버전)

from flask import Flask, request, jsonify
import os
import pandas as pd
from dotenv import load_dotenv
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate

# ✅ Flask 앱 생성
app = Flask(__name__)

# ✅ .env 파일 로드
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("⚠️ OpenAI API Key가 없습니다. .env 파일을 확인하세요.")

# ✅ 말투 데이터셋 로드
style_data_path = "data/tone_dataset.csv"
df = pd.read_csv(style_data_path)

# ✅ 벡터 DB 로드
vectorstore = FAISS.load_local("data/db/faiss", OpenAIEmbeddings(), allow_dangerous_deserialization=True)
retriever = vectorstore.as_retriever()
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True, output_key="answer")
llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.7)

conversation_rag = ConversationalRetrievalChain.from_llm(
    llm=llm,
    retriever=retriever,
    memory=memory,
    return_source_documents=True
)

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("user_input", "")

    # ✅ RAG 검색
    response = conversation_rag.invoke({"question": user_input})
    answer = response["answer"]

    return jsonify({"user_input": user_input, "chatbot_response": answer})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
