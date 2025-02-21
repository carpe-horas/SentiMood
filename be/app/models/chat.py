from datetime import datetime
from flask_pymongo import PyMongo

mongo = PyMongo()  

def generate_session_id(user_id):
    """새로운 대화 시작 시 자동으로 세션 ID 생성"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S") 
    return f"{user_id}_{timestamp}" 

def end_previous_session(user_id):
    """새로운 대화가 시작되면 기존 대화 자동 종료"""
    mongo.db.chats.update_many(
        {"user_id": user_id, "conversation_end": False},
        {"$set": {"conversation_end": True}}
    )

def auto_end_sessions_by_date():
    """날짜가 바뀌면 미종료된 대화 자동 종료"""
    now = datetime.now()
    today_start = datetime(now.year, now.month, now.day) 

    mongo.db.chats.update_many(
        {"conversation_end": False, "timestamp": {"$lt": today_start}},
        {"$set": {"conversation_end": True}}
    )

def save_chat(user_id: str, session_id: str, user_message: str, bot_response: str, emotion_id=None, conversation_end=False, confidence=None):
    try:
        chat_data = {
            "user_id": user_id,
            "session_id": session_id,
            "user_message": user_message,
            "bot_response": bot_response,
            "emotion_id": emotion_id,
            "conversation_end": conversation_end,
            "confidence": confidence,
            "timestamp": datetime.now()
        }
        result = mongo.db.chats.insert_one(chat_data)
        return result.inserted_id
    except Exception as e:
        print(f"MongoDB 삽입 오류: {e}")
        raise RuntimeError(f"MongoDB 삽입 오류: {e}")

def create_indexes():
    """MongoDB에 필요한 인덱스 추가 (조회 성능 개선)"""
    mongo.db.chats.create_index([("user_id", 1)])
    mongo.db.chats.create_index([("session_id", 1)])
    mongo.db.chats.create_index([("timestamp", -1)])
