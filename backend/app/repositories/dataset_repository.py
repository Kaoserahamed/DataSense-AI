from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.dataset import Dataset, DatasetMetadata


class DatasetRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, dataset_id: int) -> Optional[Dataset]:
        return self.db.query(Dataset).filter(Dataset.id == dataset_id).first()
    
    def get_all_by_project(self, project_id: int) -> List[Dataset]:
        return self.db.query(Dataset).filter(Dataset.project_id == project_id).all()
    
    def create(self, name: str, file_path: str, file_type: str, file_size: int, project_id: int) -> Dataset:
        dataset = Dataset(
            name=name,
            file_path=file_path,
            file_type=file_type,
            file_size=file_size,
            project_id=project_id
        )
        self.db.add(dataset)
        self.db.commit()
        self.db.refresh(dataset)
        return dataset
    
    def create_metadata(self, dataset_id: int, metadata_dict: dict) -> DatasetMetadata:
        metadata = DatasetMetadata(
            dataset_id=dataset_id,
            **metadata_dict
        )
        self.db.add(metadata)
        self.db.commit()
        self.db.refresh(metadata)
        return metadata
    
    def delete(self, dataset_id: int) -> bool:
        dataset = self.get_by_id(dataset_id)
        if not dataset:
            return False
        
        self.db.delete(dataset)
        self.db.commit()
        return True
