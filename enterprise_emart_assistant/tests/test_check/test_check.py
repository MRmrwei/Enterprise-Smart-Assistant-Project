from db.savers.factory import get_saver


class test:
    def __init__(self,*, agent: str | None = None):
        self.agent = agent

def get_test(**kwargs):
    return test(**kwargs)
def test_get_checkpoin():
    get_saver()
