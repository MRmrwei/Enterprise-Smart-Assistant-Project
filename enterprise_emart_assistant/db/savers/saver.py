from db.savers.factory import create_saver
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer
from pydantics.decision import AIDecision
from pydantics.intentions import Intention

SAVER = None


async def get_saver():
    global SAVER
    if SAVER is None:
        serde = JsonPlusSerializer(allowed_msgpack_modules=[Intention, AIDecision])
        SAVER = await create_saver(serde=serde)
    return SAVER
