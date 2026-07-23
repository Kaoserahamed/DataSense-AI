from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.connection import Base


class Dataset(Base):
    __tablename__ = "datasets"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    file_size = Column(Integer)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="datasets")
    dataset_metadata = relationship("DatasetMetadata", back_populates="dataset", uselist=False, cascade="all, delete-orphan")
    chat_history = relationship("ChatHistory", back_populates="dataset", cascade="all, delete-orphan")


class DatasetMetadata(Base):
    __tablename__ = "dataset_metadata"
    
    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id"), nullable=False, unique=True)
    rows = Column(Integer)
    columns = Column(Integer)
    column_info = Column(JSON)
    missing_values = Column(JSON)
    duplicates = Column(Integer)
    numeric_columns = Column(JSON)
    categorical_columns = Column(JSON)
    ai_summary = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    dataset = relationship("Dataset", back_populates="dataset_metadata")
