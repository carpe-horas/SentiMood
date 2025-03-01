from flask import Blueprint, request, jsonify
import base64
import cv2
import numpy as np
from app.models.emotion import load_emotion_model, predict_emotion
from app.services.emotion_service import (
    save_emotion_data,
    get_emotion_results,
    delete_emotion_results,
    auto_end_emotions,
    get_model_status,
    get_user_emotion_history,
    get_most_common_emotion,
    get_emotion_statistics,
    is_authorized,
)
from app.utils.auth import jwt_required_without_bearer, login_required
import logging
import uuid
from bson import ObjectId  


emotion_bp = Blueprint("emotion", __name__)
model = load_emotion_model()


# 감정 예측 API (웹캠 프레임 처리)
@emotion_bp.route("/predict", methods=["POST"])
@jwt_required_without_bearer  # JWT 인증 추가
def predict():
    """웹캠 스트림에서 전송된 프레임을 받아 실시간으로 감정을 예측"""
    try:
        user_id = request.user_id
        chatroom_id = request.json.get("chatroom_id")
        frame_data = request.json.get("frame")

        if not all([user_id, chatroom_id, frame_data]):
            return jsonify({"message": "필수 필드가 누락되었습니다."}), 400

        # Base64 디코딩 및 이미지 변환
        image_data = base64.b64decode(frame_data.split(",")[1])  # "data:image/jpeg;base64," 부분을 제외하고 디코딩
        np_array = np.frombuffer(image_data, np.uint8)
        image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)

        if image is None:
            return jsonify({"message": "유효하지 않은 이미지 데이터입니다."}), 400

        # 감정 예측
        emotion_label, confidence = predict_emotion(image, model)

        print(f"예측된 감정: {emotion_label}, 신뢰도: {confidence}")

        # 신뢰도가 70% 이상인 경우에만 저장
        if confidence >= 0.7:
            save_emotion_data(user_id, chatroom_id, emotion_label, confidence)

        return jsonify(
            {
                "emotion": emotion_label,
                "confidence": confidence,
                "message": "감정 분석이 성공적으로 수행되었습니다.",
            }
        ), 200

    except Exception as e:
        logging.error(f"감정 예측 실패: {e}")
        return jsonify({"error": "감정 예측 실패"}), 500


# 감정 데이터 저장 API
@emotion_bp.route("/save-emotion", methods=["POST"])
@jwt_required_without_bearer  # JWT 인증 추가
def save_emotion():
    """실시간으로 인식된 감정 데이터를 MongoDB에 저장"""
    try:
        user_id = request.user_id  # JWT에서 추출한 user_id
        chatroom_id = request.json.get("chatroom_id")
        emotion = request.json.get("emotion")
        confidence = request.json.get("confidence")

        if not all([user_id, chatroom_id, emotion, confidence]):
            return jsonify({"message": "필수 필드가 누락되었습니다."}), 400
        
        # emotion_id 생성
        emotion_id = str(uuid.uuid4())

        save_emotion_data(user_id, chatroom_id, emotion, confidence, emotion_id)
        return jsonify({"success": True, "message": "감정 데이터 저장 성공"})

    except Exception as e:
        logging.error(f"[ERROR] /save-emotion: {e}")
        return jsonify({"message": f"오류 발생: {str(e)}"}), 500


# 특정 채팅방의 감정 데이터 조회 API
@emotion_bp.route("/results/<chatroom_id>", methods=["GET"])
@jwt_required_without_bearer  
def results(chatroom_id):
    """특정 채팅방의 감정 분석 결과 조회 (가장 많이 나타난 감정 포함)"""
    try:
        user_id = request.user_id  

        print(f"[DEBUG] 감정 데이터 요청: user_id={user_id}, chatroom_id={chatroom_id}")

        if not isinstance(chatroom_id, str):
            print(f"[ERROR] chatroom_id 형식 오류: {chatroom_id}")
            return jsonify({"message": "잘못된 chatroom_id 형식입니다."}), 400

        # 감정 데이터 조회 (가장 많이 등장한 감정 포함)
        results = get_emotion_results(chatroom_id, user_id)

        print(f"[DEBUG] 채팅방({chatroom_id}) 감정 데이터 응답: {results}")
        return jsonify(results)

    except Exception as e:
        print(f"[ERROR] /results/{chatroom_id}: {e}")
        return jsonify({"message": f"오류 발생: {str(e)}"}), 500


