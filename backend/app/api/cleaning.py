from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
import logging
import numpy as np
import json
from app.database.connection import get_db
from app.repositories.dataset_repository import DatasetRepository
from app.services.dataset_service import DatasetService
from app.services.data_cleaning import DataCleaning

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/cleaning", tags=["Data Cleaning"])


def convert_to_serializable(obj):
    """Convert numpy types to Python types"""
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {key: convert_to_serializable(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_serializable(item) for item in obj]
    elif isinstance(obj, (np.bool_, bool)):
        return bool(obj)
    elif obj is None or isinstance(obj, str):
        return obj
    return str(obj)


class RemoveDuplicatesRequest(BaseModel):
    dataset_id: int
    subset: Optional[List[str]] = None
    save_as_new: bool = False
    new_name: Optional[str] = None


class FillMissingRequest(BaseModel):
    dataset_id: int
    strategy: str  # mean, median, mode, forward, backward, constant, interpolate
    columns: Optional[List[str]] = None
    fill_value: Any = None
    save_as_new: bool = False
    new_name: Optional[str] = None


class DropMissingRequest(BaseModel):
    dataset_id: int
    axis: str = "rows"  # rows or columns
    columns: Optional[List[str]] = None
    threshold: Optional[float] = None
    save_as_new: bool = False
    new_name: Optional[str] = None


class StandardizeRequest(BaseModel):
    dataset_id: int
    columns: List[str]
    save_as_new: bool = False
    new_name: Optional[str] = None


class NormalizeRequest(BaseModel):
    dataset_id: int
    columns: List[str]
    method: str = "minmax"  # minmax or max
    save_as_new: bool = False
    new_name: Optional[str] = None


class EncodeRequest(BaseModel):
    dataset_id: int
    columns: List[str]
    method: str = "label"  # label, onehot, ordinal
    save_as_new: bool = False
    new_name: Optional[str] = None


class RemoveOutliersRequest(BaseModel):
    dataset_id: int
    columns: List[str]
    method: str = "iqr"  # iqr, zscore, percentile
    threshold: float = 1.5
    save_as_new: bool = False
    new_name: Optional[str] = None


class ParseDatesRequest(BaseModel):
    dataset_id: int
    columns: List[str]
    date_format: Optional[str] = None
    extract_features: bool = False
    save_as_new: bool = False
    new_name: Optional[str] = None



@router.post("/remove-duplicates")
def remove_duplicates(request: RemoveDuplicatesRequest, db: Session = Depends(get_db)):
    """Remove duplicate rows"""
    try:
        dataset_repo = DatasetRepository(db)
        dataset = dataset_repo.get_by_id(request.dataset_id)
        
        if not dataset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dataset not found"
            )
        
        # Load data
        df = DatasetService.load_dataframe(dataset.file_path, dataset.file_type)
        
        # Clean data
        result = DataCleaning.remove_duplicates(df, request.subset)
        
        # Save if requested
        if request.save_as_new and request.new_name:
            new_path, new_size = _save_cleaned_dataset(
                result["cleaned_data"],
                request.new_name,
                dataset.project_id,
                dataset.file_type
            )
            
            new_dataset = dataset_repo.create(
                name=request.new_name,
                file_path=new_path,
                file_type=dataset.file_type,
                file_size=new_size,
                project_id=dataset.project_id
            )
            
            # Analyze new dataset
            metadata_dict = DatasetService.analyze_dataset(result["cleaned_data"])
            dataset_repo.create_metadata(new_dataset.id, metadata_dict)
            
            return {
                **result,
                "new_dataset_id": new_dataset.id,
                "saved": True
            }
        
        return {
            "original_rows": int(result["original_rows"]),
            "cleaned_rows": int(result["cleaned_rows"]),
            "removed_duplicates": int(result["removed_duplicates"]),
            "message": result["message"],
            "saved": False,
            "preview": convert_to_serializable(result["cleaned_data"].head(5).to_dict(orient="records"))
        }
        
    except Exception as e:
        logger.error(f"Error removing duplicates: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/fill-missing")
