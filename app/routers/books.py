from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.book import Book
from app.schemas.book import BookCreate, BookResponse, BookUpdate

router = APIRouter(prefix="/books", tags=["books"])


@router.post("", response_model=BookResponse, status_code=201, summary="Create a book")
def create_book(payload: BookCreate, db: Session = Depends(get_db)):
    book = Book(**payload.model_dump())
    db.add(book)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="A book with that title already exists")
    db.refresh(book)
    return book


@router.get("", response_model=list[BookResponse], summary="List books")
def list_books(
    author: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
):
    query = db.query(Book)
    if author is not None:
        query = query.filter(Book.author == author)
    return query.order_by(Book.id).all()


@router.get("/{book_id}", response_model=BookResponse, summary="Get one book")
def get_book(book_id: int, db: Session = Depends(get_db)):
    book = db.get(Book, book_id)
    if book is None:
        raise HTTPException(status_code=404, detail=f"Book {book_id} not found")
    return book


@router.patch("/{book_id}", response_model=BookResponse, summary="Update a book")
def patch_book(book_id: int, payload: BookUpdate, db: Session = Depends(get_db)):
    book = db.get(Book, book_id)
    if book is None:
        raise HTTPException(status_code=404, detail=f"Book {book_id} not found")

    changes = payload.model_dump(exclude_unset=True)
    for field, value in changes.items():
        setattr(book, field, value)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="A book with that title already exists")
    db.refresh(book)
    return book


@router.delete("/{book_id}", status_code=204, summary="Delete a book")
def delete_book(book_id: int, db: Session = Depends(get_db)):
    book = db.get(Book, book_id)
    if book is None:
        raise HTTPException(status_code=404, detail=f"Book {book_id} not found")
    db.delete(book)
    db.commit()
    return None
