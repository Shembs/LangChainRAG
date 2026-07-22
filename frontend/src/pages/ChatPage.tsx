import { useEffect, useRef, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import { Layout, Typography, Empty } from 'antd';
import { useChatStore } from '../stores/chatStore';
import SessionList from '../components/chat/SessionList';
import ChatArea from '../components/chat/ChatArea';

const { Text } = Typography;

export default function ChatPage() {
  const { sessionId } = useParams<{ sessionId: string }>();
  const { loadSessions, setCurrentSession, currentSessionId, sessions, loadMessages } = useChatStore();
  const initialized = useRef(false);

  useEffect(() => {
    loadSessions();
  }, [loadSessions]);

  useEffect(() => {
    if (sessionId && sessionId !== currentSessionId) {
      setCurrentSession(sessionId);
    }
  }, [sessionId, currentSessionId, setCurrentSession]);

  // Auto-select first session or create new one
  useEffect(() => {
    if (initialized.current) return;
    if (sessions.length > 0 && !currentSessionId && !sessionId) {
      initialized.current = true;
      setCurrentSession(sessions[0].id);
    }
  }, [sessions, currentSessionId, sessionId, setCurrentSession]);

  return (
    <div style={{ display: 'flex', height: '100vh' }}>
      {/* Left: Session List */}
      <div
        style={{
          width: 280,
          borderRight: '1px solid #f0f0f0',
          display: 'flex',
          flexDirection: 'column',
          background: '#fafafa',
        }}
      >
        <SessionList />
      </div>

      {/* Right: Chat Area */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        {currentSessionId ? (
          <ChatArea />
        ) : (
          <div
            style={{
              flex: 1,
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
            }}
          >
            <Empty description="选择一个会话或创建新对话开始问答" />
          </div>
        )}
      </div>
    </div>
  );
}
