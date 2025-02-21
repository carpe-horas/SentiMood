import pymongo
from bson import ObjectId
from werkzeug.exceptions import NotFound
from app.database import mongo
from app.services.rag_service import retrieve_relevant_documents
from app.services.llm_service import generate_response
from app.models.chat import save_chat
from datetime import datetime
from flask import current_app

def chat_with_bot(user_id: str, session_id: str, user_message: str, emotion_id=None, confidence=None, test_mode=False) -> dict:
    """
    사용자의 메시지를 받아 RAG 검색 및 LLM을 이용해 챗봇 응답을 생성하는 함수

    :param user_id: 사용자의 고유 ID
    :param session_id: 현재 대화 세션의 ID
    :param user_message: 사용자의 입력 메시지
    :param emotion_id: 감정 분석 결과 ID
    :param test_mode: True이면 DB 저장 없이 응답만 반환 (기본값 False)
    :return: 챗봇 응답 JSON
    """
    try:
        # user_id가 없으면 테스트 모드로 전환 및 기본 user_id 할당
        if not user_id:
            test_mode = True
            user_id = "test_user"

        if mongo.db is None:
            raise RuntimeError("MongoDB가 올바르게 초기화되지 않았습니다.")
        
        # RAG 검색 수행 (관련 상담 사례 검색)
        retrieved_documents = retrieve_relevant_documents(user_message)

        # 검색 결과 처리
        if retrieved_documents:
            retrieved_context = "\n".join(
                doc.metadata["output"].strip() if "output" in doc.metadata else str(doc)
                for doc in retrieved_documents
            )
            retrieved_status = "반영됨"
        else:
            retrieved_context = "상담 기록이 없습니다."
            retrieved_status = "반영 안 됨"

        # LLM을 활용하여 최종 챗봇 응답 생성
        bot_response = generate_response(user_message, retrieved_context)

        # 대화 내용 저장
        # test_mode인 경우 DB 저장을 건너뛰고 바로 반환
        if not test_mode:
            chat_data = save_chat(user_id, session_id, user_message, bot_response, emotion_id, False, confidence)
            chat_id = str(chat_data)
        else:
            chat_id = "test_chat_id"

        # JSON 형식의 응답 반환
        return {
            "user_message": user_message,
            "retrieved_documents": retrieved_status,
            "bot_response": bot_response,
            #"chat_id": str(chat_data["_id"])
            "chat_id": chat_id
        }

    except pymongo.errors.PyMongoError as e:
        raise RuntimeError(f"MongoDB 오류 발생: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"챗봇 응답 생성 중 오류 발생: {str(e)}")


def get_chat_history(session_id: str, limit: int = 10) -> list:
    """
    특정 세션의 대화 기록 조회

    :param session_id: 조회할 채팅 세션 ID
    :param limit: 가져올 대화 개수 (기본값: 10)
    :return: 대화 목록
    """
    try:
        with current_app.app_context():  
            chats = mongo.db.chats.find({"session_id": session_id}).sort("timestamp", -1).limit(limit)
            history = [{"_id": str(chat["_id"]), **chat} for chat in chats]
            return history
    except pymongo.errors.PyMongoError as e:
        raise RuntimeError(f"MongoDB 조회 오류: {str(e)}")

def end_chat_session(user_id: str) -> dict:
    """
    사용자의 대화 세션을 종료하는 함수

    :param user_id: 사용자의 고유 ID
    :return: 종료된 대화 개수
    """
    result = mongo.db.chats.update_many(
        {"user_id": user_id, "conversation_end": False},
        {"$set": {"conversation_end": True}}
    )
    return {"message": f"{result.modified_count}개의 대화가 종료되었습니다."}


def create_chat_session(user_id: str) -> str:
    """
    새로운 채팅 세션을 생성하는 함수

    :param user_id: 사용자의 고유 ID
    :return: 생성된 세션 ID
    """
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    session_id = f"{user_id}_{timestamp}"
    return session_id


def get_user_chat_history(user_id: str) -> list:
    """
    특정 사용자의 모든 채팅 세션을 조회하는 함수

    :param user_id: 사용자의 고유 ID
    :return: 사용자의 채팅 세션 목록
    """
    sessions = mongo.db.chats.distinct("session_id", {"user_id": user_id})
    return sessions


def delete_chat_message(message_id: str) -> bool:
    """
    특정 메시지를 삭제하는 함수

    :param message_id: 삭제할 메시지의 ObjectId
    :return: 삭제 성공 여부
    """
    try:
        result = mongo.db.chats.delete_one({"_id": ObjectId(message_id)})
        if result.deleted_count == 0:
            raise NotFound("삭제할 메시지를 찾을 수 없습니다.")
        return True
    except pymongo.errors.PyMongoError as e:
        raise RuntimeError(f"MongoDB 삭제 오류: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"메시지 삭제 중 오류 발생: {str(e)}")