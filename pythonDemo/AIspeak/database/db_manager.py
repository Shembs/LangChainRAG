"""
Noir AI — MySQL 数据库操作模块
管理聊天对话、消息记录和系统配置的 CRUD 操作

使用方式:
    from database.db_manager import DatabaseManager

    db = DatabaseManager()
    conv_id = db.create_conversation("deepseek", "deepseek-v4-pro")
    db.add_message(conv_id, "user", "你好")
    db.add_message(conv_id, "assistant", "你好！有什么可以帮你的？", model="deepseek-v4-pro")
"""

import os
from contextlib import contextmanager

import pymysql
from pymysql.cursors import DictCursor


# ==================== 数据库配置 ====================
# 可通过环境变量覆盖，默认值用于本地开发
DB_CONFIG = {
    "host": os.environ.get("MYSQL_HOST", "localhost"),
    "port": int(os.environ.get("MYSQL_PORT", 3306)),
    "user": os.environ.get("MYSQL_USER", "root"),
    "password": os.environ.get("MYSQL_PASSWORD", "123456"),
    "database": os.environ.get("MYSQL_DATABASE", "noir_ai_chat"),
    "charset": "utf8mb4",
    "cursorclass": DictCursor,
}


class DatabaseManager:
    """MySQL 数据库管理器，封装所有聊天记录相关的数据库操作"""

    def __init__(self, config: dict | None = None):
        self.config = config or DB_CONFIG

    # ==================== 连接管理 ====================

    @contextmanager
    def _get_connection(self):
        """获取数据库连接的上下文管理器，自动提交/回滚"""
        conn = pymysql.connect(**self.config)
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    # ==================== 对话管理 ====================

    def create_conversation(
        self, provider: str, model: str, title: str = "新对话"
    ) -> int:
        """创建新对话，返回对话ID"""
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO conversations (title, provider, model) VALUES (%s, %s, %s)",
                    (title, provider, model),
                )
                return cursor.lastrowid

    def get_conversation(self, conversation_id: int) -> dict | None:
        """获取单个对话信息"""
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM conversations WHERE id = %s",
                    (conversation_id,),
                )
                return cursor.fetchone()

    def get_conversations(
        self, limit: int = 20, offset: int = 0
    ) -> list[dict]:
        """获取对话列表（按更新时间倒序）"""
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM conversations ORDER BY updated_at DESC LIMIT %s OFFSET %s",
                    (limit, offset),
                )
                return cursor.fetchall()

    def update_conversation_title(self, conversation_id: int, title: str):
        """更新对话标题"""
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE conversations SET title = %s WHERE id = %s",
                    (title, conversation_id),
                )

    def delete_conversation(self, conversation_id: int):
        """删除对话及其所有消息（CASCADE自动删除消息）"""
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM conversations WHERE id = %s",
                    (conversation_id,),
                )

    def rename_conversation_by_first_message(self, conversation_id: int):
        """用对话的第一条用户消息自动命名"""
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT content FROM messages WHERE conversation_id = %s AND role = 'user' ORDER BY id ASC LIMIT 1",
                    (conversation_id,),
                )
                row = cursor.fetchone()
                if row:
                    title = row["content"][:50] + ("..." if len(row["content"]) > 50 else "")
                    cursor.execute(
                        "UPDATE conversations SET title = %s WHERE id = %s",
                        (title, conversation_id),
                    )

    # ==================== 消息管理 ====================

    def add_message(
        self,
        conversation_id: int,
        role: str,
        content: str,
        model: str | None = None,
        token_count: int | None = None,
    ) -> int:
        """添加一条消息，返回消息ID，同时更新对话消息计数"""
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO messages (conversation_id, role, content, model, token_count) "
                    "VALUES (%s, %s, %s, %s, %s)",
                    (conversation_id, role, content, model, token_count),
                )
                msg_id = cursor.lastrowid

                # 更新对话的消息计数和更新时间
                cursor.execute(
                    "UPDATE conversations SET message_count = message_count + 1, updated_at = NOW() WHERE id = %s",
                    (conversation_id,),
                )
                return msg_id

    def get_messages(self, conversation_id: int) -> list[dict]:
        """获取某个对话的所有消息（按时间正序）"""
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT id, role, content, model, token_count, created_at "
                    "FROM messages WHERE conversation_id = %s ORDER BY id ASC",
                    (conversation_id,),
                )
                return cursor.fetchall()

    def get_message_count(self, conversation_id: int) -> int:
        """获取对话的消息数量"""
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT COUNT(*) AS cnt FROM messages WHERE conversation_id = %s",
                    (conversation_id,),
                )
                return cursor.fetchone()["cnt"]

    def delete_messages(self, conversation_id: int):
        """清空对话的所有消息"""
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM messages WHERE conversation_id = %s",
                    (conversation_id,),
                )
                cursor.execute(
                    "UPDATE conversations SET message_count = 0, updated_at = NOW() WHERE id = %s",
                    (conversation_id,),
                )

    # ==================== 配置管理 ====================

    def get_setting(self, key: str) -> str | None:
        """获取配置项"""
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT setting_value FROM settings WHERE setting_key = %s",
                    (key,),
                )
                row = cursor.fetchone()
                return row["setting_value"] if row else None

    def set_setting(self, key: str, value: str):
        """设置/更新配置项"""
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO settings (setting_key, setting_value) VALUES (%s, %s) "
                    "ON DUPLICATE KEY UPDATE setting_value = VALUES(setting_value), updated_at = NOW()",
                    (key, value),
                )

    def get_all_settings(self) -> dict:
        """获取所有配置"""
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT setting_key, setting_value FROM settings")
                return {row["setting_key"]: row["setting_value"] for row in cursor.fetchall()}

    # ==================== 高级查询 ====================

    def search_conversations(self, keyword: str, limit: int = 20) -> list[dict]:
        """按关键词搜索消息内容，返回匹配的对话"""
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT DISTINCT c.* FROM conversations c "
                    "JOIN messages m ON c.id = m.conversation_id "
                    "WHERE m.content LIKE %s "
                    "ORDER BY c.updated_at DESC LIMIT %s",
                    (f"%{keyword}%", limit),
                )
                return cursor.fetchall()

    def get_conversation_stats(self) -> dict:
        """获取统计信息"""
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) AS total FROM conversations")
                total_conv = cursor.fetchone()["total"]

                cursor.execute("SELECT COUNT(*) AS total FROM messages")
                total_msg = cursor.fetchone()["total"]

                cursor.execute(
                    "SELECT role, COUNT(*) AS cnt FROM messages GROUP BY role"
                )
                role_stats = {row["role"]: row["cnt"] for row in cursor.fetchall()}

                return {
                    "total_conversations": total_conv,
                    "total_messages": total_msg,
                    "by_role": role_stats,
                }


# ==================== 便捷函数（模块级） ====================

# 全局单例（懒加载）
_db_instance: DatabaseManager | None = None


def get_db() -> DatabaseManager:
    """获取全局数据库管理器单例"""
    global _db_instance
    if _db_instance is None:
        _db_instance = DatabaseManager()
    return _db_instance