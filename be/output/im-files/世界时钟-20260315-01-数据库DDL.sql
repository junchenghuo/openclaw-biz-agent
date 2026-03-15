-- World Clock Database Schema
-- Database: worldclock

CREATE DATABASE IF NOT EXISTS worldclock DEFAULT CHARSET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE worldclock;

-- 时区配置表
CREATE TABLE IF NOT EXISTS timezone_config (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    name VARCHAR(50) NOT NULL COMMENT '时区名称',
    country VARCHAR(50) COMMENT '所属国家',
    timezone VARCHAR(100) NOT NULL COMMENT '时区标识(IANA时区)',
    utc_offset VARCHAR(20) COMMENT 'UTC偏移量',
    display_order INT DEFAULT 0 COMMENT '显示顺序',
    is_active TINYINT DEFAULT 1 COMMENT '是否启用(1启用/0禁用)',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_timezone (timezone),
    INDEX idx_display_order (display_order),
    INDEX idx_is_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='时区配置表';

-- 初始化8国时钟数据
INSERT INTO timezone_config (name, country, timezone, utc_offset, display_order) VALUES
('北京', '中国', 'Asia/Shanghai', '+08:00', 1),
('东京', '日本', 'Asia/Tokyo', '+09:00', 2),
('伦敦', '英国', 'Europe/London', '+00:00', 3),
('纽约', '美国', 'America/New_York', '-05:00', 4),
('巴黎', '法国', 'Europe/Paris', '+01:00', 5),
('悉尼', '澳大利亚', 'Australia/Sydney', '+11:00', 6),
('迪拜', '阿联酋', 'Asia/Dubai', '+04:00', 7),
('洛杉矶', '美国', 'America/Los_Angeles', '-08:00', 8)
ON DUPLICATE KEY UPDATE name=VALUES(name);
