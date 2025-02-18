import React, { useState } from 'react';
import api from '../api/config';
import styled from 'styled-components';
import Button from '../components/Button';

const Container = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100vh;
`;

const Input = styled.input`
  width: 250px;
  padding: 10px;
  margin: 5px;
  border: 1px solid #ccc;
  border-radius: 5px;
`;

const ForgotPassword = () => {
  const [email, setEmail] = useState('');
  const [message, setMessage] = useState('');

  const handleResetRequest = async () => {
    try {
      await api.post('/reset-password-request', { email });
      setMessage('비밀번호 재설정 링크가 이메일로 전송되었습니다.');
    } catch (error) {
      setMessage('비밀번호 재설정 요청 실패: ' + (error.response?.data?.error || '서버 오류'));
    }
  };

  return (
    <Container>
      <h2>비밀번호 찾기</h2>
      <Input type="email" placeholder="이메일" value={email} onChange={(e) => setEmail(e.target.value)} />
      <Button onClick={handleResetRequest} bgColor="blue" hoverColor="darkblue">비밀번호 재설정 요청</Button>
      <p>{message}</p>
    </Container>
  );
};

export default ForgotPassword;
