CREATE TABLE ai_user
(
    id         BIGINT              NOT NULL AUTO_INCREMENT PRIMARY KEY,
    nickname   VARCHAR(100)        NOT NULL COMMENT '昵称',
    account    VARCHAR(100) UNIQUE NOT NULL COMMENT '用户账号',
    password   VARCHAR(150)        NOT NULL COMMENT '密码',
    created_at INT(11)             NULL COMMENT '创建时间',
    updated_at INT(11)             NULL COMMENT '更新时间',
    deleted_at INT(11) DEFAULT 0 COMMENT '删除时间'
) COMMENT ='用户表';

INSERT INTO ai_user (id, nickname, account, password, created_at, updated_at)
VALUES (1, '老板', 'admin', '$2a$10$R/vzxysdmGZN63gcYQ6xCewDWl5EoUs1DpDJgYxhaNghrhNHA7JTG', UNIX_TIMESTAMP(NOW()),
        UNIX_TIMESTAMP(NOW())),
       (2, '行政', '1231', '$2a$10$wr.fBW644OZCgGKc7nxG2.nJJIlWwjR/NxxkL.cE87hP7oy716Yde', UNIX_TIMESTAMP(NOW()),
        UNIX_TIMESTAMP(NOW())),
       (3, '财务', '1232', '$2a$10$wr.fBW644OZCgGKc7nxG2.nJJIlWwjR/NxxkL.cE87hP7oy716Yde', UNIX_TIMESTAMP(NOW()),
        UNIX_TIMESTAMP(NOW())),
       (4, '牛马1', '3211', '$2a$10$wr.fBW644OZCgGKc7nxG2.nJJIlWwjR/NxxkL.cE87hP7oy716Yde', UNIX_TIMESTAMP(NOW()),
        UNIX_TIMESTAMP(NOW())),
       (5, '牛马2', '3212', '$2a$10$wr.fBW644OZCgGKc7nxG2.nJJIlWwjR/NxxkL.cE87hP7oy716Yde', UNIX_TIMESTAMP(NOW()),
        UNIX_TIMESTAMP(NOW())),
       (6, '牛马3', '3213', '$2a$10$wr.fBW644OZCgGKc7nxG2.nJJIlWwjR/NxxkL.cE87hP7oy716Yde', UNIX_TIMESTAMP(NOW()),
        UNIX_TIMESTAMP(NOW()));