import React, { useEffect } from 'react';
import useAuthStore from '../store/authStore';
import styled from 'styled-components';
import { useNavigate } from "react-router-dom";

const Container = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;  
  justify-content: center;
  height: 40vh;
`;

const Home = () => {
  const { isAuthenticated } = useAuthStore();
  const navigate = useNavigate();

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
    }
  }, [isAuthenticated, navigate]);

  return (
    <Container>
      <h1>홈 화면</h1>
      <p>채팅, 달력(다이어리), 설정</p>
    </Container>
  );
};

export default Home;