-- ============================================================
-- Noir AI 聊天助手 — 数据库建表脚本
-- 数据库: MySQL
-- 执行方式: mysql -u root -p < schema.sql
-- ============================================================

-- 创建数据库
CREATE DATABASE IF NOT EXISTS noir_ai_chat
    DEFAULT CHARACTER SET utf8mb4
    DEFAULT COLLATE utf8mb4_unicode_ci;

USE noir_ai_chat;

-- ============================================================
-- 对话表：一次完整的对话会话
-- ============================================================
CREATE TABLE IF NOT EXISTS conversations (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    title           VARCHAR(200)    NOT NULL DEFAULT '新对话',
    provider        VARCHAR(50)     NOT NULL COMMENT '提供商ID，如 deepseek, openai',
    model           VARCHAR(100)    NOT NULL COMMENT '模型名称',
    message_count   INT             NOT NULL DEFAULT 0 COMMENT '消息数量',
    created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    INDEX idx_created_at (created_at DESC),
    INDEX idx_updated_at (updated_at DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='对话会话表';


-- ============================================================
-- 消息表：对话中的每条消息
-- ============================================================
CREATE TABLE IF NOT EXISTS messages (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    conversation_id INT             NOT NULL COMMENT '所属对话ID',
    role            ENUM('user', 'assistant', 'system') NOT NULL COMMENT '消息角色',
    content         TEXT            NOT NULL COMMENT '消息内容',
    model           VARCHAR(100)    DEFAULT NULL COMMENT '生成该消息的模型',
    token_count     INT             DEFAULT NULL COMMENT 'Token 消耗量',
    created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_conversation_id (conversation_id),
    INDEX idx_created_at (created_at),
    CONSTRAINT fk_messages_conversation
        FOREIGN KEY (conversation_id) REFERENCES conversations(id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='消息记录表';


-- ============================================================
-- 系统配置表
-- ============================================================
CREATE TABLE IF NOT EXISTS settings (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    setting_key     VARCHAR(100)    NOT NULL UNIQUE COMMENT '配置键',
    setting_value   TEXT            DEFAULT NULL COMMENT '配置值',
    updated_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='系统配置表';


-- 插入默认配置
INSERT IGNORE INTO settings (setting_key, setting_value) VALUES
    ('default_provider', 'deepseek'),
    ('default_model', 'deepseek-v4-pro'),
    ('default_temperature', '0.7'),
    ('default_system_prompt', '你叫小新是一个温柔的AI助手，帮助用户解决问题');