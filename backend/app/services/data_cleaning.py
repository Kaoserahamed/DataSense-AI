"""
Data cleaning operations
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from sklearn.preprocessing import StandardScaler, MinMaxScaler, LabelEncoder
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class DataCleaning:
    """Data cleaning operations"""
    
    @staticmethod
    def remove_duplicates(df: pd.DataFrame, subset: Optional[List[str]] = None) -> Dict[str, Any]:
        """Remove duplicate rows"""
        original_rows = len(df)
        df_clean = df.drop_duplicates(subset=subset)
        removed = original_rows - len(df_clean)
        
        return {
            "cleaned_data": df_clean,
            "original_rows": int(original_rows),
            "cleaned_rows": int(len(df_clean)),
            "removed_duplicates": int(removed),
            "message": f"Removed {removed} duplicate rows"
        }
    
    @staticmethod
    def drop_missing_rows(df: pd.DataFrame, columns: Optional[List[str]] = None, 
                          threshold: Optional[float] = None) -> Dict[str, Any]:
        """Drop rows with missing values"""
        original_rows = len(df)
        
        if threshold is not None:
            # Drop rows where more than threshold% of values are missing
            min_count = int(((100 - threshold) / 100) * len(df.columns))
            df_clean = df.dropna(thresh=min_count)
        elif columns:
            df_clean = df.dropna(subset=columns)
        else:
            df_clean = df.dropna()
        
        removed = original_rows - len(df_clean)
        
        return {
            "cleaned_data": df_clean,
            "original_rows": original_rows,
            "cleaned_rows": len(df_clean),
            "removed_rows": removed,
            "message": f"Removed {removed} rows with missing values"
        }
    
    @staticmethod
    def drop_missing_columns(df: pd.DataFrame, threshold: float = 50.0) -> Dict[str, Any]:
        """Drop columns with more than threshold% missing values"""
        original_cols = len(df.columns)
        threshold_count = len(df) * (threshold / 100)
        
        df_clean = df.dropna(axis=1, thresh=len(df) - threshold_count)
        removed_cols = list(set(df.columns) - set(df_clean.columns))
        
        return {
            "cleaned_data": df_clean,
            "original_columns": original_cols,
            "cleaned_columns": len(df_clean.columns),
            "removed_columns": removed_cols,
            "message": f"Removed {len(removed_cols)} columns with >{threshold}% missing values"
        }

    
    @staticmethod
    def fill_missing_values(df: pd.DataFrame, strategy: str = "mean", 
                           columns: Optional[List[str]] = None, 
                           fill_value: Any = None) -> Dict[str, Any]:
        """Fill missing values with various strategies"""
        df_clean = df.copy()
        
        if columns is None:
            columns = df.columns.tolist()
        
        filled_info = {}
        
        for col in columns:
            if col not in df.columns:
                continue
            
            missing_before = df_clean[col].isnull().sum()
            if missing_before == 0:
                continue
            
            if strategy == "mean" and pd.api.types.is_numeric_dtype(df_clean[col]):
                df_clean[col].fillna(df_clean[col].mean(), inplace=True)
            elif strategy == "median" and pd.api.types.is_numeric_dtype(df_clean[col]):
                df_clean[col].fillna(df_clean[col].median(), inplace=True)
            elif strategy == "mode":
                if not df_clean[col].mode().empty:
                    df_clean[col].fillna(df_clean[col].mode()[0], inplace=True)
            elif strategy == "forward":
                df_clean[col].fillna(method='ffill', inplace=True)
            elif strategy == "backward":
                df_clean[col].fillna(method='bfill', inplace=True)
            elif strategy == "constant":
                df_clean[col].fillna(fill_value if fill_value is not None else 0, inplace=True)
            elif strategy == "interpolate" and pd.api.types.is_numeric_dtype(df_clean[col]):
                df_clean[col].interpolate(method='linear', inplace=True)
            
            missing_after = df_clean[col].isnull().sum()
            filled_info[col] = {
                "missing_before": int(missing_before),
                "missing_after": int(missing_after),
                "filled": int(missing_before - missing_after)
            }
        
        total_filled = sum(info["filled"] for info in filled_info.values())
        
        return {
            "cleaned_data": df_clean,
            "strategy": strategy,
            "filled_info": filled_info,
            "total_filled": total_filled,
            "message": f"Filled {total_filled} missing values using '{strategy}' strategy"
        }
    
    @staticmethod
    def standardize_columns(df: pd.DataFrame, columns: List[str]) -> Dict[str, Any]:
        """Standardize numeric columns (mean=0, std=1)"""
        df_clean = df.copy()
        scaler = StandardScaler()
        
        standardized = []
        for col in columns:
            if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
                df_clean[col] = scaler.fit_transform(df_clean[[col]])
                standardized.append(col)
        
        return {
            "cleaned_data": df_clean,
            "standardized_columns": standardized,
            "method": "StandardScaler (mean=0, std=1)",
            "message": f"Standardized {len(standardized)} columns"
        }
    
    @staticmethod
    def normalize_columns(df: pd.DataFrame, columns: List[str], 
                         method: str = "minmax") -> Dict[str, Any]:
        """Normalize numeric columns to [0, 1] range"""
        df_clean = df.copy()
        
        normalized = []
        for col in columns:
            if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
                if method == "minmax":
                    scaler = MinMaxScaler()
                    df_clean[col] = scaler.fit_transform(df_clean[[col]])
                elif method == "max":
                    max_val = df_clean[col].max()
                    if max_val != 0:
                        df_clean[col] = df_clean[col] / max_val
                
                normalized.append(col)
        
        return {
            "cleaned_data": df_clean,
            "normalized_columns": normalized,
            "method": method,
            "message": f"Normalized {len(normalized)} columns using '{method}' method"
        }

    
    @staticmethod
    def encode_categorical(df: pd.DataFrame, columns: List[str], 
                          method: str = "label") -> Dict[str, Any]:
        """Encode categorical columns"""
        df_clean = df.copy()
        
        encoding_info = {}
        
        for col in columns:
            if col not in df.columns:
                continue
            
            if method == "label":
                # Label encoding
                le = LabelEncoder()
                df_clean[col] = le.fit_transform(df_clean[col].astype(str))
                encoding_info[col] = {
                    "method": "label",
                    "classes": le.classes_.tolist()
                }
            
            elif method == "onehot":
                # One-hot encoding
                dummies = pd.get_dummies(df_clean[col], prefix=col)
                df_clean = pd.concat([df_clean.drop(col, axis=1), dummies], axis=1)
                encoding_info[col] = {
                    "method": "onehot",
                    "new_columns": dummies.columns.tolist()
                }
            
            elif method == "ordinal":
                # Ordinal encoding (preserves order)
                unique_vals = df_clean[col].unique()
                mapping = {val: idx for idx, val in enumerate(sorted(unique_vals))}
                df_clean[col] = df_clean[col].map(mapping)
                encoding_info[col] = {
                    "method": "ordinal",
                    "mapping": mapping
                }
        
        return {
            "cleaned_data": df_clean,
            "encoding_info": encoding_info,
            "message": f"Encoded {len(encoding_info)} categorical columns using '{method}' method"
        }
    
    @staticmethod
    def remove_outliers(df: pd.DataFrame, columns: List[str], 
                       method: str = "iqr", threshold: float = 1.5) -> Dict[str, Any]:
        """Remove outliers from numeric columns"""
        df_clean = df.copy()
        original_rows = len(df)
        
        outlier_info = {}
        
        for col in columns:
            if col not in df.columns or not pd.api.types.is_numeric_dtype(df[col]):
                continue
            
            if method == "iqr":
                Q1 = df_clean[col].quantile(0.25)
                Q3 = df_clean[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - threshold * IQR
                upper_bound = Q3 + threshold * IQR
                
                outliers = ((df_clean[col] < lower_bound) | (df_clean[col] > upper_bound)).sum()
                df_clean = df_clean[(df_clean[col] >= lower_bound) & (df_clean[col] <= upper_bound)]
                
            elif method == "zscore":
                z_scores = np.abs((df_clean[col] - df_clean[col].mean()) / df_clean[col].std())
                outliers = (z_scores > threshold).sum()
                df_clean = df_clean[z_scores <= threshold]
            
            elif method == "percentile":
                lower = df_clean[col].quantile(threshold / 100)
                upper = df_clean[col].quantile(1 - threshold / 100)
                outliers = ((df_clean[col] < lower) | (df_clean[col] > upper)).sum()
                df_clean = df_clean[(df_clean[col] >= lower) & (df_clean[col] <= upper)]
            
            outlier_info[col] = {
                "outliers_removed": int(outliers),
                "method": method,
                "threshold": threshold
            }
        
        removed = original_rows - len(df_clean)
        
        return {
            "cleaned_data": df_clean,
            "original_rows": original_rows,
            "cleaned_rows": len(df_clean),
            "removed_rows": removed,
            "outlier_info": outlier_info,
            "message": f"Removed {removed} rows with outliers using '{method}' method"
        }

    
    @staticmethod
    def parse_dates(df: pd.DataFrame, columns: List[str], 
                   date_format: Optional[str] = None) -> Dict[str, Any]:
        """Parse string columns to datetime"""
        df_clean = df.copy()
        
        parsed_info = {}
        
        for col in columns:
            if col not in df.columns:
                continue
            
            try:
                if date_format:
                    df_clean[col] = pd.to_datetime(df_clean[col], format=date_format, errors='coerce')
                else:
                    df_clean[col] = pd.to_datetime(df_clean[col], errors='coerce', infer_datetime_format=True)
                
                parsed_count = df_clean[col].notna().sum()
                failed_count = df_clean[col].isna().sum()
                
                parsed_info[col] = {
                    "parsed": int(parsed_count),
                    "failed": int(failed_count),
                    "success_rate": round((parsed_count / len(df)) * 100, 2)
                }
                
            except Exception as e:
                logger.error(f"Error parsing dates in column {col}: {str(e)}")
                parsed_info[col] = {
                    "error": str(e)
                }
        
        return {
            "cleaned_data": df_clean,
            "parsed_info": parsed_info,
            "message": f"Parsed {len(parsed_info)} date columns"
        }
    
    @staticmethod
    def extract_date_features(df: pd.DataFrame, columns: List[str]) -> Dict[str, Any]:
        """Extract features from datetime columns"""
        df_clean = df.copy()
        
        extracted_features = {}
        
        for col in columns:
            if col not in df.columns:
                continue
            
            # Ensure column is datetime
            if not pd.api.types.is_datetime64_any_dtype(df_clean[col]):
                try:
                    df_clean[col] = pd.to_datetime(df_clean[col])
                except:
                    continue
            
            # Extract features
            df_clean[f'{col}_year'] = df_clean[col].dt.year
            df_clean[f'{col}_month'] = df_clean[col].dt.month
            df_clean[f'{col}_day'] = df_clean[col].dt.day
            df_clean[f'{col}_dayofweek'] = df_clean[col].dt.dayofweek
            df_clean[f'{col}_quarter'] = df_clean[col].dt.quarter
            
            extracted_features[col] = [
                f'{col}_year',
                f'{col}_month',
                f'{col}_day',
                f'{col}_dayofweek',
                f'{col}_quarter'
            ]
        
        return {
            "cleaned_data": df_clean,
            "extracted_features": extracted_features,
            "message": f"Extracted date features from {len(extracted_features)} columns"
        }
    
    @staticmethod
    def trim_whitespace(df: pd.DataFrame) -> Dict[str, Any]:
        """Remove leading/trailing whitespace from string columns"""
        df_clean = df.copy()
        trimmed_columns = []
        
        for col in df.columns:
            if df_clean[col].dtype == 'object':
                df_clean[col] = df_clean[col].str.strip()
                trimmed_columns.append(col)
        
        return {
            "cleaned_data": df_clean,
            "trimmed_columns": trimmed_columns,
            "message": f"Trimmed whitespace from {len(trimmed_columns)} text columns"
        }
    
    @staticmethod
    def convert_data_types(df: pd.DataFrame, conversions: Dict[str, str]) -> Dict[str, Any]:
        """Convert column data types"""
        df_clean = df.copy()
        conversion_info = {}
        
        for col, dtype in conversions.items():
            if col not in df.columns:
                continue
            
            try:
                old_dtype = str(df_clean[col].dtype)
                
                if dtype == "int":
                    df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce').astype('Int64')
                elif dtype == "float":
                    df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
                elif dtype == "string":
                    df_clean[col] = df_clean[col].astype(str)
                elif dtype == "category":
                    df_clean[col] = df_clean[col].astype('category')
                elif dtype == "bool":
                    df_clean[col] = df_clean[col].astype(bool)
                elif dtype == "datetime":
                    df_clean[col] = pd.to_datetime(df_clean[col], errors='coerce')
                
                conversion_info[col] = {
                    "from": old_dtype,
                    "to": str(df_clean[col].dtype)
                }
                
            except Exception as e:
                conversion_info[col] = {
                    "error": str(e)
                }
        
        return {
            "cleaned_data": df_clean,
            "conversion_info": conversion_info,
            "message": f"Converted {len(conversion_info)} column types"
        }
