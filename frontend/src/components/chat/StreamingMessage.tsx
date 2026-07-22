import { Avatar, Typography, Space } from 'antd';
import { RobotOutlined } from '@ant-design/icons';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { useChatStore } from '../../stores/chatStore';
import SourceCard from './SourceCard';

const { Text } = Typography;

export default function StreamingMessage() {
  const { streamingContent, streamingCitations } = useChatStore();

  return (
    <div
      style={{
        display: 'flex',
        marginBottom: 20,
        gap: 12,
      }}
    >
      <Avatar
        size={36}
        icon={<RobotOutlined />}
        style={{
          background: '#52c41a',
          flexShrink: 0,
        }}
      />

      <div style={{ maxWidth: '75%', minWidth: 200 }}>
        <div
          style={{
            padding: '12px 16px',
            borderRadius: 12,
            background: '#fff',
            boxShadow: '0 1px 4px rgba(0,0,0,0.08)',
            wordBreak: 'break-word',
          }}
        >
          {streamingContent ? (
            <div className="markdown-content">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {streamingContent}
              </ReactMarkdown>
            </div>
          ) : (
            <Text type="secondary">
              思考中<span className="typing-dots">...</span>
            </Text>
          )}
          {/* Blinking cursor */}
          <span
            style={{
              display: 'inline-block',
              width: 2,
              height: 16,
              background: '#1677ff',
              marginLeft: 2,
              animation: 'blink 1s infinite',
            }}
          />
        </div>

        {streamingCitations.length > 0 && (
          <div style={{ marginTop: 8 }}>
            <Text type="secondary" style={{ fontSize: 12, marginBottom: 4, display: 'block' }}>
              📖 引用来源：
            </Text>
            <Space direction="vertical" style={{ width: '100%' }}>
              {streamingCitations.map((citation, idx) => (
                <SourceCard key={idx} citation={citation} index={idx + 1} />
              ))}
            </Space>
          </div>
        )}
      </div>
    </div>
  );
}
