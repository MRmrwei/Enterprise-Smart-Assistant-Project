from configs.config import config
from psycopg_pool import AsyncConnectionPool
from psycopg.rows import dict_row
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver


async def get_postgres_saver(**kwargs):
    """获取异步PostgreSQL检查点器（适配ainvoke/astream）"""
    db_url = config.get("CHECKPOINT_DB_URL")
    if db_url is None:
        raise Exception("缺少数据库连接信息")

    # 1. 创建异步连接池（调整参数避免后台错误）
    pool = AsyncConnectionPool(
        db_url,
        min_size=0,           # 不预创建连接，避免后台连接尝试
        max_size=5,           # 合理限制
        max_idle=60,          # 空闲连接关闭时间
        timeout=30,           # 连接超时
        max_lifetime=600,     # 连接存活时间
        # 禁用后台健康检查（避免额外连接错误）
        check=None,
        kwargs={
            "autocommit": True,
            "row_factory": dict_row,
        },
    )

    # 2. 初始化连接池（显式打开，此时不会创建连接，因为 min_size=0）
    await pool.open()
    print("✅ 数据库连接池已初始化")

    # kwargs.update({"conn": pool})
    # 3. 创建异步检查点器
    checkpointer = AsyncPostgresSaver(pool, **kwargs)

    # 4. 创建表（首次运行）
    await checkpointer.setup()
    print("✅ 检查点表创建/校验成功")

    return checkpointer