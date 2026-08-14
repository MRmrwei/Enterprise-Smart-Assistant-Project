from configs.config import config
from psycopg_pool import ConnectionPool
from langgraph.checkpoint.postgres import PostgresSaver


def get_postgres_saver(**kwargs):
    db_url = config.get("CHECKPOINT_DB_URL")
    if db_url is None:
        raise Exception("缺少数据库连接信息")

    # 创建连接池
    pool = ConnectionPool(
        db_url,
        min_size=2,  # 最小连接数[reference:6]
        max_size=10,  # 最大连接数[reference:7][reference:8]
        max_idle=300.0,  # 空闲连接关闭时间（秒）[reference:9][reference:10]
        kwargs={
            "autocommit": True,  # 必须开启[reference:11][reference:12]
            # "row_factory": dict_row  # 如果遇到类型问题可以尝试开启[reference:13]
        },
    )
    kwargs["pool"] = pool
    # 使用连接池创建检查点器（全局单例）
    checkpointer = PostgresSaver(**kwargs)
    checkpointer.setup()  # 首次运行创建表
