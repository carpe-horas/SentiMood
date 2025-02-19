from flask import Blueprint, request, jsonify, current_app
from app.services.auth_service import (
    register_user,
    authenticate_user,
    generate_tokens,
    verify_token,
    reset_password,
    verify_email_status_service,
    verify_email_request_service,
    logout_service,
    send_verification_code_service,
    verify_email_service,
    validate_password,
    validate_email,
    generate_token,
    request_password_reset,
)
from jose import jwt
from app.models.users import User
import redis
import os

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")  
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))  
REDIS_DB = int(os.getenv("REDIS_DB", 0))  

r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)

# 블루프린트 설정
auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    """
    회원가입 API

    요청 형식:
    {
        "email": "example@email.com",
        "password": "SecurePassword123!",
        "confirm_password": "SecurePassword123!"
    }

    응답:
    201 Created
    {
        "message": "회원가입 성공. 이메일을 확인하세요."
    }
    """
    try:
        data = request.get_json()
        response = register_user(
            data["email"], 
            data["password"], 
            data.get("confirm_password")  # KeyError 방지
        )
        return jsonify(response), 201
    except ValueError as e:
        current_app.logger.error(f"Registration error: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Unexpected error in registration: {str(e)}")
        return jsonify({"error": "서버 오류가 발생했습니다."}), 500

# @auth_bp.route("/verify-email/<token>", methods=["GET"])
# def verify_email(token):
#     """
#     이메일 인증 API

#     요청: GET /auth/verify-email/<token>

#     응답:
#     200 OK
#     {
#         "message": "이메일 인증 성공"
#     }
#     """
#     try:
#         response = verify_email_token(token)
#         return jsonify(response), 200
#     except ValueError as e:
#         current_app.logger.error(f"Email verification error: {str(e)}")
#         return jsonify({"error": str(e)}), 400
#     except Exception as e:
#         current_app.logger.error(f"Unexpected error in email verification: {str(e)}")
#         return jsonify({"error": "서버 오류가 발생했습니다."}), 500

@auth_bp.route("/verify-email", methods=["POST"])
def verify_email():
    """
    이메일 인증 API (6자리 인증 코드 사용)

    요청 형식:
    {
        "email": "example@email.com",
        "code": "123456"
    }

    응답:
    200 OK
    {
        "message": "이메일 인증 성공"
    }
    """
    try:
        data = request.get_json()
        response = verify_email_service(data["email"], data["code"])  # 수정 완료
        return jsonify(response), 200
    except ValueError as e:
        current_app.logger.error(f"Email verification error: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Unexpected error in email verification: {str(e)}")
        return jsonify({"error": "서버 오류가 발생했습니다."}), 500


@auth_bp.route("/verify-email-status", methods=["GET"])
def verify_email_status():
    """
    이메일 인증 상태 확인 API
    사용자가 이메일을 입력하고 인증했는지 상태를 조회한다.

    요청 형식:
    GET /verify-email-status?email=example@email.com

    응답:
    {
        "verified": true  # 또는 false
    }
    """
    try:
        email = request.args.get("email")
        if not email:
            raise ValueError("이메일을 입력해야 합니다.")

        response = verify_email_status_service(email)
        return jsonify(response), 200
    except ValueError as e:
        current_app.logger.error(f"Email verification status error: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Unexpected error in email verification status check: {str(e)}")
        return jsonify({"error": "서버 오류가 발생했습니다."}), 500

@auth_bp.route("/verify-email-request", methods=["POST"])
def verify_email_request():
    """
    이메일 인증 요청 API
    사용자가 이메일을 입력하고 인증 요청을 하면, 해당 이메일로 인증 링크가 전송됨.
    """
    try:
        data = request.get_json()
        email = data.get("email")
        if not email:
            raise ValueError("이메일을 입력해야 합니다.")

        # Redis에서 최근 요청 여부 확인 (1시간 내 중복 요청 방지)
        if r.exists(f"pending_user:{email}"):
            raise ValueError("이미 이메일 인증 요청이 진행 중입니다. 잠시 후 다시 시도하세요.")

        response = verify_email_request_service(email)
        return jsonify(response), 200
    except ValueError as e:
        current_app.logger.error(f"Email verification request error: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Unexpected error in email verification request: {str(e)}")
        return jsonify({"error": "서버 오류가 발생했습니다."}), 500
    
