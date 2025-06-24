from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import router  # import the APIRouter
from db import engine, Base  # import the database engine and Base
from models import User  # import the User model
Base.metadata.create_all(bind=engine)
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.get("/")
def read_root():
    return {"message": "FinSight Backend Running!"}
