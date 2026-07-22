import { useNavigate, useLocation } from 'react-router-dom';
import { Layout, Menu, Button, Dropdown, Avatar, Space, Typography } from 'antd';
import {
  MessageOutlined,
  DatabaseOutlined,
  AuditOutlined,
  SettingOutlined,
  LogoutOutlined,
  UserOutlined,
} from '@ant-design/icons';
import { useAuthStore } from '../../stores/authStore';

const { Sider } = Layout;
const { Text } = Typography;

export default function Sidebar() {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuthStore();

  const menuItems = [
    {
      key: '/chat',
      icon: <MessageOutlined />,
      label: '知识库问答',
    },
    ...(user?.role === 'admin'
      ? [
          {
            key: '/admin/knowledge',
            icon: <DatabaseOutlined />,
            label: '知识库管理',
          },
          {
            key: '/admin/audit',
            icon: <AuditOutlined />,
            label: '操作日志',
          },
        ]
      : []),
    {
      key: '/settings',
      icon: <SettingOutlined />,
      label: '个人设置',
    },
  ];

  const handleMenuClick = ({ key }: { key: string }) => {
    navigate(key);
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const userMenuItems = [
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: '退出登录',
      onClick: handleLogout,
    },
  ];

  return (
    <Sider
      width={220}
      style={{
        background: '#fff',
        borderRight: '1px solid #f0f0f0',
        display: 'flex',
        flexDirection: 'column',
        height: '100vh',
        position: 'sticky',
        top: 0,
      }}
    >
      {/* Logo Area */}
      <div
        style={{
          height: 64,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          borderBottom: '1px solid #f0f0f0',
        }}
      >
        <Text strong style={{ fontSize: 16 }}>
          📚 RAG 知识库问答
        </Text>
      </div>

      {/* Navigation */}
      <Menu
        mode="inline"
        selectedKeys={[location.pathname]}
        items={menuItems}
        onClick={handleMenuClick}
        style={{ flex: 1, borderRight: 0, marginTop: 8 }}
      />

      {/* User Info */}
      <div
        style={{
          padding: '16px',
          borderTop: '1px solid #f0f0f0',
        }}
      >
        <Dropdown menu={{ items: userMenuItems }} trigger={['click']}>
          <Button type="text" style={{ width: '100%', height: 48 }}>
            <Space>
              <Avatar size="small" icon={<UserOutlined />} />
              <Text>{user?.username}</Text>
              <Text type="secondary" style={{ fontSize: 12 }}>
                {user?.role === 'admin' ? '管理员' : '用户'}
              </Text>
            </Space>
          </Button>
        </Dropdown>
      </div>
    </Sider>
  );
}
