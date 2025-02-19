import os
import re
import uuid
import bcrypt
import redis
import json
from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta
from jose import jwt, ExpiredSignatureError, JWTError
from flask_mail import Mail, Message
from flask import current_app
from app.models import db, User
import random

# 환경 변수 불러오기 (없으면 기본값 사용)
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")  
MAIL_USERNAME = os.getenv("MAIL_USERNAME", "noreply@example.com")  
BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:5000")  
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")  
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))  
REDIS_DB = int(os.getenv("REDIS_DB", 0))  

mail = Mail()
r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)  # Redis 설정

def validate_password(password):
    """
    비밀번호 복잡성 검사

    :param password: 입력된 비밀번호
    :raises ValueError: 비밀번호 조건이 충족되지 않을 경우 예외 발생
    """
    if len(password) < 8:
        raise ValueError("비밀번호는 최소 8자 이상이어야 합니다.")
    if not any(c.isupper() for c in password):  
        raise ValueError("비밀번호에 최소 하나의 대문자가 포함되어야 합니다.")
    if not any(c.islower() for c in password):  
        raise ValueError("비밀번호에 최소 하나의 소문자가 포함되어야 합니다.")
    if not any(c.isdigit() for c in password):  
        raise ValueError("비밀번호에 최소 하나의 숫자가 포함되어야 합니다.")
    if not any(c in "@$!%*?&" for c in password):  
        raise ValueError("비밀번호에 최소 하나의 특수문자가 포함되어야 합니다.")

def validate_email(email):
    """
    이메일 형식 검증

    :param email: 입력된 이메일
    :return: 이메일이 유효한 경우 True, 그렇지 않으면 False
    """
    email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(email_regex, email)

def register_user(email, password, confirm_password):
    """
    회원가입 처리 (중복 이메일 인증 요청 방지 추가)

    :param email: 사용자 이메일
    :param password: 비밀번호
    :param confirm_password: 비밀번호 확인
    :raises ValueError: 유효하지 않은 이메일, 이미 존재하는 이메일, 비밀번호 불일치일 경우 예외 발생
    :return: 회원가입 성공 메시지
    """
    if not validate_email(email):
        raise ValueError("유효하지 않은 이메일 형식입니다.")

    if User.query.filter_by(email=email).first():
        raise ValueError("이미 존재하는 이메일입니다.")

    if password != confirm_password:
        raise ValueError("비밀번호가 일치하지 않습니다.")

    validate_password(password)

    # 중복 이메일 인증 요청 방지 (10분 동안 유효)
    if r.exists(f"email_verification_request:{email}"):
        raise ValueError("이메일 인증 요청이 이미 진행 중입니다. 잠시 후 다시 시도하세요.")

    user_id = str(uuid.uuid4())
    new_user = User(email=email, user_id=user_id, is_verified=False)
    new_user.password = password

    db.session.add(new_user)
    db.session.commit()

    # Redis에 이메일 인증 요청 기록 저장 (10분 유지)
    r.setex(f"email_verification_request:{email}", timedelta(minutes=10), "requested")

    send_verification_code_service(email)

    return {"message": "회원가입 요청이 완료되었습니다. 이메일을 확인하세요."}


    #### 추가로 생각할 부분 #############
    # 이메일 전송 실패 처리 및 재시도 안내 로직
    # 이메일 재전송 기능
    # 약관 동의 및 개인정보 처리방침
    # 인증 완료 후 자동으로 로그인
    # 이메일 인증을 위한 토큰 유효 기간 관리


