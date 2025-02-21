from flask import Blueprint, request, jsonify, current_app
from werkzeug.exceptions import BadRequest, NotFound, InternalServerError
from app.services.chat_service import (
    save_chat, 
    get_chat_history, 
    end_chat_session,
    create_chat_session, 
    get_user_chat_history, 
    delete_chat_message,
    chat_with_bot  
)

from app.services.rag_service import preview_rag_search

chat_bp = Blueprint("chat", __name__)

@chat_bp.route("/session", methods=["POST"])
def create_session():
    """새로운 채팅 세션 생성"""
    data = request.json
    user_id = data.get("user_id")

    if not user_id:
        return jsonify({"error": "user_id가 필요합니다."}), 400

    session_id = create_chat_session(user_id)
    return jsonify({"session_id": session_id}), 201


@chat_bp.route("/message", methods=["POST"])
def create_chat():
    """새로운 챗봇 대화 저장"""
    try:
        data = request.get_json()
        if not data:
            raise BadRequest("JSON 데이터를 전달해야 합니다.")

        user_id = data.get("user_id")
        session_id = data.get("session_id")
        user_message = data.get("user_message")
        bot_response = data.get("bot_response")
        emotion_id = data.get("emotion_id", None)
        confidence = data.get("confidence", None)
        conversation_end = data.get("conversation_end", False)

        if not all([user_id, session_id, user_message, bot_response]):
            raise BadRequest("필수 값이 누락되었습니다.")

        chat_data = save_chat(user_id, session_id, user_message, bot_response, emotion_id, conversation_end, confidence)
        return jsonify(chat_data), 201

    except BadRequest as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "서버 내부 오류"}), 500


@chat_bp.route("/<session_id>", methods=["GET"])
def get_chat(session_id):
    """특정 세션의 대화 기록 조회
        (이전 대화 기록 불러오기) """
    try:
        limit = int(request.args.get("limit", 10))
        history = get_chat_history(session_id, limit)
        return jsonify(history), 200
    except Exception as e:
        return jsonify({"error": "서버 내부 오류"}), 500


@chat_bp.route("/<session_id>/end", methods=["PUT"])
def close_chat(session_id):
    """특정 세션의 대화 종료
        (대화종료)"""
    try:
        result = end_chat_session(session_id)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": "서버 내부 오류"}), 500


@chat_bp.route("/history/<user_id>", methods=["GET"])
def get_chat_history(user_id):
    """특정 사용자의 모든 채팅 세션 조회"""
    sessions = get_user_chat_history(user_id)
    return jsonify({"sessions": sessions}), 200


@chat_bp.route("/preview", methods=["POST"])
def preview_rag():
    """RAG 검색 결과 미리보기
    (어떤 사례를 검색하는지 확인)"""
    data = request.json
    user_message = data.get("user_message")

    if not user_message:
        return jsonify({"error": "user_message가 필요합니다."}), 400

    search_results = preview_rag_search(user_message)
    return jsonify({"retrieved_documents": search_results}), 200


@chat_bp.route("/message/<message_id>", methods=["DELETE"])
def delete_message(message_id):
    """특정 메시지 삭제"""
    try:
        result = delete_chat_message(message_id)
        if not result:
            raise NotFound("메시지를 찾을 수 없습니다.")

        return jsonify({"message": "삭제 완료"}), 200

    except NotFound as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": "서버 내부 오류"}), 500
    

@chat_bp.route("/rag-response", methods=["POST"])
def chat_rag_response():
    """
    RAG 기반 상담 챗봇 응답 API
    요청 형식:
    {
        "user_message": "요즘 너무 우울해."
    }
    응답 형식:
    {
        "user_message": "요즘 너무 우울해.",
        "retrieved_documents": "반영됨" 또는 "반영 안 됨",
        "bot_response": "챗봇의 최종 응답"
    }
    """
    try:
        data = request.get_json()
        user_message = data.get("user_message", "").strip()
        
        if not user_message:
            return jsonify({"error": "user_message는 필수 입력값입니다."}), 400
        
        # 테스트 용도: user_id와 session_id를 고정값으로 설정하고 test_mode 활성화
        user_id = "test_user"
        session_id = "test_session"

        # test_mode=True를 전달하여 DB 저장 없이 응답만 반환
        response = chat_with_bot(user_id, session_id, user_message, test_mode=True)

        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

