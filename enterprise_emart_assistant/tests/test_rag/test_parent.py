import asyncio

from services.rags.search import mixed_parent_search


def test_parent_search():
    docs = asyncio.run(mixed_parent_search("微服务架构", 3))
    