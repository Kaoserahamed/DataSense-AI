from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate


class ProjectRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, project_id: int) -> Optional[Project]:
        return self.db.query(Project).filter(Project.id == project_id).first()
    
    def get_all(self) -> List[Project]:
        return self.db.query(Project).all()
    
    def create(self, project_data: ProjectCreate) -> Project:
        project = Project(
            name=project_data.name,
            description=project_data.description
        )
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        return project
    
    def update(self, project_id: int, project_data: ProjectUpdate) -> Optional[Project]:
        project = self.get_by_id(project_id)
        if not project:
            return None
        
        if project_data.name is not None:
            project.name = project_data.name
        if project_data.description is not None:
            project.description = project_data.description
        
        self.db.commit()
        self.db.refresh(project)
        return project
    
    def delete(self, project_id: int) -> bool:
        project = self.get_by_id(project_id)
        if not project:
            return False
        
        self.db.delete(project)
        self.db.commit()
        return True
