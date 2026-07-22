import { useState } from 'react';
import { Typography, Card, Form, Input, Button, message, Descriptions } from 'antd';
import { useAuthStore } from '../stores/authStore';
import { authApi } from '../api/auth';

const { Title } = Typography;

export default function SettingsPage() {
  const { user } = useAuthStore();
  const [loading, setLoading] = useState(false);
  const [form] = Form.useForm();

  const handleChangePassword = async (values: {
    old_password: string;
    new_password: string;
    confirm_password: string;
  }) => {
    if (values.new_password !== values.confirm_password) {
      message.error('两次输入的密码不一致');
      return;
    }
    setLoading(true);
    try {
      await authApi.changePassword({
        old_password: values.old_password,
        new_password: values.new_password,
      });
      message.success('密码修改成功！');
      form.resetFields();
    } catch (err: any) {
      message.error(err?.response?.data?.detail || '密码修改失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: 24, height: '100vh', overflow: 'auto', maxWidth: 700 }}>
      <Title level={4}>个人设置</Title>

      {/* User Info */}
      <Card title="基本信息" style={{ marginBottom: 24 }}>
        <Descriptions column={1}>
          <Descriptions.Item label="用户名">{user?.username}</Descriptions.Item>
          <Descriptions.Item label="角色">
            {user?.role === 'admin' ? '管理员' : '普通用户'}
          </Descriptions.Item>
          <Descriptions.Item label="注册时间">
            {user?.created_at ? new Date(user.created_at).toLocaleString('zh-CN') : '-'}
          </Descriptions.Item>
          <Descriptions.Item label="最后登录">
            {user?.last_login_at
              ? new Date(user.last_login_at).toLocaleString('zh-CN')
              : '-'}
          </Descriptions.Item>
        </Descriptions>
      </Card>

      {/* Change Password */}
      <Card title="修改密码">
        <Form form={form} onFinish={handleChangePassword} layout="vertical">
          <Form.Item
            name="old_password"
            label="当前密码"
            rules={[{ required: true, message: '请输入当前密码' }]}
          >
            <Input.Password placeholder="输入当前密码" />
          </Form.Item>

          <Form.Item
            name="new_password"
            label="新密码"
            rules={[
              { required: true, message: '请输入新密码' },
              { min: 6, message: '密码至少 6 个字符' },
            ]}
          >
            <Input.Password placeholder="输入新密码（至少 6 个字符）" />
          </Form.Item>

          <Form.Item
            name="confirm_password"
            label="确认新密码"
            rules={[
              { required: true, message: '请确认新密码' },
              ({ getFieldValue }) => ({
                validator(_, value) {
                  if (!value || getFieldValue('new_password') === value) {
                    return Promise.resolve();
                  }
                  return Promise.reject(new Error('两次输入的密码不一致'));
                },
              }),
            ]}
          >
            <Input.Password placeholder="再次输入新密码" />
          </Form.Item>

          <Form.Item>
            <Button type="primary" htmlType="submit" loading={loading}>
              修改密码
            </Button>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
}
