export interface Document {
  id: string;
  title: string;
  file_type: string;
  file_size_bytes: number | null;
  category: string | null;
  status: string;
  chunk_count: number;
  error_message: string | null;
  created_at: string;
  updated_at: string;
}

export interface DocumentChunk {
  id: string;
  chunk_index: number;
  content: string;
  token_count: number | null;
  page_number: number | null;
  section_title: string | null;
}

export interface KnowledgeStats {
  total_documents: number;
  total_chunks: number;
  total_size_bytes: number;
  documents_by_status: Record<string, number>;
  documents_by_category: Record<string, number>;
}