def fill_missing(request: FillMissingRequest, db: Session = Depends(get_db)):
    """Fill missing values"""
    try:
        dataset_repo = DatasetRepository(db)
        dataset = dataset_repo.get_by_id(request.dataset_id)
        
        if not dataset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dataset not found"
            )
        
        df = DatasetService.load_dataframe(dataset.file_path, dataset.file_type)
        result = DataCleaning.fill_missing_values(
            df, 
            request.strategy, 
            request.columns, 
            request.fill_value
        )
        
        if request.save_as_new and request.new_name:
            new_path, new_size = _save_cleaned_dataset(
                result["cleaned_data"],
                request.new_name,
                dataset.project_id,
                dataset.file_type
            )
            
            new_dataset = dataset_repo.create(
                name=request.new_name,
                file_path=new_path,
                file_type=dataset.file_type,
                file_size=new_size,
                project_id=dataset.project_id
            )
            
            metadata_dict = DatasetService.analyze_dataset(result["cleaned_data"])
            dataset_repo.create_metadata(new_dataset.id, metadata_dict)
            
            return convert_to_serializable({
                **{k: v for k, v in result.items() if k != "cleaned_data"},
                "new_dataset_id": new_dataset.id,
                "saved": True
            })
        
        return convert_to_serializable({
            **{k: v for k, v in result.items() if k != "cleaned_data"},
            "saved": False,
            "preview": result["cleaned_data"].head(5).to_dict(orient="records")
        })
        
    except Exception as e:
        logger.error(f"Error filling missing values: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )



@router.post("/drop-missing")
def drop_missing(request: DropMissingRequest, db: Session = Depends(get_db)):
    """Drop rows or columns with missing values"""
    try:
        dataset_repo = DatasetRepository(db)
        dataset = dataset_repo.get_by_id(request.dataset_id)
        
        if not dataset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dataset not found"
            )
        
        df = DatasetService.load_dataframe(dataset.file_path, dataset.file_type)
        
        if request.axis == "rows":
            result = DataCleaning.drop_missing_rows(df, request.columns, request.threshold)
        else:
            result = DataCleaning.drop_missing_columns(df, request.threshold or 50.0)
        
        if request.save_as_new and request.new_name:
            new_path, new_size = _save_cleaned_dataset(
                result["cleaned_data"],
                request.new_name,
                dataset.project_id,
                dataset.file_type
            )
            
            new_dataset = dataset_repo.create(
                name=request.new_name,
                file_path=new_path,
                file_type=dataset.file_type,
                file_size=new_size,
                project_id=dataset.project_id
            )
            
            metadata_dict = DatasetService.analyze_dataset(result["cleaned_data"])
            dataset_repo.create_metadata(new_dataset.id, metadata_dict)
            
            return convert_to_serializable({
                **{k: v for k, v in result.items() if k != "cleaned_data"},
                "new_dataset_id": new_dataset.id,
                "saved": True
            })
        
        return convert_to_serializable({
            **{k: v for k, v in result.items() if k != "cleaned_data"},
            "saved": False
        })
        
    except Exception as e:
        logger.error(f"Error dropping missing values: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/standardize")
