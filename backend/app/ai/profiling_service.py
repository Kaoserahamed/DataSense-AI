import pandas as pd
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class ProfilingService:
    """Data profiling service with optional AI enhancement"""
    
    @staticmethod
    def generate_dataset_summary(df: pd.DataFrame, metadata: Dict[str, Any]) -> str:
        """Generate dataset summary with AI if available, otherwise use rule-based approach"""
        
        # Try AI-powered summary first
        try:
            from app.ai.llm_provider import llm_provider
            
            if llm_provider.is_available():
                return ProfilingService._generate_ai_summary(df, metadata)
            else:
                logger.info("AI provider not available, using rule-based summary")
        except Exception as e:
            logger.warning(f"AI summary generation failed: {str(e)}, falling back to rule-based")
        
        # Fallback to rule-based summary
        return ProfilingService._generate_rule_based_summary(df, metadata)
    
    @staticmethod
    def _generate_ai_summary(df: pd.DataFrame, metadata: Dict[str, Any]) -> str:
        """Generate AI-powered summary"""
        from app.ai.llm_provider import llm_provider
        
        description = f"""
Dataset Overview:
- Total Rows: {metadata['rows']}
- Total Columns: {metadata['columns']}
- Duplicate Rows: {metadata['duplicates']}

Numeric Columns ({len(metadata['numeric_columns'])}):
{', '.join(metadata['numeric_columns'][:10])}

Categorical Columns ({len(metadata['categorical_columns'])}):
{', '.join(metadata['categorical_columns'][:10])}

Missing Values:
{ProfilingService._format_missing_values(metadata['missing_values'])}

Sample Data (first 3 rows):
{df.head(3).to_string()}
"""
        
        prompt = f"""Analyze this dataset and provide:

1. A brief summary of what this dataset appears to contain
2. Key insights about the data quality
3. Suggested analyses that would be valuable
4. Recommended chart types for visualization
5. Potential machine learning tasks (classification, regression, clustering, time series)

{description}

Provide a clear, structured response."""
        
        summary = llm_provider.generate_completion(
            prompt=prompt,
            system_prompt="You are a data analysis expert. Provide concise, actionable insights."
        )
        
        return summary
    
    @staticmethod
    def _generate_rule_based_summary(df: pd.DataFrame, metadata: Dict[str, Any]) -> str:
        """Generate rule-based summary without AI"""
        
        summary_parts = []
        
        # Dataset Overview
        summary_parts.append("=== DATASET SUMMARY ===\n")
        summary_parts.append(f"Total Records: {metadata['rows']:,}")
        summary_parts.append(f"Total Columns: {metadata['columns']}")
        summary_parts.append(f"Duplicate Rows: {metadata['duplicates']}\n")
        
        # Column Analysis
        summary_parts.append("=== COLUMN ANALYSIS ===")
        summary_parts.append(f"Numeric Columns ({len(metadata['numeric_columns'])}): {', '.join(metadata['numeric_columns'][:10])}")
        if len(metadata['numeric_columns']) > 10:
            summary_parts.append(f"  ... and {len(metadata['numeric_columns']) - 10} more")
        
        summary_parts.append(f"\nCategorical Columns ({len(metadata['categorical_columns'])}): {', '.join(metadata['categorical_columns'][:10])}")
        if len(metadata['categorical_columns']) > 10:
            summary_parts.append(f"  ... and {len(metadata['categorical_columns']) - 10} more")
        
        # Data Quality
        summary_parts.append("\n=== DATA QUALITY ===")
        if metadata['missing_values']:
            summary_parts.append("Missing Values Detected:")
            summary_parts.append(ProfilingService._format_missing_values(metadata['missing_values']))
        else:
            summary_parts.append("✓ No missing values detected")
        
        if metadata['duplicates'] > 0:
            summary_parts.append(f"\n⚠ {metadata['duplicates']} duplicate rows found")
        else:
            summary_parts.append("\n✓ No duplicate rows")
        
        # Suggestions
        summary_parts.append("\n=== SUGGESTED OPERATIONS ===")
        
        suggestions = []
        if metadata['missing_values']:
            suggestions.append("• Data Cleaning: Handle missing values")
        if metadata['duplicates'] > 0:
            suggestions.append("• Data Cleaning: Remove duplicate rows")
        if len(metadata['numeric_columns']) >= 2:
            suggestions.append("• Visualization: Create scatter plots, correlation matrix")
            suggestions.append("• Analysis: Perform statistical analysis and correlation")
        if len(metadata['categorical_columns']) > 0:
            suggestions.append("• Visualization: Create bar charts, pie charts")
        
        if not suggestions:
            suggestions.append("• Dataset appears clean and ready for analysis")
        
        summary_parts.extend(suggestions)
        
        # ML Recommendations
        if len(metadata['numeric_columns']) > 0 or len(metadata['categorical_columns']) > 0:
            summary_parts.append("\n=== POTENTIAL ANALYSIS ===")
            if len(metadata['numeric_columns']) >= 2:
                summary_parts.append("• Regression Analysis (if target variable exists)")
                summary_parts.append("• Clustering Analysis")
            if len(metadata['categorical_columns']) > 0:
                summary_parts.append("• Classification (if categorical target exists)")
        
        summary_parts.append("\n[Note: AI-powered insights unavailable. Configure OpenAI API key for enhanced analysis.]")
        
        return "\n".join(summary_parts)
    
    @staticmethod
    def _format_missing_values(missing_values: Dict[str, Any]) -> str:
        if not missing_values:
            return "No missing values detected"
        
        lines = []
        for col, info in list(missing_values.items())[:5]:
            lines.append(f"  - {col}: {info['count']} ({info['percentage']}%)")
        
        if len(missing_values) > 5:
            lines.append(f"  ... and {len(missing_values) - 5} more columns")
        
        return "\n".join(lines)
