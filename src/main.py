from fastapi import FastAPI
from contextlib import asynccontextmanager

from src.api.agent import agent_router
from src.api.dependencies import(
    init_app_dependencies,
    get_app_dependencies,
)

async def startup_span(app:FastAPI):
    init_app_dependencies()
    app.state.depends= get_app_dependencies()



@asynccontextmanager
async def lifespan(app: FastAPI):
    await startup_span(app)
    yield


app=FastAPI(lifespan=lifespan)
app.include_router(agent_router)

