import React from "react";
import { Link } from "react-router-dom";
import useAuthStore from "../store/authStore";
import styled from "styled-components";

const Nav = styled.nav`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 15px 20px;
  background: #f8f9fa;
`;

const Logo = styled(Link)`
  font-weight: bold;
  font-size: 20px;
  text-decoration: none;
  color: black;
  margin-right: 40px;

  &:hover {
    color: rgb(148, 201, 253);
  }
`;

const NavContainer = styled.div`
  display: flex;
  align-items: center;
  flex-grow: 1;
`;

const MenuLeft = styled.div`
  display: flex;
  align-items: center;
  gap: 30px;
`;

const MenuRight = styled.div`
  margin-left: auto;
  display: flex;
  gap: 20px;
`;

const StyledLink = styled(Link)`
  text-decoration: none;
  color: black;
  font-size: 16px;

  &:hover {
    color: rgb(148, 201, 253);
  }
`;

const StyledButton = styled.button`
  all: unset;
  border: none;
  color: black;
  font-size: 16px;
  cursor: pointer;
  padding: 0;
  margin-right: 20px;
  text-decoration: none;
  outline: none;

  &:hover {
    color: rgb(255, 114, 96);
    background: none;
  }

  &:focus {
    outline: none;
    box-shadow: none;
  }
`;

const SignupLink = styled(Link)`
  margin-right: 20px;
  text-decoration: none;
  color: black;
  font-size: 16px;

  &:hover {
    color: rgb(148, 201, 253);
  }
`;

const Navbar = () => {
  const { isAuthenticated, logout } = useAuthStore();
  return (
    <Nav>
      <NavContainer>
        {/* 왼쪽 로고 (로그인 전: 랜딩 페이지, 로그인 후: 홈 화면) */}
        <Logo to={isAuthenticated ? "/home" : "/"}>RobotPet</Logo>
        {/* RobotPet 오른쪽에 위치할 메뉴 */}
        {isAuthenticated && (
          <MenuLeft>
            <StyledLink to="/chat">채팅</StyledLink>
            <StyledLink to="/calendar">캘린더</StyledLink>
          </MenuLeft>
        )}
      </NavContainer>
      {/* 오른쪽 끝에 위치할 메뉴 */}
      {isAuthenticated ? (
        <MenuRight>
          <StyledButton onClick={logout}>로그아웃</StyledButton>
        </MenuRight>
      ) : (
        <MenuRight>
          <StyledLink to="/login">로그인</StyledLink>
          <SignupLink to="/signup">회원가입</SignupLink>
        </MenuRight>
      )}
    </Nav>
  );
};

export default Navbar;
