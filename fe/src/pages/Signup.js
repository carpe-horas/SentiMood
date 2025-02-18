import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { signup } from '../api/auth';
import api from '../api/config';
import styled from 'styled-components';
import Button from '../components/Button';
import ErrorMessage from '../components/ErrorMessage';

const Container = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 60vh;
`;

const Title = styled.h2`
  margin-bottom: 50px; /* 제목과 입력창 사이 간격*/
`;

const FormContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  align-items: flex-start; 
  gap: 15px;
`;

const EmailContainer = styled.div`
  display: flex;
  align-items: center;
  gap: 10px; /* 입력창과 버튼 사이 간격 */
  width: 100%;
`;

const Input = styled.input`
  width: 250px;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 5px;
  box-sizing: border-box;
`;

const EmailInput = styled(Input)`
  height: 40px; 
`;

const EmailButton = styled(Button)`
  height: 40px;
  padding: 0 20px; 
  white-space: nowrap; 
  flex-shrink: 0; /* 버튼이 줄어들지 않도록*/
`;

const SignupButtonWrapper = styled.div`
  width: 100%;
  display: flex;
`;

const SignupButton = styled(Button)`
  width: 250px; 
  margin-top: 20px; /* 회원가입 버튼과 입력창 사이 간격*/
`;

const Signup = () => {
  const [email, setEmail] = useState('');
  const [isEmailVerified, setIsEmailVerified] = useState(false);
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [verificationSent, setVerificationSent] = useState(false);
  const navigate = useNavigate();

  // 이메일 인증 요청 & 상태 확인
  const handleEmailVerification = async () => {
    try {
      if (!verificationSent) {
        await api.post('/verify-email-request', { email });
        setVerificationSent(true);
        alert('이메일이 전송되었습니다. 인증 후 다시 시도해주세요.');
      }

      // 이메일 인증 상태 확인
      const response = await api.get(`/verify-email-status?email=${email}`);
      if (response.data.verified) {
        setIsEmailVerified(true);
        alert('이메일 인증이 완료되었습니다.');
      } else {
        alert('아직 이메일 인증이 완료되지 않았습니다.');
      }
    } catch (error) {
      setError(error.response?.data?.error || '서버 오류');
    }
  };

  // 회원가입 요청
  const handleSignup = async () => {
    if (!isEmailVerified) {
      alert('이메일 인증이 완료되지 않았습니다.');
      return;
    }

    if (password !== confirmPassword) {
      setError('비밀번호가 일치하지 않습니다.');
      return;
    }

    try {
      await signup(email, password, confirmPassword);
      alert('회원가입 성공! 로그인 페이지로 이동합니다.');
      navigate('/login');
    } catch (error) {
      setError(error.response?.data?.error || '서버 오류');
    }
  };

  return (
    <Container>
      <Title>회원가입</Title>

      <FormContainer>
        {/* 이메일 입력 & 인증 버튼을 한 줄로 정렬 */}
        <EmailContainer>
          <EmailInput
            type="email"
            placeholder="이메일"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            disabled={isEmailVerified}
          />
          <EmailButton onClick={handleEmailVerification} bgColor="#A3C6ED" hoverColor="#258DFB">
            {verificationSent ? '이메일 인증 확인' : '이메일 인증 요청'}
          </EmailButton>
        </EmailContainer>

        {/* 이메일 인증과 상관없이 비밀번호 입력 가능 */}
        <Input type="password" placeholder="비밀번호" value={password} onChange={(e) => setPassword(e.target.value)} />
        <Input type="password" placeholder="비밀번호 확인" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} />

        {/* 이메일 인증이 완료되지 않으면 회원가입 버튼 비활성화 */}
        <SignupButtonWrapper>
          <SignupButton onClick={handleSignup} bgColor="#A3C6ED" hoverColor="#258DFB" disabled={!isEmailVerified}>
            회원가입
          </SignupButton>
        </SignupButtonWrapper>
        <ErrorMessage message={error} />
      </FormContainer>
    </Container>
  );
};

export default Signup;
