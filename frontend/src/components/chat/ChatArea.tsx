import { useEffect, useRef } from 'react';
import { Typography, Button } from 'antd';
import { ExportOutlined } from '@ant-design/icons';
import { useChatStore } from '../../stores/chatStore';
import MessageBubble from './MessageBubble';
import StreamingMessage from './StreamingMessage';
import ChatInput from './ChatInput';

const { Title } = Typography;

export default function ChatArea() {
  const { messages, currentSessionId, sessions, isStreaming, streamingContent } = useChatStore();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const currentSession = sessions.find((s) => s.id === currentSessionId);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, streamingContent]);

  const handleExport = () => {
    if (messages.length === 0) return;
    const markdown = messages
      .map((m) => `### ${m.role === 'user' ? '用户' : '助手'}\n\n${m.content}\n`)
      .join('\n---\n');
    const blob = new Blob([markdown], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${currentSession?.title || '对话'}.md`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <>
      {/* Header */}
      <div
        style={{
          padding: '12px 24px',
          borderBottom: '1px solid #f0f0f0',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          background: '#fff',
        }}
      >
        <Title level={4} style={{ margin: 0 }}>
          {currentSession?.title || '知识库问答'}
        </Title>
        <Button icon={<ExportOutlined />} onClick={handleExport} disabled={messages.length === 0}>
          导出对话
        </Button>
      </div>

      {/* Messages */}
      <div
        style={{
          flex: 1,
          overflow: 'auto',
          padding: '16px 24px',
          background: '#f5f5f5',
        }}
      >
        {messages.length === 0 && !isStreaming && (
          <div
            style={{
              textAlign: 'center',
              color: '#999',
              marginTop: 100,
            }}
          >
            <p style={{ fontSize: 18 }}>👋 欢迎使用知识库问答系统</p>
            <p>在下方输入您的问题，系统将从知识库中检索相关信息并生成回答</p>
          </div>
        )}

        {messages.map((msg) => (
          <MessageBubble key={msg.id} message={msg} />
        ))}

        {isStreaming && <StreamingMessage />}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <ChatInput />
    </>
  );
}
