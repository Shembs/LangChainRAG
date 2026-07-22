import { Avatar, Typography, Space } from 'antd';
import { UserOutlined, RobotOutlined } from '@ant-design/icons';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import SourceCard from './SourceCard';
import type { MessageData } from '../../types/chat';

const { Text } = Typography;

interface Props {
  message: MessageData;
}

export default function MessageBubble({ message }: Props) {
  const isUser = message.role === 'user';

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: isUser ? 'row-reverse' : 'row',
        marginBottom: 20,
        gap: 12,
      }}
    >
      {/* Avatar */}
      <Avatar
        size={36}
        icon={isUser ? <UserOutlined /> : <RobotOutlined />}
        style={{
          background: isUser ? '#1677ff' : '#52c41a',
          flexShrink: 0,
        }}
      />

      {/* Content */}
      <div
        style={{
          maxWidth: '75%',
          minWidth: 200,
        }}
      >
        <div
          style={{
            padding: '12px 16px',
            borderRadius: 12,
            background: isUser ? '#1677ff' : '#fff',
            color: isUser ? '#fff' : '#000',
            boxShadow: isUser ? 'none' : '0 1px 4px rgba(0,0,0,0.08)',
            wordBreak: 'break-word',
          }}
        >
          {isUser ? (
            <Text style={{ color: '#fff', whiteSpace: 'pre-wrap' }}>
              {message.content}
            </Text>
          ) : (
            <div className="markdown-content">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {message.content}
              </ReactMarkdown>
            </div>
          )}
        </div>

        {/* Source Citations */}
        {!isUser && message.citations && message.citations.length > 0 && (
          <div style={{ marginTop: 8 }}>
            <Text type="secondary" style={{ fontSize: 12, marginBottom: 4, display: 'block' }}>
              📖 引用来源：
            </Text>
            <Space direction="vertical" style={{ width: '100%' }}>
              {message.citations.map((citation, idx) => (
                <SourceCard key={idx} citation={citation} index={idx + 1} />
              ))}
            </Space>
          </div>
        )}
      </div>
    </div>
  );
}
