from fastapi import FastAPI
from api.agent import agent_router

app=FastAPI()

app.include_router(agent_router)