# 특정 채팅방의 감정 데이터 삭제 API
@emotion_bp.route("/results/<chatroom_id>", methods=["DELETE"])
@jwt_required_without_bearer  # JWT 인증 추가
def delete_results(chatroom_id):
    """특정 채팅방의 감정 분석 결과를 삭제"""
    try:
        user_id = request.user_id  # JWT에서 추출한 user_id

        # 권한 확인 (해당 채팅방의 감정 데이터에 접근 가능한지 확인)
        if not is_authorized(user_id, chatroom_id):
            return jsonify({"message": "접근 권한이 없습니다."}), 403

        success = delete_emotion_results(chatroom_id)
        return jsonify({"message": "삭제 성공" if success else "삭제 실패"})
    except Exception as e:
        return jsonify({"message": f"오류 발생: {str(e)}"}), 500


# 대화 종료 시 대표 감정 저장 API
@emotion_bp.route("/save-end-emotion", methods=["POST"])
@jwt_required_without_bearer  # JWT 인증 추가
def save_end_emotion():
    """대화 종료 시, 채팅방에서 가장 많이 감지된 감정을 저장"""
    try:
        user_id = request.user_id  # JWT에서 추출한 user_id
        chatroom_id = request.json.get("chatroom_id")

        if not all([chatroom_id, user_id]):
            return jsonify({"message": "필수 필드가 누락되었습니다."}), 400

        # 권한 확인 (해당 채팅방의 감정 데이터에 접근 가능한지 확인)
        if not is_authorized(user_id, chatroom_id):
            return jsonify({"message": "접근 권한이 없습니다."}), 403

        # 감정 데이터를 불러와서 가장 많이 감지된 감정 확인
        emotion_data = get_emotion_results(chatroom_id)
        most_common_emotion = get_most_common_emotion(emotion_data)

        # 감정 데이터를 저장
        save_emotion_data(
            user_id,
            chatroom_id,
            most_common_emotion["emotion"],
            most_common_emotion["confidence"],
        )
        return jsonify(
            {
                "message": "대화 종료 시 감정 데이터 저장 성공",
                "emotion": most_common_emotion,
            }
        )
    except Exception as e:
        return jsonify({"message": f"오류 발생: {str(e)}"}), 500


# 사용자 감정 분석 기록 조회 API
@emotion_bp.route("/history", methods=["GET"])
@jwt_required_without_bearer  
def user_history():
    """사용자의 감정 분석 기록을 조회"""
    try:
        user_id = request.user_id  

        # 사용자의 감정 기록 조회
        history = get_user_emotion_history(user_id)
        return jsonify(history)
    except Exception as e:
        return jsonify({"message": f"오류 발생: {str(e)}"}), 500


# 감정 통계 조회 API
@emotion_bp.route("/stats", methods=["GET"])
@jwt_required_without_bearer 
def emotion_stats():
    """사용자의 감정 통계를 조회 (주간, 월간 등)"""
    try:
        user_id = request.user_id 

        # 요청 파라미터에서 날짜 범위 추출
        start_date = request.args.get("start_date")  
        end_date = request.args.get("end_date")     

        # 감정 통계 조회
        stats = get_emotion_statistics(user_id, start_date, end_date)
        return jsonify({"message": "감정 통계 조회 성공", "stats": stats})
    except Exception as e:
        return jsonify({"message": f"오류 발생: {str(e)}"}), 500


# 감정 분석 모델 상태 확인 API
@emotion_bp.route("/status", methods=["GET"])
def model_status():
    """감정 분석 모델의 상태를 확인"""
    try:
        status = get_model_status(model)
        return jsonify({"status": status})
    except Exception as e:
        return jsonify({"message": f"오류 발생: {str(e)}"}), 500


# 미처리된 감정 데이터 자동 종료 API
@emotion_bp.route("/auto-end", methods=["POST"])
@jwt_required_without_bearer  # JWT 인증 추가
def auto_end():
    """날짜가 바뀌면 미종료된 감정 분석 데이터를 자동으로 종료"""
    try:
        ended_emotions = auto_end_emotions()
        return jsonify(
            {
                "message": "자동 종료된 감정 분석 데이터",
                "ended_emotions": ended_emotions,
            }
        )
    except Exception as e:
        return jsonify({"message": f"오류 발생: {str(e)}"}), 500
