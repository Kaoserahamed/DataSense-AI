from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List
import logging
from app.database.connection import get_db
from app.schemas.dataset import DatasetResponse, DatasetWithMetadata
from app.repositories.dataset_repository import DatasetRepository
from app.repositories.project_repository import ProjectRepository
from app.services.dataset_service import DatasetService
from app.ai.profiling_service import ProfilingService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/datasets", tags=["Datasets"])


@router.post("", response_model=DatasetWithMetadata, status_code=status.HTTP_201_CREATED)
async def upload_dataset(
    file: UploadFile = File(...),
    project_id: int = Form(...),
    db: Session = Depends(get_db)
):
    # Verify project exists
    project_repo = ProjectRepository(db)
    project = project_repo.get_by_id(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Validate file type
    file_extension = file.filename.split(".")[-1].lower()
    allowed_types = ["csv", "xlsx", "xls", "json", "parquet"]
    
    if file_extension not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not supported. Allowed: {', '.join(allowed_types)}"
        )
    
    # Read and save file
    content = await file.read()
    file_path, file_size = DatasetService.save_file(content, file.filename, project_id)
    
    # Create dataset record
    dataset_repo = DatasetRepository(db)
    dataset = dataset_repo.create(
        name=file.filename,
        file_path=file_path,
        file_type=file_extension,
        file_size=file_size,
        project_id=project_id
    )
    
    # Analyze dataset
    try:
        df = DatasetService.load_dataframe(file_path, file_extension)
        metadata_dict = DatasetService.analyze_dataset(df)
        
        # Generate AI summary
        ai_summary = ProfilingService.generate_dataset_summary(df, metadata_dict)
        metadata_dict["ai_summary"] = ai_summary
        
        # Save metadata
        metadata = dataset_repo.create_metadata(dataset.id, metadata_dict)
        
        # Return dataset with metadata - properly serialize
        return {
            "id": dataset.id,
            "name": dataset.name,
            "file_path": dataset.file_path,
            "file_type": dataset.file_type,
            "file_size": dataset.file_size,
            "project_id": dataset.project_id,
            "created_at": dataset.created_at,
            "metadata": {
                "id": metadata.id,
                "dataset_id": metadata.dataset_id,
                "rows": metadata.rows,
                "columns": metadata.columns,
                "column_info": metadata.column_info,
                "missing_values": metadata.missing_values,
                "duplicates": metadata.duplicates,
                "numeric_columns": metadata.numeric_columns,
                "categorical_columns": metadata.categorical_columns,
                "ai_summary": metadata.ai_summary
            }
        }
    
    except Exception as e:
        # Log the full error
        logger.error(f"Error processing dataset: {str(e)}", exc_info=True)
        
        # Cleanup on error
        dataset_repo.delete(dataset.id)
        DatasetService.delete_file(file_path)
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error processing file: {str(e)}"
        )


@router.get("/project/{project_id}", response_model=List[DatasetResponse])
def get_project_datasets(
    project_id: int,
    db: Session = Depends(get_db)
):
    # Verify project exists
    project_repo = ProjectRepository(db)
    project = project_repo.get_by_id(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    dataset_repo = DatasetRepository(db)
    datasets = dataset_repo.get_all_by_project(project_id)
    return datasets


@router.get("/{dataset_id}", response_model=DatasetWithMetadata)
def get_dataset(
    dataset_id: int,
    db: Session = Depends(get_db)
):
    dataset_repo = DatasetRepository(db)
    dataset = dataset_repo.get_by_id(dataset_id)
    
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found"
        )
    
    # Serialize properly
    result = {
        "id": dataset.id,
        "name": dataset.name,
        "file_path": dataset.file_path,
        "file_type": dataset.file_type,
        "file_size": dataset.file_size,
        "project_id": dataset.project_id,
        "created_at": dataset.created_at,
        "metadata": None
    }
    
    # Add metadata if exists
    if dataset.dataset_metadata:
        result["metadata"] = {
            "id": dataset.dataset_metadata.id,
            "dataset_id": dataset.dataset_metadata.dataset_id,
            "rows": dataset.dataset_metadata.rows,
            "columns": dataset.dataset_metadata.columns,
            "column_info": dataset.dataset_metadata.column_info,
            "missing_values": dataset.dataset_metadata.missing_values,
            "duplicates": dataset.dataset_metadata.duplicates,
            "numeric_columns": dataset.dataset_metadata.numeric_columns,
            "categorical_columns": dataset.dataset_metadata.categorical_columns,
            "ai_summary": dataset.dataset_metadata.ai_summary
        }
    
    return result


@router.delete("/{dataset_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_dataset(
    dataset_id: int,
    db: Session = Depends(get_db)
):
    dataset_repo = DatasetRepository(db)
    dataset = dataset_repo.get_by_id(dataset_id)
    
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found"
        )
    
    # Delete file and record
    DatasetService.delete_file(dataset.file_path)
    dataset_repo.delete(dataset_id)
    
    return None
