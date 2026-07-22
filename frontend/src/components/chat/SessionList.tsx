import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { List, Button, Input, Dropdown, Typography, Popconfirm, Space } from 'antd';
import {
  PlusOutlined,
  MessageOutlined,
  DeleteOutlined,
  EditOutlined,
  SearchOutlined,
} from '@ant-design/icons';
import { useChatStore } from '../../stores/chatStore';
import dayjs from 'dayjs';

const { Text } = Typography;

export default function SessionList() {
  const [search, setSearch] = useState('');
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editingTitle, setEditingTitle] = useState('');

  const {
    sessions,
    currentSessionId,
    createSession,
    deleteSession,
    renameSession,
    setCurrentSession,
  } = useChatStore();
  const navigate = useNavigate();

  const filteredSessions = sessions.filter((s) =>
    s.title.toLowerCase().includes(search.toLowerCase())
  );

  const handleCreate = async () => {
    const conv = await createSession();
    navigate(`/chat/${conv.id}`);
  };

  const handleSelect = (id: string) => {
    setCurrentSession(id);
    navigate(`/chat/${id}`);
  };

  const handleRename = async (id: string) => {
    if (editingTitle.trim()) {
      await renameSession(id, editingTitle.trim());
    }
    setEditingId(null);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      {/* Header */}
      <div style={{ padding: '12px 16px', borderBottom: '1px solid #f0f0f0' }}>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          block
          onClick={handleCreate}
        >
          新建对话
        </Button>
      </div>

      {/* Search */}
      <div style={{ padding: '8px 16px' }}>
        <Input
          prefix={<SearchOutlined />}
          placeholder="搜索会话..."
          size="small"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          allowClear
        />
      </div>

      {/* Session List */}
      <div style={{ flex: 1, overflow: 'auto' }}>
        <List
          dataSource={filteredSessions}
          renderItem={(item) => (
            <List.Item
              key={item.id}
              onClick={() => handleSelect(item.id)}
              style={{
                cursor: 'pointer',
                padding: '10px 16px',
                background: currentSessionId === item.id ? '#e6f4ff' : 'transparent',
                borderBottom: '1px solid #f5f5f5',
                transition: 'background 0.2s',
              }}
              onMouseEnter={(e) => {
                (e.currentTarget as HTMLElement).style.background =
                  currentSessionId === item.id ? '#e6f4ff' : '#f5f5f5';
              }}
              onMouseLeave={(e) => {
                (e.currentTarget as HTMLElement).style.background =
                  currentSessionId === item.id ? '#e6f4ff' : 'transparent';
              }}
            >
              <div style={{ flex: 1, overflow: 'hidden' }}>
                <MessageOutlined style={{ marginRight: 8, color: '#999' }} />
                {editingId === item.id ? (
                  <Input
                    size="small"
                    value={editingTitle}
                    onChange={(e) => setEditingTitle(e.target.value)}
                    onPressEnter={() => handleRename(item.id)}
                    onBlur={() => handleRename(item.id)}
                    autoFocus
                    style={{ width: '80%' }}
                    onClick={(e) => e.stopPropagation()}
                  />
                ) : (
                  <Text
                    ellipsis
                    style={{
                      fontWeight: currentSessionId === item.id ? 600 : 400,
                    }}
                  >
                    {item.title}
                  </Text>
                )}
                <br />
                <Text type="secondary" style={{ fontSize: 11 }}>
                  {item.message_count} 条消息 · {dayjs(item.updated_at).format('MM-DD HH:mm')}
                </Text>
              </div>

              <Dropdown
                menu={{
                  items: [
                    {
                      key: 'rename',
                      icon: <EditOutlined />,
                      label: '重命名',
                      onClick: () => {
                        setEditingId(item.id);
                        setEditingTitle(item.title);
                      },
                    },
                    {
                      key: 'delete',
                      icon: <DeleteOutlined />,
                      label: '删除',
                      danger: true,
                      onClick: () => deleteSession(item.id),
                    },
                  ],
                }}
                trigger={['click']}
              >
                <Button
                  type="text"
                  size="small"
                  icon={<EditOutlined />}
                  onClick={(e) => e.stopPropagation()}
                />
              </Dropdown>
            </List.Item>
          )}
          locale={{ emptyText: '暂无会话，点击上方按钮创建' }}
        />
      </div>
    </div>
  );
}
