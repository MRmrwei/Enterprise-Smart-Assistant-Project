from configs.config import config
from langgraph.checkpoint.memory import InMemorySaver, BaseCheckpointSaver
from db.savers.pg import get_postgres_saver


async def create_saver(**kwargs) -> BaseCheckpointSaver:
    check_type = config.get("CHECKPOINT_TPYE", "local")
    if check_type == "postgre":
        return await get_postgres_saver(**kwargs)
    else:
        return InMemorySaver(**kwargs)



