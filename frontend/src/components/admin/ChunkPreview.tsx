import { Card, Tag, Typography } from 'antd';
import type { DocumentChunk } from '../../types/knowledge';

const { Text, Paragraph } = Typography;

interface Props {
  chunks: DocumentChunk[];
}

export default function ChunkPreview({ chunks }: Props) {
  return (
    <div>
      <Text type="secondary" style={{ display: 'block', marginBottom: 16 }}>
        共 {chunks.length} 个切片
      </Text>
      {chunks.map((chunk) => (
        <Card
          key={chunk.id}
          size="small"
          style={{ marginBottom: 12 }}
          title={
            <span>
              <Tag color="blue">切片 #{chunk.chunk_index + 1}</Tag>
              {chunk.section_title && (
                <Text strong style={{ fontSize: 13 }}>
                  {chunk.section_title}
                </Text>
              )}
              {chunk.page_number && (
                <Text type="secondary" style={{ fontSize: 12, marginLeft: 8 }}>
                  第 {chunk.page_number} 页
                </Text>
              )}
              {chunk.token_count && (
                <Text type="secondary" style={{ fontSize: 12, marginLeft: 8 }}>
                  {chunk.token_count} tokens
                </Text>
              )}
            </span>
          }
        >
          <Paragraph style={{ margin: 0, fontSize: 13, whiteSpace: 'pre-wrap' }}>
            {chunk.content}
          </Paragraph>
        </Card>
      ))}
    </div>
  );
}
