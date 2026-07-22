import { useEffect } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import { Layout } from 'antd';
import Sidebar from './Sidebar';
import { useAuthStore } from '../../stores/authStore';

const { Content } = Layout;

export default function AppLayout() {
  const { user, fetchUser } = useAuthStore();
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    if (!user) {
      fetchUser();
    }
  }, [user, fetchUser]);

  useEffect(() => {
    // Redirect to chat on first load
    if (location.pathname === '/') {
      navigate('/chat', { replace: true });
    }
  }, [location.pathname, navigate]);

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sidebar />
      <Layout>
        <Content
          style={{
            padding: 0,
            background: '#fff',
            minHeight: '100vh',
          }}
        >
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  );
}
