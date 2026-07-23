"""
Data operations that work without requiring AI
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class DataOperations:
    """Basic data operations that don't require AI"""
    
    @staticmethod
    def get_basic_stats(df: pd.DataFrame) -> Dict[str, Any]:
        """Get basic statistical information"""
        import math

        def safe_float(v) -> Any:
            if v is None:
                return None
            try:
                f = float(v)
                return None if math.isnan(f) or math.isinf(f) else f
            except (TypeError, ValueError):
                return None

        stats = {}
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

        for col in numeric_cols:
            stats[col] = {
                "count": int(df[col].count()),
                "mean":   safe_float(df[col].mean()),
                "median": safe_float(df[col].median()),
                "std":    safe_float(df[col].std()),
                "min":    safe_float(df[col].min()),
                "max":    safe_float(df[col].max()),
                "q25":    safe_float(df[col].quantile(0.25)),
                "q75":    safe_float(df[col].quantile(0.75)),
            }

        return stats
    
    @staticmethod
    def get_value_counts(df: pd.DataFrame, column: str, limit: int = 10) -> Dict[str, int]:
        """Get value counts for a column"""
        if column not in df.columns:
            raise ValueError(f"Column '{column}' not found")
        
        value_counts = df[column].value_counts().head(limit)
        return {str(k): int(v) for k, v in value_counts.items()}
    
    @staticmethod
    def get_correlation_matrix(df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate correlation matrix for numeric columns"""
        numeric_df = df.select_dtypes(include=[np.number])
        
        if numeric_df.empty:
            return {"error": "No numeric columns found"}
        
        corr_matrix = numeric_df.corr()
        
        return {
            "columns": corr_matrix.columns.tolist(),
            "values": corr_matrix.values.tolist()
        }
    
    @staticmethod
    def filter_data(df: pd.DataFrame, filters: List[Dict[str, Any]]) -> pd.DataFrame:
        """Apply filters to dataframe"""
        filtered_df = df.copy()
        
        for f in filters:
            column = f.get("column")
            operator = f.get("operator")
            value = f.get("value")
            
            if column not in filtered_df.columns:
                continue
            
            if operator == "equals":
                filtered_df = filtered_df[filtered_df[column] == value]
            elif operator == "not_equals":
                filtered_df = filtered_df[filtered_df[column] != value]
            elif operator == "greater_than":
                filtered_df = filtered_df[filtered_df[column] > value]
            elif operator == "less_than":
                filtered_df = filtered_df[filtered_df[column] < value]
            elif operator == "contains":
                filtered_df = filtered_df[filtered_df[column].astype(str).str.contains(str(value), na=False)]
        
        return filtered_df
    
    @staticmethod
    def sort_data(df: pd.DataFrame, column: str, ascending: bool = True) -> pd.DataFrame:
        """Sort dataframe by column"""
        if column not in df.columns:
            raise ValueError(f"Column '{column}' not found")
        
        return df.sort_values(by=column, ascending=ascending)
    
    @staticmethod
    def get_unique_values(df: pd.DataFrame, column: str) -> List[Any]:
        """Get unique values for a column"""
        if column not in df.columns:
            raise ValueError(f"Column '{column}' not found")
        
        unique_vals = df[column].unique().tolist()
        # Limit to 100 values
        return unique_vals[:100]
    
    @staticmethod
    def get_missing_summary(df: pd.DataFrame) -> Dict[str, Any]:
        """Get summary of missing values"""
        missing = df.isnull().sum()
        missing_pct = (missing / len(df) * 100).round(2)
        
        summary = []
        for col in df.columns:
            if missing[col] > 0:
                summary.append({
                    "column": col,
                    "missing_count": int(missing[col]),
                    "missing_percentage": float(missing_pct[col])
                })
        
        return {
            "total_rows": len(df),
            "columns_with_missing": len(summary),
            "details": summary
        }
    
    @staticmethod
    def clean_remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
        """Remove duplicate rows"""
        return df.drop_duplicates()
    
    @staticmethod
    def clean_drop_missing(df: pd.DataFrame, columns: Optional[List[str]] = None) -> pd.DataFrame:
        """Drop rows with missing values"""
        if columns:
            return df.dropna(subset=columns)
        return df.dropna()
    
    @staticmethod
    def clean_fill_missing(df: pd.DataFrame, strategy: str = "mean", columns: Optional[List[str]] = None) -> pd.DataFrame:
        """Fill missing values with a strategy"""
        df_clean = df.copy()
        
        if columns is None:
            columns = df.columns.tolist()
        
        for col in columns:
            if col not in df.columns:
                continue
            
            if strategy == "mean" and df[col].dtype in [np.number]:
                df_clean[col].fillna(df[col].mean(), inplace=True)
            elif strategy == "median" and df[col].dtype in [np.number]:
                df_clean[col].fillna(df[col].median(), inplace=True)
            elif strategy == "mode":
                if not df[col].mode().empty:
                    df_clean[col].fillna(df[col].mode()[0], inplace=True)
            elif strategy == "forward":
                df_clean[col].fillna(method='ffill', inplace=True)
            elif strategy == "backward":
                df_clean[col].fillna(method='bfill', inplace=True)
            elif strategy == "zero":
                df_clean[col].fillna(0, inplace=True)
        
        return df_clean
    
    @staticmethod
    def get_data_preview(df: pd.DataFrame, rows: int = 10) -> Dict[str, Any]:
        """Get preview of data with safe serialization"""
        import math

        def safe_value(v: Any) -> Any:
            """Convert a single value to a JSON-safe Python primitive."""
            if v is None:
                return None
            # numpy scalar types
            if isinstance(v, (np.integer,)):
                return int(v)
            if isinstance(v, (np.floating,)):
                f = float(v)
                return None if math.isnan(f) or math.isinf(f) else f
            if isinstance(v, np.bool_):
                return bool(v)
            # pandas Timestamp / datetime
            if isinstance(v, pd.Timestamp):
                return v.isoformat()
            # plain float NaN / inf
            if isinstance(v, float):
                return None if math.isnan(v) or math.isinf(v) else v
            # numpy arrays / other ndarray-like
            if isinstance(v, np.ndarray):
                return v.tolist()
            return v

        preview_df = df.head(rows)
        records = []
        for _, row in preview_df.iterrows():
            records.append({col: safe_value(row[col]) for col in df.columns})

        return {
            "columns": df.columns.tolist(),
            "data": records,
            "total_rows": len(df)
        }
