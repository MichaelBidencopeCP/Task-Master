import asyncio
import pytest
from httpx import AsyncClient, ASGITransport
from todo.main import create_app
from todo.models import Base 
from todo.database import get_db
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, AsyncSession

SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./test_todo.db"
engine: AsyncEngine = create_async_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

@pytest.fixture(scope="session")
async def setup_database():
    """Create database tables before tests run"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Cleanup after tests
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture()
async def db_session(setup_database):
    """Create a new database session for each test"""
    async with AsyncSession(bind=engine, expire_on_commit=False) as session:
        yield session

@pytest.fixture(scope="session")
def event_loop():
    """
    Create one asyncio event loop for the entire test session.
    Why: async tests need a loop to run on; making it explicit avoids platform quirks.
    """
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture()
async def app(setup_database):
    """
    Build a fresh FastAPI app for each test by calling the factory.
    Fresh app = no cross-test leakage of state or overrides.
    """
    app = create_app()
    app.dependency_overrides = {}
    
    async def get_test_db():
        async with AsyncSession(bind=engine, expire_on_commit=False) as session:
            yield session
    
    app.dependency_overrides[get_db] = get_test_db
    yield app

@pytest.fixture()
async def client(app):
    """
    Create an async HTTP client that talks to the app IN MEMORY.
    No real server or sockets; it's fast and respects app lifespan events.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac