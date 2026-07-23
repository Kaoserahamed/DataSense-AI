from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from app.database.connection import get_db
from app.repositories.dataset_repository import DatasetRepository
from app.services.dataset_service import DatasetService
from app.services.data_operations import DataOperations

router = APIRouter(prefix="/analysis", tags=["Analysis"])


class FilterRequest(BaseModel):
    column: str
    operator: str  # equals, not_equals, greater_than, less_than, contains
    value: Any


class DataRequest(BaseModel):
    dataset_id: int
    filters: Optional[List[FilterRequest]] = None
    sort_column: Optional[str] = None
    sort_ascending: bool = True


@router.post("/stats")
def get_statistics(request: DataRequest, db: Session = Depends(get_db)):
    """Get statistical analysis of dataset"""
    dataset_repo = DatasetRepository(db)
    dataset = dataset_repo.get_by_id(request.dataset_id)
    
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found"
        )
    
    df = DatasetService.load_dataframe(dataset.file_path, dataset.file_type)
    
    # Apply filters if provided
    if request.filters:
        filter_dicts = [f.model_dump() for f in request.filters]
        df = DataOperations.filter_data(df, filter_dicts)
    
    stats = DataOperations.get_basic_stats(df)
    
    return {
        "dataset_id": request.dataset_id,
        "filtered_rows": len(df),
        "statistics": stats
    }


@router.get("/correlation/{dataset_id}")
def get_correlation(dataset_id: int, db: Session = Depends(get_db)):
    """Get correlation matrix"""
    dataset_repo = DatasetRepository(db)
    dataset = dataset_repo.get_by_id(dataset_id)
    
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found"
        )
    
    df = DatasetService.load_dataframe(dataset.file_path, dataset.file_type)
    correlation = DataOperations.get_correlation_matrix(df)
    
    return {
        "dataset_id": dataset_id,
        "correlation": correlation
    }


@router.get("/value-counts/{dataset_id}/{column}")
def get_value_counts(
    dataset_id: int,
    column: str,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get value counts for a column"""
    dataset_repo = DatasetRepository(db)
    dataset = dataset_repo.get_by_id(dataset_id)
    
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found"
        )
    
    try:
        df = DatasetService.load_dataframe(dataset.file_path, dataset.file_type)
        value_counts = DataOperations.get_value_counts(df, column, limit)
        
        return {
            "dataset_id": dataset_id,
            "column": column,
            "value_counts": value_counts
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/unique/{dataset_id}/{column}")
def get_unique_values(
    dataset_id: int,
    column: str,
    db: Session = Depends(get_db)
):
    """Get unique values for a column"""
    dataset_repo = DatasetRepository(db)
    dataset = dataset_repo.get_by_id(dataset_id)
    
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found"
        )
    
    try:
        df = DatasetService.load_dataframe(dataset.file_path, dataset.file_type)
        unique_values = DataOperations.get_unique_values(df, column)
        
        return {
            "dataset_id": dataset_id,
            "column": column,
            "unique_values": unique_values,
            "count": len(unique_values)
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/missing/{dataset_id}")
def get_missing_summary(dataset_id: int, db: Session = Depends(get_db)):
    """Get summary of missing values"""
    dataset_repo = DatasetRepository(db)
    dataset = dataset_repo.get_by_id(dataset_id)
    
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found"
        )
    
    df = DatasetService.load_dataframe(dataset.file_path, dataset.file_type)
    missing_summary = DataOperations.get_missing_summary(df)
    
    return {
        "dataset_id": dataset_id,
        "missing_summary": missing_summary
    }


@router.post("/preview")
def get_data_preview(request: DataRequest, rows: int = 10, db: Session = Depends(get_db)):
    """Get preview of data with optional filters and sorting"""
    dataset_repo = DatasetRepository(db)
    dataset = dataset_repo.get_by_id(request.dataset_id)
    
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found"
        )
    
    df = DatasetService.load_dataframe(dataset.file_path, dataset.file_type)
    
    # Apply filters
    if request.filters:
        filter_dicts = [f.model_dump() for f in request.filters]
        df = DataOperations.filter_data(df, filter_dicts)
    
    # Apply sorting
    if request.sort_column:
        try:
            df = DataOperations.sort_data(df, request.sort_column, request.sort_ascending)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
    
    preview = DataOperations.get_data_preview(df, rows)
    
    return preview
