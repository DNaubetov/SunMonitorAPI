from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

from database.connection import Settings
from routes.api_key import api_key_router
from routes.chart_all_inv import data_all_inv_router
from routes.events import event_router
from routes.users import user_router
from routes.controllers import controller_router
from routes.invertors import inverter_router
from routes.registers import register_router
from routes.data_rs import data_router
from utility.ip import get_local_ip


@asynccontextmanager
async def lifespan(app: FastAPI):
    await settings.initialize_database()
    yield


app = FastAPI(lifespan=lifespan)

settings = Settings()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes

app.include_router(user_router, prefix="/user")
app.include_router(controller_router, prefix='/controller')
app.include_router(inverter_router, prefix='/inverter')
app.include_router(register_router, prefix='/register')
app.include_router(data_all_inv_router, prefix='/data/chart')
app.include_router(data_router, prefix='/data')
app.include_router(api_key_router, prefix='/key')


@app.get("/")
async def home():
    return RedirectResponse(url="/docs")


if __name__ == '__main__':
    # uvicorn.run("main:app", host=get_local_ip(), port=8080, reload=True)
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)

