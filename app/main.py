from fastapi import FastAPI

from app.database import Base, engine
from app.models import book  # noqa: F401 - registers the books table with Base
from app.routers import books

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Books CRUD API",
    description="A books API used to demonstrate a pytest test suite",
    version="1.0.0",
)

app.include_router(books.router)


@app.get("/")
def root():
    return {"app": "Books CRUD API", "docs": "/docs"}