def send_verification_code_service(email):
    """
    이메일 인증 코드 생성 및 전송 (6자리 숫자 코드)
    
    :param email: 사용자 이메일
    :raises ValueError: 이메일 형식이 올바르지 않거나, 인증 요청이 너무 빈번할 경우
    :return: 성공 메시지
    """
    if not validate_email(email):
        raise ValueError("유효하지 않은 이메일 형식입니다.")

    # Redis에서 1분 내에 동일한 이메일로 인증 코드 요청이 있었는지 확인
    if r.exists(f"verification_code_request:{email}"):
        raise ValueError("인증 코드 요청이 너무 빈번합니다. 잠시 후 다시 시도하세요.")

    # 6자리 랜덤 숫자 코드 생성
    verification_code = str(random.randint(100000, 999999))

    # Redis에 저장 (5분 동안 유효)
    r.setex(f"verification_code:{email}", timedelta(minutes=5), verification_code)

    # Redis에 요청 기록 (1분 동안 중복 요청 방지)
    r.setex(f"verification_code_request:{email}", timedelta(minutes=1), "requested")

    # 이메일 전송
    msg = Message("이메일 인증 코드", sender=MAIL_USERNAME, recipients=[email])
    msg.body = f"인증 코드: {verification_code}\n\n이 코드는 5분 동안 유효합니다."

    try:
        mail.send(msg)
    except Exception as e:
        raise ValueError(f"이메일 전송 실패: {str(e)}")

    return {"message": "인증 코드가 이메일로 전송되었습니다."}


def verify_email_service(email, code):
    """
    이메일 인증 코드 검증

    :param email: 사용자 이메일
    :param code: 사용자가 입력한 인증 코드
    :raises ValueError: 인증 코드가 만료되었거나 일치하지 않는 경우
    :return: 이메일 인증 성공 메시지
    """
    stored_code = r.get(f"verification_code:{email}")

    if not stored_code:
        raise ValueError("인증 코드가 만료되었거나 요청되지 않았습니다.")

    if stored_code.decode("utf-8") != code:
        raise ValueError("잘못된 인증 코드입니다.")

    # 인증 코드 검증 성공 시, Redis에서 삭제
    r.delete(f"verification_code:{email}")

    # DB에서 사용자 이메일 인증 상태 업데이트
    user = User.query.filter_by(email=email).first()
    if not user:
        raise ValueError("해당 이메일의 사용자가 존재하지 않습니다.")

    user.is_verified = True
    db.session.commit()

    return {"message": "이메일 인증이 완료되었습니다."}

# def verify_email_token(token):
#     """
#     이메일 인증 처리

#     :param token: 이메일 인증 토큰
#     :raises ValueError: 유효하지 않은 또는 만료된 토큰일 경우 예외 발생
#     :return: 이메일 인증 성공 메시지
#     """
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
#         user_id = payload.get("user_id")
#     except ExpiredSignatureError:
#         raise ValueError("이메일 인증 토큰이 만료되었습니다.")
#     except JWTError:
#         raise ValueError("유효하지 않은 토큰입니다.")

#     # DB에서 사용자 검색
#     user = User.query.filter_by(user_id=user_id).first()
#     if not user:
#         raise ValueError("해당 사용자를 찾을 수 없습니다.")

#     # 이메일 인증 완료 (`is_verified=True`)
#     user.is_verified = True
#     db.session.commit()

#     return {"message": "이메일 인증이 완료되었습니다. 이제 로그인이 가능합니다."}

def verify_email_status_service(email):
    """
    이메일 인증 상태 확인
    """
    user = User.query.filter_by(email=email).first()
    if not user:
        raise ValueError("등록되지 않은 이메일입니다.")

    return {"verified": user.is_verified}

def verify_email_request_service(email):
    """
    이메일 인증 요청 처리
    """
    if not validate_email(email):
        raise ValueError("유효하지 않은 이메일 형식입니다.")

    if r.exists(f"pending_user:{email}"):
        raise ValueError("이미 이메일 인증 요청이 진행 중입니다. 잠시 후 다시 시도하세요.")

    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(email=email, is_verified=False)
        db.session.add(user)
        db.session.commit()

    r.setex(f"pending_user:{email}", timedelta(minutes=60), json.dumps({"email": email}))

    send_verification_code_service(email)

    return {"message": "이메일이 전송되었습니다. 인증 후 다시 확인해주세요."}

