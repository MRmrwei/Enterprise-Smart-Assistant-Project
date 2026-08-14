from db.savers.factory import create_saver
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer
from pydantics.decision import AIDecision
from pydantics.intentions import Intention

SAVER = None


def get_saver():
    if SAVER is None:
        serde = JsonPlusSerializer(allowed_msgpack_modules=[Intention, AIDecision])
        SAVER = create_saver(serde=serde)
    return SAVER
