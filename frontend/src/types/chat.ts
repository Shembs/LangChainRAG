export interface Conversation {
  id: string;
  title: string;
  message_count: number;
  created_at: string;
  updated_at: string;
}

export interface MessageData {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  citations: Citation[];
  response_time_ms: number | null;
  created_at: string;
}

export interface Citation {
  chunk_id: string;
  doc_title: string;
  preview: string;
  score: number;
}
