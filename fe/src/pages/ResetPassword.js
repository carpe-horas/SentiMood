import React, { useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
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

const ResetPassword = () => {
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token');
  const email = searchParams.get('email');

  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const navigate = useNavigate();

  const handleReset = async () => {
    if (newPassword !== confirmPassword) {
      alert('비밀번호가 일치하지 않습니다.');
      return;
    }

    try {
      await api.post('/reset-password', { token, email, new_password: newPassword, confirm_password: confirmPassword });
      alert('비밀번호가 변경되었습니다. 로그인 페이지로 이동합니다.');
      navigate('/login');
    } catch (error) {
      alert('비밀번호 변경 실패: ' + (error.response?.data?.error || '서버 오류'));
    }
  };

  return (
    <Container>
      <h2>비밀번호 재설정</h2>
      <Input type="password" placeholder="새 비밀번호" value={newPassword} onChange={(e) => setNewPassword(e.target.value)} />
      <Input type="password" placeholder="비밀번호 확인" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} />
      <Button onClick={handleReset} bgColor="green" hoverColor="darkgreen">비밀번호 변경</Button>
    </Container>
  );
};

export default ResetPassword;
