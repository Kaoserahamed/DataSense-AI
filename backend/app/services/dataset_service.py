import pandas as pd
import os
from typing import Dict, Any, Tuple
from pathlib import Path
from app.core.config import settings


class DatasetService:
    
    @staticmethod
    def save_file(file_content: bytes, filename: str, project_id: int) -> Tuple[str, int]:
        """Save uploaded file to disk"""
        upload_dir = Path(settings.UPLOAD_DIR) / str(project_id)
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = upload_dir / filename
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        file_size = len(file_content)
        return str(file_path), file_size
    
    @staticmethod
    def load_dataframe(file_path: str, file_type: str) -> pd.DataFrame:
        """Load dataset into pandas DataFrame"""
        if file_type == "csv":
            return pd.read_csv(file_path)
        elif file_type in ["xls", "xlsx"]:
            return pd.read_excel(file_path)
        elif file_type == "json":
            return pd.read_json(file_path)
        elif file_type == "parquet":
            return pd.read_parquet(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
    
    @staticmethod
    def analyze_dataset(df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze dataset and extract metadata"""
        column_info = {}
        missing_values = {}
        numeric_columns = []
        categorical_columns = []
        
        for col in df.columns:
            dtype = str(df[col].dtype)
            null_count = int(df[col].isnull().sum())
            unique_count = int(df[col].nunique())
            
            column_info[col] = {
                "dtype": dtype,
                "null_count": null_count,
                "unique_count": unique_count
            }
            
            if null_count > 0:
                missing_values[col] = {
                    "count": null_count,
                    "percentage": round((null_count / len(df)) * 100, 2)
                }
            
            if df[col].dtype in ['int64', 'float64']:
                numeric_columns.append(col)
                column_info[col]["min"] = float(df[col].min()) if not df[col].isnull().all() else None
                column_info[col]["max"] = float(df[col].max()) if not df[col].isnull().all() else None
                column_info[col]["mean"] = float(df[col].mean()) if not df[col].isnull().all() else None
            else:
                categorical_columns.append(col)
        
        duplicates = int(df.duplicated().sum())
        
        return {
            "rows": len(df),
            "columns": len(df.columns),
            "column_info": column_info,
            "missing_values": missing_values,
            "duplicates": duplicates,
            "numeric_columns": numeric_columns,
            "categorical_columns": categorical_columns
        }
    
    @staticmethod
    def delete_file(file_path: str) -> bool:
        """Delete dataset file from disk"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
            return True
        except Exception:
            return False
