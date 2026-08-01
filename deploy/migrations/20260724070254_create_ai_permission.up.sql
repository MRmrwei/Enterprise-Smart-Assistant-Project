CREATE TABLE ai_premission
(
    id         BIGINT       NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name       VARCHAR(50)  NOT NULL COMMENT '权限名称',
    path       VARCHAR(100) NULL COMMENT '权限路径',
    perms      VARCHAR(100) NULL COMMENT '权限标识符',
    created_at INT(11)          NULL COMMENT '创建时间',
    updated_at INT(11)          NULL COMMENT '更新时间',
    deleted_at INT(11) DEFAULT 0 COMMENT '删除时间'
) COMMENT ='角色权限表';