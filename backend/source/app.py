from fastapi import FastAPI
from auth.endpoints import router as user_router


app = FastAPI()
app.include_router(user_router)