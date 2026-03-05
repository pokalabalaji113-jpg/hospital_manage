from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Change password if needed
db_url = "postgresql://postgres:Bala7569@localhost:5432/hospitalproject"

engine = create_engine(db_url)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)
