import { Routes, Route } from 'react-router-dom';
import Landing from '../pages/Landing';
import Login from '../pages/Login';
import Signup from '../pages/Signup';
import Home from '../pages/Home';
import PrivateRoute from './PrivateRoute';

const AppRoutes = () => {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/login" element={<Login />} />
      <Route path="/signup" element={<Signup />} />

      {/* 로그인한 사용자만 접근 가능 */}
      <Route element={<PrivateRoute />}>
        <Route path="/home" element={<Home />} />
      </Route>
    </Routes>
  );
};

export default AppRoutes;
