import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import useAuthStore from '../store/authStore';
import { logout } from '../api/auth';
import styled from 'styled-components';
import Button from '../components/Button';

const Container = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100vh;
`;

const Home = () => {
  const { isAuthenticated, logout: setLogout } = useAuthStore();
  const navigate = useNavigate();

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
    }
  }, [isAuthenticated, navigate]);

  const handleLogout = async () => {
    try {
      await logout();
      setLogout(); // Zustand 상태 변경
      navigate('/login');
    } catch (error) {
      alert('로그아웃 실패: ' + (error.response?.data?.error || '서버 오류'));
    }
  };

  return (
    <Container>
      <h2>홈 화면</h2>
      <p>환영합니다! 🎉</p>
      <Button onClick={handleLogout} bgColor="red" hoverColor="darkred">로그아웃</Button>
    </Container>
  );
};

export default Home;
