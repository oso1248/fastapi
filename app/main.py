from fastapi import FastAPI
from . import models
from . database import engine, get_db
from .routers import post, user, auth, vote
from fastapi.middleware.cors import CORSMiddleware

# models.Base.metadata.create_all(bind=engine) # when not using ALEMBIC to create/track tables


app = FastAPI()

origins = ['https://www.google.com', '*']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get('/', tags=['ROOT'])
async def root():
    return {'detail': 'Hello World!'}

app.include_router(auth.router)
app.include_router(user.router)
app.include_router(post.router)
app.include_router(vote.router)
