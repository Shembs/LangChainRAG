import json
import os
from typing import Sequence

from langchain_core.messages import messages_from_dict, messages_to_dict, BaseMessage
from langchain_core.chat_history import BaseChatMessageHistory


def get_history(session_id):
    """获取文件聊天历史记录"""
    return FileChatMessageHistory(session_id, "./chat_history")


class FileChatMessageHistory(BaseChatMessageHistory):
    """基于文件的聊天消息历史记录"""

    def __init__(self, session_id, storage_path):
        self.session_id = session_id
        self.storage_path = storage_path

        self.file_path = os.path.join(self.storage_path, self.session_id)
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)

    def add_message(self, message: BaseMessage) -> None:
        """添加单条消息"""
        self.add_messages([message])

    def add_messages(self, messages: Sequence[BaseMessage]) -> None:
        """批量添加消息"""
        all_messages = list(self.messages)
        all_messages.extend(messages)

        new_messages = messages_to_dict(all_messages)
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(new_messages, f, ensure_ascii=False)

    @property
    def messages(self) -> list[BaseMessage]:
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                messages_data = json.load(f)
                if not messages_data:
                    return []
                return messages_from_dict(messages_data)
        except FileNotFoundError:
            return []
        except (json.JSONDecodeError, ValueError):
            # 文件损坏时返回空列表，下次写入会覆盖
            return []

    def clear(self) -> None:
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump([], f)



