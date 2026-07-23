from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import logging

from app.database.connection import get_db
from app.repositories.dataset_repository import DatasetRepository
from app.services.dataset_service import DatasetService
from app.services.visualization_service import VisualizationService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/visualization", tags=["Visualization"])


class BarChartRequest(BaseModel):
    dataset_id: int
    x_column: str
    y_column: Optional[str] = None
    title: Optional[str] = "Bar Chart"
    horizontal: bool = False


class LineChartRequest(BaseModel):
    dataset_id: int
    x_column: str
    y_columns: List[str]
    title: Optional[str] = "Line Chart"


class PieChartRequest(BaseModel):
    dataset_id: int
    column: str
    title: Optional[str] = "Pie Chart"
    top_n: int = 10


class ScatterPlotRequest(BaseModel):
    dataset_id: int
    x_column: str
    y_column: str
    color_column: Optional[str] = None
    title: Optional[str] = "Scatter Plot"


class HistogramRequest(BaseModel):
    dataset_id: int
    column: str
    bins: int = 30
    title: Optional[str] = "Histogram"


class BoxPlotRequest(BaseModel):
    dataset_id: int
    columns: List[str]
    title: Optional[str] = "Box Plot"


class HeatmapRequest(BaseModel):
    dataset_id: int
    columns: Optional[List[str]] = None
    title: Optional[str] = "Correlation Heatmap"


class AutoChartRequest(BaseModel):
    dataset_id: int
    columns: Optional[List[str]] = None


@router.post("/bar-chart")
def create_bar_chart(request: BarChartRequest, db: Session = Depends(get_db)):
    """Generate a bar chart"""
    try:
        dataset_repo = DatasetRepository(db)
        dataset = dataset_repo.get_by_id(request.dataset_id)
        
        if not dataset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dataset not found"
            )
        
        df = DatasetService.load_dataframe(dataset.file_path, dataset.file_type)
        
        result = VisualizationService.generate_bar_chart(
            df,
            request.x_column,
            request.y_column,
            request.title,
            request.horizontal
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error creating bar chart: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/line-chart")
def create_line_chart(request: LineChartRequest, db: Session = Depends(get_db)):
    """Generate a line chart"""
    try:
        dataset_repo = DatasetRepository(db)
        dataset = dataset_repo.get_by_id(request.dataset_id)
        
        if not dataset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dataset not found"
            )
        
        df = DatasetService.load_dataframe(dataset.file_path, dataset.file_type)
        
        result = VisualizationService.generate_line_chart(
            df,
            request.x_column,
            request.y_columns,
            request.title
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error creating line chart: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/pie-chart")
def create_pie_chart(request: PieChartRequest, db: Session = Depends(get_db)):
    """Generate a pie chart"""
    try:
        dataset_repo = DatasetRepository(db)
        dataset = dataset_repo.get_by_id(request.dataset_id)
        
        if not dataset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dataset not found"
            )
        
        df = DatasetService.load_dataframe(dataset.file_path, dataset.file_type)
        
        result = VisualizationService.generate_pie_chart(
            df,
            request.column,
            request.title,
            request.top_n
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error creating pie chart: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/scatter-plot")
def create_scatter_plot(request: ScatterPlotRequest, db: Session = Depends(get_db)):
    """Generate a scatter plot"""
    try:
        dataset_repo = DatasetRepository(db)
        dataset = dataset_repo.get_by_id(request.dataset_id)
        
        if not dataset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dataset not found"
            )
        
        df = DatasetService.load_dataframe(dataset.file_path, dataset.file_type)
        
        result = VisualizationService.generate_scatter_plot(
            df,
            request.x_column,
            request.y_column,
            request.color_column,
            request.title
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error creating scatter plot: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/histogram")
def create_histogram(request: HistogramRequest, db: Session = Depends(get_db)):
    """Generate a histogram"""
    try:
        dataset_repo = DatasetRepository(db)
        dataset = dataset_repo.get_by_id(request.dataset_id)
        
        if not dataset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dataset not found"
            )
        
        df = DatasetService.load_dataframe(dataset.file_path, dataset.file_type)
        
        result = VisualizationService.generate_histogram(
            df,
            request.column,
            request.bins,
            request.title
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error creating histogram: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/box-plot")
def create_box_plot(request: BoxPlotRequest, db: Session = Depends(get_db)):
    """Generate a box plot"""
    try:
        dataset_repo = DatasetRepository(db)
        dataset = dataset_repo.get_by_id(request.dataset_id)
        
        if not dataset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dataset not found"
            )
        
        df = DatasetService.load_dataframe(dataset.file_path, dataset.file_type)
        
        result = VisualizationService.generate_box_plot(
            df,
            request.columns,
            request.title
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error creating box plot: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/heatmap")
def create_heatmap(request: HeatmapRequest, db: Session = Depends(get_db)):
    """Generate a correlation heatmap"""
    try:
        dataset_repo = DatasetRepository(db)
        dataset = dataset_repo.get_by_id(request.dataset_id)
        
        if not dataset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dataset not found"
            )
        
        df = DatasetService.load_dataframe(dataset.file_path, dataset.file_type)
        
        result = VisualizationService.generate_heatmap(
            df,
            request.columns,
            request.title
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error creating heatmap: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/auto-chart")
def create_auto_chart(request: AutoChartRequest, db: Session = Depends(get_db)):
    """Automatically generate the most appropriate chart"""
    try:
        dataset_repo = DatasetRepository(db)
        dataset = dataset_repo.get_by_id(request.dataset_id)
        
        if not dataset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dataset not found"
            )
        
        df = DatasetService.load_dataframe(dataset.file_path, dataset.file_type)
        
        result = VisualizationService.generate_auto_chart(df, request.columns)
        
        return result
        
    except Exception as e:
        logger.error(f"Error creating auto chart: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