@auth_bp.route("/resend-verification-code", methods=["POST"])
def resend_verification_code():
    """
    이메일 인증 코드 재전송 API

    요청 형식:
    {
        "email": "example@email.com"
    }

    응답:
    200 OK
    {
        "message": "새로운 인증 코드가 이메일로 전송되었습니다."
    }
    """
    try:
        data = request.get_json()
        email = data.get("email")
        if not email:
            raise ValueError("이메일을 입력해야 합니다.")

        response = send_verification_code_service(email) 
        return jsonify(response), 200
    except ValueError as e:
        current_app.logger.error(f"Resend verification code error: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Unexpected error in resending verification code: {str(e)}")
        return jsonify({"error": "서버 오류가 발생했습니다."}), 500



@auth_bp.route("/login", methods=["POST"])
def login():
    """
    로그인 API

    요청 형식:
    {
        "email": "example@email.com",
        "password": "SecurePassword123!"
    }

    응답:
    200 OK
    {
        "access_token": "<JWT_ACCESS_TOKEN>",
        "refresh_token": "<JWT_REFRESH_TOKEN>"
    }
    """
    try:
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            raise ValueError("이메일과 비밀번호를 입력해야 합니다.")
        
        # user = User.query.filter_by(email=email).first()

        # if not user:
        #     print(f"사용자 없음: {email}")
        #     raise ValueError("이메일 또는 비밀번호가 올바르지 않습니다.")
        
        # print(f"이메일: {email}")
        # print(f"저장된 해시: {user.password_hash}")
        # print(f"입력된 비밀번호: {password}")
        # print(f"비밀번호 검증 결과: {user.check_password(password)}")

        access_token, refresh_token = authenticate_user(email, password)

        return jsonify({"access_token": access_token, "refresh_token": refresh_token}), 200
    except ValueError as e:
        current_app.logger.error(f"Login error: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Unexpected error in login: {str(e)}")
        return jsonify({"error": "서버 오류가 발생했습니다."}), 500

@auth_bp.route("/refresh-token", methods=["POST"])  # 수정
def refresh():
    """
    리프레시 토큰 API (수정됨)

    요청 형식:
    {
        "refresh_token": "<JWT_REFRESH_TOKEN>"
    }

    응답:
    200 OK
    {
        "access_token": "<새로운 JWT_ACCESS_TOKEN>"
    }
    """
    try:
        data = request.get_json()
        decoded_token = verify_token(data["refresh_token"])
        access_token, _ = generate_tokens(decoded_token["user_id"])
        return jsonify({"access_token": access_token}), 200
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Refresh token has expired"}), 400
    except jwt.JWTError:
        return jsonify({"error": "Invalid refresh token"}), 400
    except Exception as e:
        current_app.logger.error(f"Error in token refresh: {str(e)}")
        return jsonify({"error": "서버 오류가 발생했습니다."}), 500

@auth_bp.route("/logout", methods=["POST"])
def logout():
    """
    로그아웃 API

    요청 형식:
    {
        "access_token": "<JWT_ACCESS_TOKEN>"
    }

    응답:
    200 OK
    {
        "message": "Logged out successfully"
    }
    """
    try:
        data = request.get_json()
        response = logout_service(data.get("access_token"))
        return jsonify(response), 200
    except ValueError as e:
        current_app.logger.error(f"Logout error: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Unexpected error in logout: {str(e)}")
        return jsonify({"error": "서버 오류가 발생했습니다."}), 500

@auth_bp.route("/request-password-reset", methods=["POST"])
def request_password_reset_route():
    """
    비밀번호 재설정 요청 API (이메일로 링크 전송)
    """
    try:
        data = request.get_json()
        if "email" not in data:
            raise ValueError("이메일을 입력해야 합니다.")

        response = request_password_reset(data["email"])
        return jsonify(response), 200
    except ValueError as e:
        current_app.logger.error(f"Password reset request error: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Unexpected error in password reset request: {str(e)}")
        return jsonify({"error": "서버 오류가 발생했습니다."}), 500


@auth_bp.route("/reset-password", methods=["POST"])
def reset_password_route():
    """비밀번호 재설정 (토큰 검증 후 비밀번호 변경)"""
    try:
        data = request.get_json()
        token = data.get("token")
        email = data.get("email")
        new_password = data.get("new_password")
        confirm_password = data.get("confirm_password")

        if not all([token, email, new_password, confirm_password]):
            raise ValueError("모든 필드를 입력해야 합니다.")

        response = reset_password(token, email, new_password, confirm_password)
        return jsonify(response), 200
    except ValueError as e:
        current_app.logger.error(f"Password reset error: {str(e)}")
        return jsonify({"error": str(e)}), 400 
    except Exception as e:
        current_app.logger.error(f"Unexpected error in reset-password: {str(e)}")
        return jsonify({"error": "서버 오류가 발생했습니다."}), 500