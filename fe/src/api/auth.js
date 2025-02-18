import api from './config';
import Cookies from 'js-cookie';

// 회원가입 API
export const signup = async (email, password, confirmPassword) => {
  try {
    const response = await api.post('/register', {
      email,
      password,
      confirm_password: confirmPassword,
    });
    return response.data;
  } catch (error) {
    console.error('회원가입 실패:', error.response?.data?.error || error.message);
    throw error;
  }
};

// 로그인 API
export const login = async (email, password, rememberMe) => {
  try {
    const response = await api.post('/login', {
      email,
      password,
      remember_me: rememberMe,
    });

    // const { access_token, refresh_token } = response.data;

    // 로컬스토리지에 토큰 저장 (자동 로그인 지원)
    // localStorage.setItem('access_token', access_token);
    // localStorage.setItem('refresh_token', refresh_token);

    return response.data;
  } catch (error) {
    console.error('로그인 실패:', error.response?.data?.error || error.message);
    throw error;
  }
};

// 로그아웃 API
export const logout = async () => {
  try {
    // const accessToken = localStorage.getItem('access_token');
    // if (!accessToken) throw new Error('로그인 상태가 아닙니다.');
    // await api.post('/logout', { access_token: accessToken });

    await api.post('/logout', { access_token: Cookies.get('access_token') || localStorage.getItem('access_token') });

    Cookies.remove('access_token');
    Cookies.remove('refresh_token');

    // 로컬스토리지에서 토큰 삭제
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  } catch (error) {
    console.error('로그아웃 실패:', error.response?.data?.error || error.message);
    throw error;
  }
};

// 토큰 갱신 (Refresh Token 사용)
export const refreshAccessToken = async () => {
  try {
    const refreshToken = localStorage.getItem('refresh_token');
    if (!refreshToken) throw new Error('Refresh Token이 없습니다.');

    const response = await api.put('/token', { refresh_token: refreshToken });

    // 새로운 액세스 토큰 저장
    localStorage.setItem('access_token', response.data.access_token);
    return response.data.access_token;
  } catch (error) {
    console.error('토큰 갱신 실패:', error.response?.data?.error || error.message);
    throw error;
  }
};
