import { Card, Tag, Typography, Space } from 'antd';
import { FileTextOutlined } from '@ant-design/icons';
import type { Citation } from '../../types/chat';

const { Text, Paragraph } = Typography;

interface Props {
  citation: Citation;
  index: number;
}

export default function SourceCard({ citation, index }: Props) {
  return (
    <Card
      size="small"
      style={{
        background: '#fafafa',
        border: '1px solid #f0f0f0',
        borderRadius: 8,
      }}
      title={
        <Space>
          <Tag color="blue" style={{ margin: 0 }}>
            [{index}]
          </Tag>
          <FileTextOutlined />
          <Text style={{ fontSize: 13 }}>{citation.doc_title}</Text>
        </Space>
      }
    >
      <Paragraph
        ellipsis={{ rows: 3, expandable: true, symbol: '展开' }}
        style={{ margin: 0, fontSize: 12, color: '#666' }}
      >
        {citation.preview}
      </Paragraph>
      <Text type="secondary" style={{ fontSize: 11 }}>
        相关度: {(citation.score * 100).toFixed(1)}%
      </Text>
    </Card>
  );
}