def standardize(request: StandardizeRequest, db: Session = Depends(get_db)):
    """Standardize numeric columns"""
    try:
        dataset_repo = DatasetRepository(db)
        dataset = dataset_repo.get_by_id(request.dataset_id)
        
        if not dataset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dataset not found"
            )
        
        df = DatasetService.load_dataframe(dataset.file_path, dataset.file_type)
        result = DataCleaning.standardize_columns(df, request.columns)
        
        if request.save_as_new and request.new_name:
            new_path, new_size = _save_cleaned_dataset(
                result["cleaned_data"],
                request.new_name,
                dataset.project_id,
                dataset.file_type
            )
            
            new_dataset = dataset_repo.create(
                name=request.new_name,
                file_path=new_path,
                file_type=dataset.file_type,
                file_size=new_size,
                project_id=dataset.project_id
            )
            
            metadata_dict = DatasetService.analyze_dataset(result["cleaned_data"])
            dataset_repo.create_metadata(new_dataset.id, metadata_dict)
            
            return convert_to_serializable({
                **{k: v for k, v in result.items() if k != "cleaned_data"},
                "new_dataset_id": new_dataset.id,
                "saved": True
            })
        
        return convert_to_serializable({
            **{k: v for k, v in result.items() if k != "cleaned_data"},
            "saved": False,
            "preview": result["cleaned_data"][request.columns].head(5).to_dict(orient="records")
        })
        
    except Exception as e:
        logger.error(f"Error standardizing: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )



@router.post("/normalize")
def normalize(request: NormalizeRequest, db: Session = Depends(get_db)):
    """Normalize numeric columns"""
    try:
        dataset_repo = DatasetRepository(db)
        dataset = dataset_repo.get_by_id(request.dataset_id)
        
        if not dataset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dataset not found"
            )
        
        df = DatasetService.load_dataframe(dataset.file_path, dataset.file_type)
        result = DataCleaning.normalize_columns(df, request.columns, request.method)
        
        if request.save_as_new and request.new_name:
            new_path, new_size = _save_cleaned_dataset(
                result["cleaned_data"],
                request.new_name,
                dataset.project_id,
                dataset.file_type
            )
            
            new_dataset = dataset_repo.create(
                name=request.new_name,
                file_path=new_path,
                file_type=dataset.file_type,
                file_size=new_size,
                project_id=dataset.project_id
            )
            
            metadata_dict = DatasetService.analyze_dataset(result["cleaned_data"])
            dataset_repo.create_metadata(new_dataset.id, metadata_dict)
            
            return convert_to_serializable({
                **{k: v for k, v in result.items() if k != "cleaned_data"},
                "new_dataset_id": new_dataset.id,
                "saved": True
            })
        
        return convert_to_serializable({
            **{k: v for k, v in result.items() if k != "cleaned_data"},
            "saved": False,
            "preview": result["cleaned_data"][request.columns].head(5).to_dict(orient="records")
        })
        
    except Exception as e:
        logger.error(f"Error normalizing: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/encode-categorical")
def encode_categorical(request: EncodeRequest, db: Session = Depends(get_db)):
    """Encode categorical columns"""
    try:
        dataset_repo = DatasetRepository(db)
        dataset = dataset_repo.get_by_id(request.dataset_id)
        
        if not dataset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dataset not found"
            )
        
        df = DatasetService.load_dataframe(dataset.file_path, dataset.file_type)
        result = DataCleaning.encode_categorical(df, request.columns, request.method)
        
        if request.save_as_new and request.new_name:
            new_path, new_size = _save_cleaned_dataset(
                result["cleaned_data"],
                request.new_name,
                dataset.project_id,
                dataset.file_type
            )
            
            new_dataset = dataset_repo.create(
                name=request.new_name,
                file_path=new_path,
                file_type=dataset.file_type,
                file_size=new_size,
                project_id=dataset.project_id
            )
            
            metadata_dict = DatasetService.analyze_dataset(result["cleaned_data"])
            dataset_repo.create_metadata(new_dataset.id, metadata_dict)
            
            return convert_to_serializable({
                **{k: v for k, v in result.items() if k != "cleaned_data"},
                "new_dataset_id": new_dataset.id,
                "saved": True
            })
        
        return convert_to_serializable({
            **{k: v for k, v in result.items() if k != "cleaned_data"},
            "saved": False,
            "preview": result["cleaned_data"].head(5).to_dict(orient="records")
        })
        
    except Exception as e:
        logger.error(f"Error encoding categorical: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )



@router.post("/remove-outliers")
def remove_outliers(request: RemoveOutliersRequest, db: Session = Depends(get_db)):
    """Remove outliers from numeric columns"""
    try:
        dataset_repo = DatasetRepository(db)
        dataset = dataset_repo.get_by_id(request.dataset_id)
        
        if not dataset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dataset not found"
            )
        
        df = DatasetService.load_dataframe(dataset.file_path, dataset.file_type)
        result = DataCleaning.remove_outliers(df, request.columns, request.method, request.threshold)
        
        if request.save_as_new and request.new_name:
            new_path, new_size = _save_cleaned_dataset(
                result["cleaned_data"],
                request.new_name,
                dataset.project_id,
                dataset.file_type
            )
            
            new_dataset = dataset_repo.create(
                name=request.new_name,
                file_path=new_path,
                file_type=dataset.file_type,
                file_size=new_size,
                project_id=dataset.project_id
            )
            
            metadata_dict = DatasetService.analyze_dataset(result["cleaned_data"])
            dataset_repo.create_metadata(new_dataset.id, metadata_dict)
            
            return convert_to_serializable({
                **{k: v for k, v in result.items() if k != "cleaned_data"},
                "new_dataset_id": new_dataset.id,
                "saved": True
            })
        
        return convert_to_serializable({
            **{k: v for k, v in result.items() if k != "cleaned_data"},
            "saved": False
        })
        
    except Exception as e:
        logger.error(f"Error removing outliers: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/parse-dates")
