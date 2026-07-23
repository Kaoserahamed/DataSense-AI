from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.connection import Base


class Chart(Base):
    __tablename__ = "charts"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    chart_type = Column(String, nullable=False)
    config = Column(JSON)
    data = Column(JSON)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    dataset_id = Column(Integer, ForeignKey("datasets.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="charts")
