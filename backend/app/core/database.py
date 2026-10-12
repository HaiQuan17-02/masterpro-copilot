from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings

# Create engine with connection pooling
engine = create_engine(
    settings.sync_database_url,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """Dependency for obtaining database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def check_db_connection() -> dict:
    """Utility to test active database connectivity."""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT DB_NAME() AS current_db, @@VERSION AS version"))
            row = result.mappings().first()
            return {
                "status": "connected",
                "database": row["current_db"] if row else None,
                "version": row["version"].split("\n")[0] if row else None,
            }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
        }
