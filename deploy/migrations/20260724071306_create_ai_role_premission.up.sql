CREATE TABLE IF NOT EXISTS ai_role_permission (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  role_id INTEGER NOT NULL,
  permission_id INTEGER NOT NULL,
  created_at INT(11)     NULL COMMENT '创建时间',
  updated_at INT(11)     NULL COMMENT '更新时间',
  deleted_at INT(11) DEFAULT 0 COMMENT '删除时间',
  KEY `idx_role_id` (role_id),
  KEY `idx_permission_id` (permission_id)
) COMMENT='角色权限关联表';