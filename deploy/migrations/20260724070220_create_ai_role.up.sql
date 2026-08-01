CREATE TABLE ai_role
(
    id         BIGINT             NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name       VARCHAR(50)        NOT NULL COMMENT '角色名称',
    code       VARCHAR(50) UNIQUE NOT NULL COMMENT '角色编码',
    weight     INT(11)            NOT NULL COMMENT '权重（由高到低）',
    created_at INT(11)            NULL COMMENT '创建时间',
    updated_at INT(11)            NULL COMMENT '更新时间',
    deleted_at INT(11) DEFAULT 0 COMMENT '删除时间'
) COMMENT ='角色表';

INSERT INTO ai_role (id, name, code, weight, created_at, updated_at)
VALUES (1, '管理员', 'boss', 999, UNIX_TIMESTAMP(NOW()), UNIX_TIMESTAMP(NOW())),
       (2, '主管', 'manager', 2, UNIX_TIMESTAMP(NOW()), UNIX_TIMESTAMP(NOW())),
       (3, '员工', 'employee', 1, UNIX_TIMESTAMP(NOW()), UNIX_TIMESTAMP(NOW()));