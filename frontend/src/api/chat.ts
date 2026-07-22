import client from './client';
import type { Conversation, MessageData } from '../types/chat';

export const chatApi = {
  listSessions: (page = 1, pageSize = 20) =>
    client
      .get<{ items: Conversation[]; total: number }>('/chat/sessions', {
        params: { page, page_size: pageSize },
      })
      .then((r) => r.data),

  createSession: (title?: string) =>
    client.post<Conversation>('/chat/sessions', { title }).then((r) => r.data),

  updateSession: (id: string, title: string) =>
    client.patch<Conversation>(`/chat/sessions/${id}`, { title }).then((r) => r.data),

  deleteSession: (id: string) =>
    client.delete(`/chat/sessions/${id}`).then((r) => r.data),

  getMessages: (sessionId: string) =>
    client.get<MessageData[]>(`/chat/sessions/${sessionId}/messages`).then((r) => r.data),
};
