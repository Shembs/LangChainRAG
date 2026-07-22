import { create } from 'zustand';
import type { Conversation, MessageData } from '../types/chat';
import { chatApi } from '../api/chat';

interface ChatState {
  sessions: Conversation[];
  currentSessionId: string | null;
  messages: MessageData[];
  isStreaming: boolean;
  streamingContent: string;
  streamingCitations: MessageData['citations'];

  loadSessions: () => Promise<void>;
  createSession: (title?: string) => Promise<Conversation>;
  deleteSession: (id: string) => Promise<void>;
  renameSession: (id: string, title: string) => Promise<void>;
  setCurrentSession: (id: string) => void;
  loadMessages: (sessionId: string) => Promise<void>;
  addMessage: (msg: MessageData) => void;
  setStreaming: (isStreaming: boolean) => void;
  appendStreamContent: (content: string) => void;
  setStreamCitations: (citations: MessageData['citations']) => void;
  clearStream: () => void;
}

export const useChatStore = create<ChatState>((set, get) => ({
  sessions: [],
  currentSessionId: null,
  messages: [],
  isStreaming: false,
  streamingContent: '',
  streamingCitations: [],

  loadSessions: async () => {
    const data = await chatApi.listSessions();
    set({ sessions: data.items });
  },

  createSession: async (title) => {
    const conv = await chatApi.createSession(title || '新对话');
    set((state) => ({ sessions: [conv, ...state.sessions] }));
    return conv;
  },

  deleteSession: async (id) => {
    await chatApi.deleteSession(id);
    set((state) => ({
      sessions: state.sessions.filter((s) => s.id !== id),
      messages: state.currentSessionId === id ? [] : state.messages,
      currentSessionId: state.currentSessionId === id ? null : state.currentSessionId,
    }));
  },

  renameSession: async (id, title) => {
    const updated = await chatApi.updateSession(id, title);
    set((state) => ({
      sessions: state.sessions.map((s) => (s.id === id ? updated : s)),
    }));
  },

  setCurrentSession: (id) => {
    set({ currentSessionId: id });
    if (id) {
      get().loadMessages(id);
    }
  },

  loadMessages: async (sessionId) => {
    try {
      const messages = await chatApi.getMessages(sessionId);
      set({ messages });
    } catch {
      set({ messages: [] });
    }
  },

  addMessage: (msg) => {
    set((state) => ({ messages: [...state.messages, msg] }));
  },

  setStreaming: (isStreaming) => set({ isStreaming }),
  appendStreamContent: (content) =>
    set((state) => ({ streamingContent: state.streamingContent + content })),
  setStreamCitations: (citations) => set({ streamingCitations: citations }),
  clearStream: () => set({ streamingContent: '', streamingCitations: [], isStreaming: false }),
}));
