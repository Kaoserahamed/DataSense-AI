from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, List, Any


class DatasetBase(BaseModel):
    name: str


class DatasetCreate(DatasetBase):
    project_id: int


class DatasetResponse(DatasetBase):
    id: int
    file_path: str
    file_type: str
    file_size: Optional[int]
    project_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class DatasetMetadataResponse(BaseModel):
    id: int
    dataset_id: int
    rows: Optional[int]
    columns: Optional[int]
    column_info: Optional[Dict[str, Any]]
    missing_values: Optional[Dict[str, Any]]
    duplicates: Optional[int]
    numeric_columns: Optional[List[str]]
    categorical_columns: Optional[List[str]]
    ai_summary: Optional[str]
    
    class Config:
        from_attributes = True


class DatasetWithMetadata(DatasetResponse):
    metadata: Optional[DatasetMetadataResponse] = None
