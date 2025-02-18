import { create } from 'zustand';

const useAuthStore = create((set) => ({
  isAuthenticated: !!localStorage.getItem('access_token'), // 로그인 상태 유지
  login: () => {
    set({ isAuthenticated: true });
  },
  logout: () => {
    localStorage.removeItem('access_token'); // 로그아웃 시 토큰 삭제
    localStorage.removeItem('refresh_token');
    set({ isAuthenticated: false });
  }
}));

export default useAuthStore;
