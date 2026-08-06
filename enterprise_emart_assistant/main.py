import uvicorn
from fastapi import FastAPI
from core.middlewares.context import ContextMiddleware
from core.boot import lifespan

app = FastAPI(lifespan=lifespan)

app.add_middleware(ContextMiddleware)

   
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8084, reload=True)