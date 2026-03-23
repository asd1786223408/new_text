-- 用户平台数据库初始化脚本
-- 包含：用户、部门、角色、权限、登录日志、简历、岗位

-- 启用外键
SET FOREIGN_KEY_CHECKS = 1;

-- ==================== 基础 RBAC 表 ====================

-- 部门表
CREATE TABLE IF NOT EXISTS departments (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL COMMENT '部门名称',
    parent_id BIGINT DEFAULT 0 COMMENT '父部门 ID（0 为顶级）',
    level INT DEFAULT 1 COMMENT '层级',
    sort INT DEFAULT 0 COMMENT '排序',
    leader_id BIGINT COMMENT '负责人 ID',
    status TINYINT DEFAULT 1 COMMENT '状态：1-正常，0-禁用',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_parent (parent_id),
    INDEX idx_level (level)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='部门表';

-- 角色表
CREATE TABLE IF NOT EXISTS roles (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE COMMENT '角色标识',
    display_name VARCHAR(100) NOT NULL COMMENT '显示名称',
    description TEXT COMMENT '描述',
    permissions JSON COMMENT '权限列表（冗余）',
    status TINYINT DEFAULT 1 COMMENT '状态：1-正常，0-禁用',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='角色表';

-- 权限表
CREATE TABLE IF NOT EXISTS permissions (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE COMMENT '权限标识',
    display_name VARCHAR(100) NOT NULL COMMENT '显示名称',
    module VARCHAR(50) NOT NULL COMMENT '所属模块',
    action VARCHAR(50) NOT NULL COMMENT '操作类型',
    icon VARCHAR(50) COMMENT '图标',
    sort INT DEFAULT 0 COMMENT '排序',
    status TINYINT DEFAULT 1 COMMENT '状态：1-正常，0-禁用',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_module (module)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='权限表';

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE COMMENT '用户名',
    password_hash VARCHAR(255) NOT NULL COMMENT '密码哈希',
    email VARCHAR(100) UNIQUE COMMENT '邮箱',
    phone VARCHAR(20) UNIQUE COMMENT '手机号',
    avatar VARCHAR(255) COMMENT '头像 URL',
    nickname VARCHAR(50) COMMENT '昵称',
    gender TINYINT DEFAULT 0 COMMENT '性别：0-未知，1-男，2-女',
    birthday DATE COMMENT '生日',
    department_id BIGINT COMMENT '部门 ID',
    position VARCHAR(50) COMMENT '职位',
    status TINYINT DEFAULT 1 COMMENT '状态：1-正常，0-禁用，2-锁定',
    permissions JSON COMMENT '权限列表（冗余存储）',
    last_login_at DATETIME COMMENT '最后登录时间',
    last_login_ip VARCHAR(50) COMMENT '最后登录 IP',
    password_changed_at DATETIME COMMENT '密码最后修改时间',
    login_failure_count INT DEFAULT 0 COMMENT '登录失败次数',
    locked_until DATETIME COMMENT '锁定截止时间',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted_at DATETIME COMMENT '删除时间（软删除）',
    INDEX idx_department (department_id),
    INDEX idx_status (status),
    INDEX idx_email (email),
    INDEX idx_phone (phone)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- 用户角色关联表
CREATE TABLE IF NOT EXISTS user_roles (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL COMMENT '用户 ID',
    role_id BIGINT NOT NULL COMMENT '角色 ID',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_user_role (user_id, role_id),
    INDEX idx_role (role_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户角色关联表';

-- 登录日志表
CREATE TABLE IF NOT EXISTS login_logs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT COMMENT '用户 ID',
    login_type VARCHAR(20) DEFAULT 'password' COMMENT '登录方式：password/phone/email',
    status TINYINT DEFAULT 1 COMMENT '状态：0-失败，1-成功',
    ip VARCHAR(50) COMMENT 'IP 地址',
    user_agent VARCHAR(255) COMMENT 'User-Agent',
    fail_reason VARCHAR(255) COMMENT '失败原因',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user (user_id),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='登录日志表';

-- ==================== 简历管理表 ====================

-- 岗位表
CREATE TABLE IF NOT EXISTS positions (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL COMMENT '岗位名称',
    description TEXT COMMENT '岗位描述',
    requirements TEXT COMMENT '任职要求',
    department VARCHAR(100) COMMENT '所属部门',
    skills_required JSON COMMENT '技能要求列表',
    headcount INT DEFAULT 1 COMMENT '招聘人数',
    hire_by_date DATE COMMENT '期望入职时间',
    status TINYINT DEFAULT 1 COMMENT '状态：1-招聘中，0-已结束',
    created_by BIGINT COMMENT '创建人 ID',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_status (status),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='岗位表';

-- 简历附件表
CREATE TABLE IF NOT EXISTS resume_attachments (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    file_name VARCHAR(255) NOT NULL COMMENT '原始文件名',
    cos_key VARCHAR(512) NOT NULL COMMENT 'COS 存储路径',
    file_size INT DEFAULT 0 COMMENT '文件大小 (字节)',
    file_type VARCHAR(100) COMMENT '文件类型/MIME 类型',
    position_id BIGINT COMMENT '关联岗位 ID',
    position_name VARCHAR(255) COMMENT '岗位名称',
    candidate_name VARCHAR(100) COMMENT '候选人姓名',
    candidate_phone VARCHAR(20) COMMENT '候选人电话',
    candidate_email VARCHAR(100) COMMENT '候选人邮箱',
    upload_user_id BIGINT COMMENT '上传用户 ID',
    upload_username VARCHAR(100) COMMENT '上传用户名',
    status TINYINT DEFAULT 1 COMMENT '状态：1-有效，0-无效',
    download_count INT DEFAULT 0 COMMENT '下载次数',
    analysis_score INT COMMENT 'AI 打分 0-100',
    analysis_report JSON COMMENT 'AI 分析报告',
    analyzed_at DATETIME COMMENT '分析时间',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_position (position_id),
    INDEX idx_status (status),
    INDEX idx_created (created_at),
    INDEX idx_score (analysis_score)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='简历附件表';

-- ==================== 初始数据 ====================

-- 默认权限
INSERT INTO permissions (name, display_name, module, action, sort) VALUES
('user:create', '创建用户', 'user', 'create', 1),
('user:read', '查看用户', 'user', 'read', 2),
('user:update', '编辑用户', 'user', 'update', 3),
('user:delete', '删除用户', 'user', 'delete', 4),
('role:create', '创建角色', 'role', 'create', 5),
('role:read', '查看角色', 'role', 'read', 6),
('role:update', '编辑角色', 'role', 'update', 7),
('role:delete', '删除角色', 'role', 'delete', 8),
('dept:read', '查看部门', 'dept', 'read', 9),
('dept:manage', '管理部门', 'dept', 'manage', 10),
('stat:view', '查看统计', 'stat', 'view', 11),
('system:config', '系统配置', 'system', 'config', 12),
('resume:upload', '上传简历', 'resume', 'upload', 13),
('resume:read', '查看简历', 'resume', 'read', 14),
('resume:delete', '删除简历', 'resume', 'delete', 15),
('resume:analyze', '分析简历', 'resume', 'analyze', 16),
('position:create', '创建岗位', 'position', 'create', 17),
('position:read', '查看岗位', 'position', 'read', 18),
('position:update', '编辑岗位', 'position', 'update', 19),
('position:delete', '删除岗位', 'position', 'delete', 20);

-- 默认角色
INSERT INTO roles (name, display_name, description, permissions, status) VALUES
('super_admin', '超级管理员', '拥有所有权限',
 '["user:create","user:read","user:update","user:delete","role:create","role:read","role:update","role:delete","dept:read","dept:manage","stat:view","system:config","resume:upload","resume:read","resume:delete","resume:analyze","position:create","position:read","position:update","position:delete"]', 1),
('admin', '管理员', '拥有大部分权限',
 '["user:read","user:update","role:read","dept:read","stat:view","resume:upload","resume:read","resume:delete","resume:analyze","position:create","position:read","position:update"]', 1),
('user', '普通用户', '只读权限',
 '["user:read","dept:read","stat:view","resume:read","position:read"]', 1);

-- 默认部门
INSERT INTO departments (name, parent_id, level, sort) VALUES
('总公司', 0, 1, 1),
('技术部', 1, 2, 1),
('产品部', 1, 2, 2),
('运营部', 1, 2, 3);

-- 默认管理员（密码：admin123）
INSERT INTO users (username, password_hash, email, nickname, department_id, status, permissions) VALUES
('admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzS3MebAJu', 'admin@example.com', '管理员', 1, 1,
 '["user:create","user:read","user:update","user:delete","role:create","role:read","role:update","role:delete","dept:read","dept:manage","stat:view","system:config","resume:upload","resume:read","resume:delete","resume:analyze","position:create","position:read","position:update","position:delete"]');

-- 关联默认管理员角色
INSERT INTO user_roles (user_id, role_id) VALUES
((SELECT id FROM users WHERE username = 'admin'),
 (SELECT id FROM roles WHERE name = 'super_admin'));