def parse_dates(request: ParseDatesRequest, db: Session = Depends(get_db)):
    """Parse date columns"""
    try:
        dataset_repo = DatasetRepository(db)
        dataset = dataset_repo.get_by_id(request.dataset_id)
        
        if not dataset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dataset not found"
            )
        
        df = DatasetService.load_dataframe(dataset.file_path, dataset.file_type)
        result = DataCleaning.parse_dates(df, request.columns, request.date_format)
        
        # Extract features if requested
        if request.extract_features:
            feature_result = DataCleaning.extract_date_features(result["cleaned_data"], request.columns)
            result["cleaned_data"] = feature_result["cleaned_data"]
            result["extracted_features"] = feature_result["extracted_features"]
        
        if request.save_as_new and request.new_name:
            new_path, new_size = _save_cleaned_dataset(
                result["cleaned_data"],
                request.new_name,
                dataset.project_id,
                dataset.file_type
            )
            
            new_dataset = dataset_repo.create(
                name=request.new_name,
                file_path=new_path,
                file_type=dataset.file_type,
                file_size=new_size,
                project_id=dataset.project_id
            )
            
            metadata_dict = DatasetService.analyze_dataset(result["cleaned_data"])
            dataset_repo.create_metadata(new_dataset.id, metadata_dict)
            
            return convert_to_serializable({
                **{k: v for k, v in result.items() if k != "cleaned_data"},
                "new_dataset_id": new_dataset.id,
                "saved": True
            })
        
        return convert_to_serializable({
            **{k: v for k, v in result.items() if k != "cleaned_data"},
            "saved": False,
            "preview": result["cleaned_data"].head(5).to_dict(orient="records")
        })
        
    except Exception as e:
        logger.error(f"Error parsing dates: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


def _save_cleaned_dataset(df, name, project_id, file_type):
    """Helper function to save cleaned dataset"""
    from pathlib import Path
    from app.core.config import settings
    
    upload_dir = Path(settings.UPLOAD_DIR) / str(project_id)
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = upload_dir / name
    
    if file_type == "csv":
        df.to_csv(file_path, index=False)
    elif file_type in ["xlsx", "xls"]:
        df.to_excel(file_path, index=False)
    elif file_type == "json":
        df.to_json(file_path, orient="records")
    elif file_type == "parquet":
        df.to_parquet(file_path, index=False)
    
    file_size = file_path.stat().st_size
    return str(file_path), file_size
