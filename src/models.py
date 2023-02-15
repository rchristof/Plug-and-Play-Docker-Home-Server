from sqlalchemy import Column, Integer, String, Boolean, LargeBinary, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Image(Base):
    __tablename__ = 'images'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    data = Column(LargeBinary, nullable=False)
    deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime, nullable=True)

class Archive(Base):
    __tablename__ = 'archives'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    data = Column(LargeBinary, nullable=False)
    deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime, nullable=True)
