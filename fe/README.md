
## 폴더 구조
```
📂 fe/ 
├── 📂 public/  # 정적 파일
│   └── assets/ # 이미지 등 정적 리소스
│   └── 📄 index.html  # 메인 HTML 파일
│
├── 📂 src/  # 소스 코드
│   ├── 📂 api/  # API 요청  
│   │   ├── 📄 auth.js    # 로그인/회원가입 관련 API  
│   │   └── 📄 config.js  # Axios 기본 설정  
│   ├── 📂 components/    # 재사용 가능한 UI 컴포넌트
│   │   ├── 📄 Navbar.js  # 네비게이션 바 
│   │   ├── 📄 Button.js  # 재사용 가능한 버튼
│   │   └── ErrorMessage.js  # 에러 메시지 
│   ├── 📂 pages/         # 개별 페이지
│   │   ├── 📄 Landing.js  # 랜딩 페이지 (로그인/회원가입 버튼)
│   │   ├── 📄 Login.js    # 로그인 페이지
│   │   ├── 📄 Signup.js   # 회원가입 페이지
│   │   ├── 📄 Home.js     # 로그인 후 홈 화면 (메뉴 포함)
│   │   ├── ForgotPassword.js  # 비밀번호 찾기  
│   │   └── ResetPassword.js  # 비밀번호 재설정  
│   ├── 📂 routes/         # React Router 설정
│   │   └── 📄 routes.js   # 전체 경로 정의
│   ├── 📂 store/          # Zustand 상태 관리  
│   │   └── 📄 authStore.js  # 로그인 상태 관리 
│   ├── 📂 styles/         # Styled Components 스타일 관리
│   │   ├── 📄 GlobalStyle.js  # 전역 스타일
│   │   └── 📄 components.js  # 개별 컴포넌트 스타일 모음  
│   ├── 📄 App.js           # 전체 앱 구조
│   └── 📄 index.js          # React 진입점
├── 📄 package.json         # 패키지 정보
├── 📄 .gitignore  
├── 📄 README.md 
└── 📄 .env  

```