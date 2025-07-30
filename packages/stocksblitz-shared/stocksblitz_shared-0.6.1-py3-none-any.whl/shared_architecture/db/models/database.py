from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

Base = declarative_base()
engine = create_engine("postgresql://tradmin:tradpass@timescaledb_secure:5432/tradingdb")  # Use container name for Docker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)