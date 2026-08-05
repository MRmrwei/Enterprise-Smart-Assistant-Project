from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager
from tools.base import tools_container
from langchain_mcp_adapters.client import MultiServerMCPClient
from core.context import context

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up")


    yield

    print("Shutting down")