def logout_service(access_token):
    """
    로그아웃 처리 (토큰 즉시 무효화)

    :param access_token: 사용자 액세스 토큰
    :return: 로그아웃 성공 메시지
    """
    try:
        decoded_token = verify_token(access_token)
        user_id = decoded_token["user_id"]
    except ValueError as e:
        raise ValueError(f"로그아웃 실패: {str(e)}") 

    # Redis에서 해당 사용자의 토큰 삭제 (즉시 만료)
    r.setex(f"access_token_{user_id}", timedelta(seconds=1), "invalid")
    r.setex(f"refresh_token_{user_id}", timedelta(seconds=1), "invalid")

    return {"message": "로그아웃이 완료되었습니다."}

def authenticate_user(email, password):
    """
    사용자 로그인 처리

    :param email: 사용자 이메일
    :param password: 비밀번호
    :raises ValueError: 이메일 또는 비밀번호가 잘못되었을 경우 예외 발생
    :raises ValueError: 탈퇴한 계정일 경우 예외 발생
    :return: 액세스 토큰 및 리프레시 토큰
    """
    # 이메일로 사용자 조회
    user = User.query.filter_by(email=email, deleted_at=None).first()

    # 사용자 없거나 비밀번호가 틀린 경우 예외 발생
    if not user or not user.check_password(password):  # bcrypt.checkpw() 대신 check_password() 사용
        raise ValueError("이메일 또는 비밀번호가 올바르지 않습니다.")

    # 탈퇴한 계정인지 확인
    if user.status == "deleted":
        raise ValueError("탈퇴한 계정입니다. 로그인할 수 없습니다.")

    # 이메일 인증 여부 확인
    if not user.is_verified:
        raise ValueError("이메일 인증이 완료되지 않았습니다. 이메일을 확인하세요.")

    # 토큰 생성
    return generate_tokens(user.user_id)


def generate_tokens(user_id: str, access_token_expiry: int = 15, refresh_token_expiry: int = 60 * 24 * 7) -> tuple:
    """
    액세스 토큰 및 리프레시 토큰을 한 번의 호출로 생성

    :param user_id: 사용자 ID
    :param access_token_expiry: 액세스 토큰 유효 시간 (분)
    :param refresh_token_expiry: 리프레시 토큰 유효 시간 (분)
    :return: 액세스 토큰 및 리프레시 토큰 (tuple)
    """
    try:
        # 액세스 토큰 생성
        access_token = generate_token(user_id, expiration_minutes=access_token_expiry)
        
        # 리프레시 토큰 생성
        refresh_token = generate_token(user_id, expiration_minutes=refresh_token_expiry)

        # Redis에 액세스 토큰과 리프레시 토큰 저장
        r.setex(f"access_token_{user_id}", timedelta(minutes=access_token_expiry), access_token)
        r.setex(f"refresh_token_{user_id}", timedelta(minutes=refresh_token_expiry), refresh_token)

        return access_token, refresh_token
    except Exception as e:
        raise ValueError(f"토큰 생성 중 오류 발생: {str(e)}")


def generate_token(user_id: str, expiration_minutes: int) -> str:
    """
    JWT 토큰 생성

    :param user_id: 사용자 ID
    :param expiration_minutes: 토큰 유효 시간 (분)
    :return: 생성된 JWT 토큰
    """
    try:
        expiration_time = datetime.now(timezone.utc) + timedelta(minutes=expiration_minutes)
        payload = {
            "user_id": user_id,
            "exp": expiration_time
        }
        return jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    except Exception as e:
        raise ValueError(f"토큰 생성 오류: {str(e)}")

