import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app

# In-memory SQLite for tests. StaticPool holds a single connection open for the
# whole session, which is what makes ":memory:" usable - a fresh connection
# would otherwise get its own empty database.
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Same shape as the real get_db, pointed at the test engine."""
    db = TestSession()
    try:
        yield db
    finally:
        db.close()


# Swap the app's database dependency for the test one - app/ stays untouched.
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def reset_db():
    """Fresh schema around every test, so nothing leaks between them."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    """TestClient talks to the app in-process - no server, no port."""
    return TestClient(app)


@pytest.fixture
def sample_book(client):
    """A book already in the database, for tests that need existing data."""
    response = client.post("/books", json={
        "title": "Test Book",
        "author": "Test Author",
        "price": 19.99,
    })
    assert response.status_code == 201, response.text
    return response.json()
