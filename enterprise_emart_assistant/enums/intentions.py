from enum import Enum


class Intentions(Enum):
    QA = "qa"
    FILL_FORM = "fill_form"
    KNOWLEDGE_INGEST = "knowledge_ingest"
    DATA_QUERY = "data_query"
    UNKNOWN = "unknown"
