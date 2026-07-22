import { useState, useEffect } from 'react';
import { Typography, Table, Tag, Card } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import client from '../api/client';

const { Title } = Typography;

interface AuditLog {
  id: string;
  user_id: string | null;
  action: string;
  resource_type: string;
  detail: any;
  ip_address: string | null;
  created_at: string;
}

export default function AuditLogPage() {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(false);

  const fetchLogs = async () => {
    setLoading(true);
    try {
      const data = await client.get('/system/audit-logs', {
        params: { page, page_size: 20 },
      });
      setLogs(data.data.items);
      setTotal(data.data.total);
    } catch {
      // Silently fail
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, [page]);

  const actionLabels: Record<string, string> = {
    doc_upload: '上传文档',
    doc_delete: '删除文档',
    user_ban: '禁用用户',
    system_config: '系统配置',
  };

  const columns: ColumnsType<AuditLog> = [
    {
      title: '时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      render: (t: string) => new Date(t).toLocaleString('zh-CN'),
    },
    {
      title: '操作',
      dataIndex: 'action',
      key: 'action',
      width: 120,
      render: (a: string) => (
        <Tag color="blue">{actionLabels[a] || a}</Tag>
      ),
    },
    {
      title: '资源类型',
      dataIndex: 'resource_type',
      key: 'resource_type',
      width: 100,
    },
    {
      title: '用户 ID',
      dataIndex: 'user_id',
      key: 'user_id',
      width: 200,
      render: (id: string | null) => id || '-',
    },
    {
      title: 'IP 地址',
      dataIndex: 'ip_address',
      key: 'ip_address',
      width: 140,
      render: (ip: string | null) => ip || '-',
    },
    {
      title: '详情',
      dataIndex: 'detail',
      key: 'detail',
      render: (d: any) =>
        d ? (
          <code style={{ fontSize: 12, maxWidth: 300, display: 'inline-block', overflow: 'hidden', textOverflow: 'ellipsis' }}>
            {JSON.stringify(d)}
          </code>
        ) : '-',
    },
  ];

  return (
    <div style={{ padding: 24, height: '100vh', overflow: 'auto' }}>
      <Title level={4}>操作审计日志</Title>
      <Card>
        <Table
          columns={columns}
          dataSource={logs}
          rowKey="id"
          loading={loading}
          pagination={{
            current: page,
            total,
            pageSize: 20,
            onChange: setPage,
            showTotal: (t) => `共 ${t} 条日志`,
          }}
        />
      </Card>
    </div>
  );
}
