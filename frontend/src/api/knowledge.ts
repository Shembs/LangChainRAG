import client from './client';
import type { Document, DocumentChunk, KnowledgeStats } from '../types/knowledge';

export const knowledgeApi = {
  uploadDocuments: (files: File[], category: string) => {
    const formData = new FormData();
    files.forEach((f) => formData.append('files', f));
    formData.append('category', category);
    return client
      .post<{ message: string; document_ids: string[] }>('/admin/knowledge/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      .then((r) => r.data);
  },

  listDocuments: (page = 1, pageSize = 20, search = '', category = '', status = '') =>
    client
      .get<{ items: Document[]; total: number; page: number; page_size: number }>(
        '/admin/knowledge/documents',
        { params: { page, page_size: pageSize, search, category, status_filter: status } }
      )
      .then((r) => r.data),

  getDocument: (id: string) =>
    client.get<Document>(`/admin/knowledge/documents/${id}`).then((r) => r.data),

  deleteDocument: (id: string) =>
    client.delete(`/admin/knowledge/documents/${id}`).then((r) => r.data),

  getDocumentChunks: (id: string, page = 1, pageSize = 20) =>
    client
      .get<{ items: DocumentChunk[]; total: number }>(
        `/admin/knowledge/documents/${id}/chunks`,
        { params: { page, page_size: pageSize } }
      )
      .then((r) => r.data),

  getStats: () =>
    client.get<KnowledgeStats>('/admin/knowledge/stats').then((r) => r.data),
};
