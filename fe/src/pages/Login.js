import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { login } from '../api/auth';
import useAuthStore from '../store/authStore';
import styled from 'styled-components';
import Button from '../components/Button';
import Cookies from 'js-cookie';

const Container = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 50vh;
`;

const Input = styled.input`
  width: 250px;
  padding: 10px;
  margin: 5px;
  border: 1px solid #ccc;
  border-radius: 5px;
`;

const CheckboxContainer = styled.div`
  display: flex;
  align-items: center;
  margin: 5px;
`;

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(false);
  const { login: setLogin } = useAuthStore();
  const navigate = useNavigate();

  const handleLogin = async () => {
    try {
      const response = await login(email, password, rememberMe);

      setLogin(); // Zustand 상태 변경
      if (rememberMe) {
        Cookies.set('access_token', response.access_token, { expires: 7 }); // 7일 유지
        Cookies.set('refresh_token', response.refresh_token, { expires: 7 });
      } else {
        localStorage.setItem('access_token', response.access_token);
        localStorage.setItem('refresh_token', response.refresh_token);
      }

      navigate('/home');
    } catch (error) {
      alert('로그인 실패: ' + (error.response?.data?.error || '서버 오류'));
    }
  };

  return (
    <Container>
      <h2>로그인</h2>
      <Input type="email" placeholder="이메일" value={email} onChange={(e) => setEmail(e.target.value)} />
      <Input type="password" placeholder="비밀번호" value={password} onChange={(e) => setPassword(e.target.value)} />
      <CheckboxContainer>
        <input type="checkbox" checked={rememberMe} onChange={(e) => setRememberMe(e.target.checked)} />
        <label>로그인 유지</label>
      </CheckboxContainer>
      <Button onClick={handleLogin}>로그인</Button>
    </Container>
  );
};

export default Login;
