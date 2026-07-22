import { useState, useEffect } from 'react';
import {
  Typography,
  Upload,
  Button,
  Table,
  Tag,
  Space,
  Popconfirm,
  message,
  Select,
  Input,
  Card,
  Statistic,
  Row,
  Col,
  Drawer,
} from 'antd';
import {
  UploadOutlined,
  DeleteOutlined,
  InboxOutlined,
  FileTextOutlined,
  ReloadOutlined,
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import { knowledgeApi } from '../api/knowledge';
import type { Document, DocumentChunk, KnowledgeStats } from '../types/knowledge';
import ChunkPreview from '../components/admin/ChunkPreview';

const { Title, Text } = Typography;
const { Dragger } = Upload;

export default function KnowledgePage() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');
  const [stats, setStats] = useState<KnowledgeStats | null>(null);
  const [selectedDoc, setSelectedDoc] = useState<Document | null>(null);
  const [chunks, setChunks] = useState<DocumentChunk[]>([]);
  const [chunksTotal, setChunksTotal] = useState(0);
  const [chunkDrawerOpen, setChunkDrawerOpen] = useState(false);

  const fetchDocuments = async () => {
    setLoading(true);
    try {
      const data = await knowledgeApi.listDocuments(page, 20, search, categoryFilter);
      setDocuments(data.items);
      setTotal(data.total);
    } catch {
      message.error('获取文档列表失败');
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const data = await knowledgeApi.getStats();
      setStats(data);
    } catch {
      // Stats are non-critical
    }
  };

  useEffect(() => {
    fetchDocuments();
    fetchStats();
  }, [page, categoryFilter]);

  const handleUpload = async (file: File) => {
    try {
      await knowledgeApi.uploadDocuments([file], '通用');
      message.success(`"${file.name}" 上传成功`);
      fetchDocuments();
      fetchStats();
    } catch (err: any) {
      message.error(err?.response?.data?.detail || '上传失败');
    }
    return false; // Prevent default upload behavior
  };

  const handleDelete = async (id: string) => {
    try {
      await knowledgeApi.deleteDocument(id);
      message.success('文档已删除');
      fetchDocuments();
      fetchStats();
    } catch {
      message.error('删除失败');
    }
  };

  const handleViewChunks = async (doc: Document) => {
    setSelectedDoc(doc);
    try {
      const data = await knowledgeApi.getDocumentChunks(doc.id);
      setChunks(data.items);
      setChunksTotal(data.total);
    } catch {
      message.error('获取切片失败');
    }
    setChunkDrawerOpen(true);
  };

  const columns: ColumnsType<Document> = [
    {
      title: '文档名称',
      dataIndex: 'title',
      key: 'title',
      render: (text: string, record: Document) => (
        <Space>
          <FileTextOutlined />
          <a onClick={() => handleViewChunks(record)}>{text}</a>
        </Space>
      ),
    },
    {
      title: '类型',
      dataIndex: 'file_type',
      key: 'file_type',
      width: 80,
      render: (t: string) => <Tag>{t.toUpperCase()}</Tag>,
    },
    {
      title: '分类',
      dataIndex: 'category',
      key: 'category',
      width: 100,
    },
    {
      title: '大小',
      dataIndex: 'file_size_bytes',
      key: 'size',
      width: 100,
      render: (size: number | null) =>
        size ? `${(size / 1024).toFixed(1)} KB` : '-',
    },
    {
      title: '切片数',
      dataIndex: 'chunk_count',
      key: 'chunks',
      width: 80,
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: string) => {
        const colorMap: Record<string, string> = {
          pending: 'default',
          processing: 'processing',
          completed: 'success',
          error: 'error',
        };
        const labelMap: Record<string, string> = {
          pending: '等待中',
          processing: '处理中',
          completed: '已完成',
          error: '失败',
        };
        return <Tag color={colorMap[status] || 'default'}>{labelMap[status] || status}</Tag>;
      },
    },
    {
      title: '上传时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 160,
      render: (t: string) => new Date(t).toLocaleString('zh-CN'),
    },
    {
      title: '操作',
      key: 'actions',
      width: 120,
      render: (_, record: Document) => (
        <Space>
          <Button size="small" onClick={() => handleViewChunks(record)}>
            切片
          </Button>
          <Popconfirm
            title="确定删除此文档？"
            description="删除后将同时删除所有切片和向量数据"
            onConfirm={() => handleDelete(record.id)}
          >
            <Button size="small" danger icon={<DeleteOutlined />} />
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div style={{ padding: 24, height: '100vh', overflow: 'auto' }}>
      <Title level={4}>知识库管理</Title>

      {/* Stats */}
      {stats && (
        <Row gutter={16} style={{ marginBottom: 24 }}>
          <Col span={6}>
            <Card size="small">
              <Statistic title="文档总数" value={stats.total_documents} />
            </Card>
          </Col>
          <Col span={6}>
            <Card size="small">
              <Statistic title="切片总数" value={stats.total_chunks} />
            </Card>
          </Col>
          <Col span={6}>
            <Card size="small">
              <Statistic
                title="总大小"
                value={stats.total_size_bytes}
                formatter={(v) => `${((v as number) / (1024 * 1024)).toFixed(1)} MB`}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card size="small">
              <Statistic
                title="已完成文档"
                value={stats.documents_by_status?.completed || 0}
                suffix={`/ ${stats.total_documents}`}
              />
            </Card>
          </Col>
        </Row>
      )}

      {/* Upload */}
      <Card title="上传文档" style={{ marginBottom: 24 }}>
        <Dragger
          accept=".pdf,.txt,.csv,.md,.docx"
          beforeUpload={handleUpload}
          showUploadList={false}
          multiple
        >
          <p className="ant-upload-drag-icon">
            <InboxOutlined />
          </p>
          <p className="ant-upload-text">点击或拖拽文件到此区域上传</p>
          <p className="ant-upload-hint">
            支持 PDF、TXT、CSV、Markdown、Word 格式，单文件最大 50MB
          </p>
        </Dragger>
      </Card>

      {/* Document List */}
      <Card
        title="文档列表"
        extra={
          <Space>
            <Input.Search
              placeholder="搜索文档..."
              onSearch={(v) => {
                setSearch(v);
                fetchDocuments();
              }}
              style={{ width: 200 }}
            />
            <Select
              placeholder="筛选分类"
              allowClear
              style={{ width: 120 }}
              onChange={(v) => setCategoryFilter(v || '')}
              options={[
                { label: '手机数码', value: '手机数码' },
                { label: '家电', value: '家电' },
                { label: '服饰', value: '服饰' },
                { label: '食品', value: '食品' },
                { label: '通用', value: '通用' },
              ]}
            />
            <Button icon={<ReloadOutlined />} onClick={fetchDocuments}>
              刷新
            </Button>
          </Space>
        }
      >
        <Table
          columns={columns}
          dataSource={documents}
          rowKey="id"
          loading={loading}
          pagination={{
            current: page,
            total,
            pageSize: 20,
            onChange: setPage,
            showTotal: (t) => `共 ${t} 个文档`,
          }}
        />
      </Card>

      {/* Chunk Preview Drawer */}
      <Drawer
        title={`切片预览 - ${selectedDoc?.title || ''}`}
        open={chunkDrawerOpen}
        onClose={() => setChunkDrawerOpen(false)}
        width={700}
      >
        <ChunkPreview chunks={chunks} />
      </Drawer>
    </div>
  );
}
