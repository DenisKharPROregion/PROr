# db.py
import datetime
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker

from config import DATABASE_URL

Base = declarative_base()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class MasterClass(Base):
    __tablename__ = "master_classes"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    max_participants = Column(Integer)
    is_open = Column(Boolean, default=False)

class Registration(Base):
    __tablename__ = "registrations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    master_class_id = Column(Integer)
    full_name = Column(String)
    phone_number = Column(String)
    registered_at = Column(DateTime, default=datetime.datetime.now)

def init_db():
    Base.metadata.create_all(bind=engine)
    
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
