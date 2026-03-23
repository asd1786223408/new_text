-- 简历附件表
CREATE TABLE IF NOT EXISTS resume_attachments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    file_name VARCHAR(255) NOT NULL COMMENT '原始文件名',
    cos_key VARCHAR(512) NOT NULL COMMENT 'COS 存储路径',
    file_size INT DEFAULT 0 COMMENT '文件大小 (字节)',
    file_type VARCHAR(100) COMMENT '文件类型/MIME 类型',
    position_id INT COMMENT '关联岗位 ID',
    position_name VARCHAR(255) COMMENT '岗位名称',
    candidate_name VARCHAR(100) COMMENT '候选人姓名',
    candidate_phone VARCHAR(20) COMMENT '候选人电话',
    candidate_email VARCHAR(100) COMMENT '候选人邮箱',
    upload_user_id INT COMMENT '上传用户 ID',
    upload_username VARCHAR(100) COMMENT '上传用户名',
    status TINYINT DEFAULT 1 COMMENT '状态：1-有效，0-无效',
    download_count INT DEFAULT 0 COMMENT '下载次数',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_position (position_id),
    INDEX idx_status (status),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='简历附件表';
