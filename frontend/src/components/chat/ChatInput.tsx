import { useState } from 'react';
import { Input, Button, Space, Alert } from 'antd';
import { SendOutlined } from '@ant-design/icons';
import { useChatStore } from '../../stores/chatStore';

export default function ChatInput() {
  const [input, setInput] = useState('');
  const [error, setError] = useState<string | null>(null);
  const { currentSessionId, createSession, addMessage, setStreaming, appendStreamContent, clearStream } = useChatStore();

  const handleSend = async () => {
    const question = input.trim();
    if (!question) return;

    setInput('');
    setError(null);

    // Ensure we have a session
    let sessionId = currentSessionId;
    if (!sessionId) {
      const conv = await createSession();
      sessionId = conv.id;
    }

    // Add user message
    const userMsg = {
      id: `temp-${Date.now()}`,
      role: 'user' as const,
      content: question,
      citations: [],
      response_time_ms: null,
      created_at: new Date().toISOString(),
    };
    addMessage(userMsg);

    // Start streaming response
    setStreaming(true);
    clearStream();

    try {
      const response = await fetch('/api/v1/chat/ask', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify({ conversation_id: sessionId, question }),
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.detail || `请求失败 (${response.status})`);
      }

      const reader = response.body?.getReader();
      if (!reader) throw new Error('无法读取流式响应');

      const decoder = new TextDecoder();
      let buffer = '';
      let fullContent = '';
      let citations: any[] = [];

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (!line.startsWith('data: ')) continue;
          const dataStr = line.slice(6);
          try {
            const data = JSON.parse(dataStr);

            if (data.type === 'text') {
              fullContent += data.content;
              appendStreamContent(data.content);
            } else if (data.type === 'citation') {
              if (data.citations) {
                citations = data.citations;
                useChatStore.getState().setStreamCitations(citations);
              }
            }
            // 'done' event is handled after the loop
          } catch {
            // Skip unparseable lines
          }
        }
      }

      // Add assistant message
      const assistantMsg = {
        id: `temp-${Date.now()}-assistant`,
        role: 'assistant' as const,
        content: fullContent,
        citations,
        response_time_ms: null,
        created_at: new Date().toISOString(),
      };
      addMessage(assistantMsg);
    } catch (err: any) {
      setError(err.message || '请求失败，请重试');
    } finally {
      clearStream();
    }
  };

  return (
    <div
      style={{
        padding: '16px 24px',
        borderTop: '1px solid #f0f0f0',
        background: '#fff',
      }}
    >
      {error && (
        <Alert
          message={error}
          type="error"
          closable
          onClose={() => setError(null)}
          style={{ marginBottom: 8 }}
        />
      )}
      <Space.Compact style={{ width: '100%' }}>
        <Input.TextArea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onPressEnter={(e) => {
            if (!e.shiftKey) {
              e.preventDefault();
              handleSend();
            }
          }}
          placeholder="输入您的问题，按 Enter 发送，Shift+Enter 换行..."
          autoSize={{ minRows: 1, maxRows: 4 }}
          style={{ flex: 1 }}
        />
        <Button
          type="primary"
          icon={<SendOutlined />}
          onClick={handleSend}
          disabled={!input.trim()}
          style={{ height: 'auto' }}
        >
          发送
        </Button>
      </Space.Compact>
    </div>
  );
}