def verify_token(token):
    """
    토큰 검증 (Redis에서 저장된 토큰인지 확인 포함)

    :param token: JWT 토큰
    :raises ValueError: 유효하지 않은 토큰 또는 만료된 토큰일 경우 예외 발생
    :return: 토큰 페이로드
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = payload["user_id"]

        # Redis에서 해당 사용자의 저장된 토큰 확인 (로그아웃된 경우 예외 발생)
        stored_token = r.get(f"access_token_{user_id}")
        if not stored_token or stored_token.decode("utf-8") != token:
            raise ValueError("로그아웃된 사용자입니다. 다시 로그인해주세요.")

        return payload
    except ExpiredSignatureError:
        raise ValueError("토큰이 만료되었습니다.")
    except JWTError:
        raise ValueError("유효하지 않은 토큰입니다.")

def request_password_reset(email):
    """
    비밀번호 재설정 요청 (중복 요청 방지 추가)

    :param email: 사용자 이메일
    :raises ValueError: 등록되지 않은 이메일, 너무 빈번한 요청일 경우 예외 발생
    :return: 이메일 발송 성공 메시지
    """
    user = User.query.filter_by(email=email).first()
    if not user:
        raise ValueError("해당 이메일을 사용하는 계정을 찾을 수 없습니다.")

    # Redis에서 중복 요청 여부 확인 (30분 내 요청 제한)
    if r.exists(f"password_reset_request:{email}"):
        raise ValueError("비밀번호 재설정 요청이 너무 자주 발생했습니다. 잠시 후 다시 시도하세요.")

    token = jwt.encode(
        {
            "email": user.email,
            "exp": datetime.now(timezone.utc) + timedelta(minutes=30)
        },
        SECRET_KEY,
        algorithm="HS256"
    )

    reset_url = f"{BASE_URL}/reset-password?token={token}"

    msg = Message("비밀번호 재설정 요청", sender=MAIL_USERNAME, recipients=[email])
    msg.body = f"비밀번호를 재설정하려면 아래 링크를 클릭하세요:\n{reset_url}"

    try:
        mail.send(msg)
    except Exception as e:
        raise ValueError(f"이메일 전송 실패: {str(e)}")

    # Redis에 비밀번호 재설정 요청 기록 저장 (30분 유지)
    r.setex(f"password_reset_request:{email}", timedelta(minutes=30), "requested")

    return {"message": "비밀번호 재설정 링크를 이메일로 전송했습니다."}

def reset_password(token, email, new_password, confirm_password):
    """
    비밀번호 변경 (토큰 검증 후 새로운 비밀번호 저장)

    :param token: 이메일 인증을 위한 JWT 토큰
    :param email: 사용자 이메일
    :param new_password: 새 비밀번호
    :param confirm_password: 비밀번호 확인
    :raises ValueError: 유효하지 않은 토큰, 이메일 불일치, 비밀번호 조건 미충족 시 예외 발생
    :return: 성공 메시지
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        if payload["email"] != email:
            raise ValueError("이메일이 일치하지 않습니다.")
    except ExpiredSignatureError:
        raise ValueError("토큰이 만료되었습니다.")
    except JWTError:
        raise ValueError("유효하지 않은 토큰입니다.")

    # 비밀번호 유효성 체크
    validate_password(new_password)

    if new_password != confirm_password:
        raise ValueError("비밀번호가 일치하지 않습니다.")

    # 비밀번호 변경
    user = User.query.filter_by(email=email).first()
    if not user:
        raise ValueError("사용자를 찾을 수 없습니다.")

    user.password = new_password
    db.session.commit()

    return {"message": "비밀번호가 성공적으로 변경되었습니다."}

def refresh_token(refresh_token):
    """
    리프레시 토큰 검증 및 새로운 액세스 토큰 발급 (수정됨)

    :param refresh_token: 사용자 리프레시 토큰
    :raises ValueError: 유효하지 않은 토큰일 경우 예외 발생
    :return: 새 액세스 토큰
    """
    try:
        decoded_token = verify_token(refresh_token)
        access_token, _ = generate_tokens(decoded_token["user_id"])
        return {"access_token": access_token}
    except jwt.ExpiredSignatureError:
        raise ValueError("Refresh token has expired")
    except jwt.JWTError:
        raise ValueError("Invalid refresh token")