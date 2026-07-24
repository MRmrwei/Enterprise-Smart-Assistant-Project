CREATE TABLE IF NOT EXISTS ai_user_role
(
    id         BIGINT  NOT NULL AUTO_INCREMENT PRIMARY KEY,
    user_id    INT(10) NOT NULL,
    role_id    INT(10) NOT NULL,
    created_at INT(11) NULL COMMENT '创建时间',
    updated_at INT(11) NULL COMMENT '更新时间',
    deleted_at INT(11) DEFAULT 0 COMMENT '删除时间',
    UNIQUE KEY `uk_user_role` (`user_id`, `role_id`),
    KEY `idx_role_id` (`role_id`)

) COMMENT = '用户角色关联表';

INSERT INTO ai_user_role (user_id, role_id, created_at, updated_at)
VALUES (1, 1, UNIX_TIMESTAMP(NOW()), UNIX_TIMESTAMP(NOW())),
       (2, 2, UNIX_TIMESTAMP(NOW()), UNIX_TIMESTAMP(NOW())),
       (3, 2, UNIX_TIMESTAMP(NOW()), UNIX_TIMESTAMP(NOW())),
       (4, 3, UNIX_TIMESTAMP(NOW()), UNIX_TIMESTAMP(NOW())),
       (5, 3, UNIX_TIMESTAMP(NOW()), UNIX_TIMESTAMP(NOW())),
       (6, 3, UNIX_TIMESTAMP(NOW()), UNIX_TIMESTAMP(NOW()));