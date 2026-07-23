"""
Visualization service - Generate various chart types using Plotly
"""
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, Any, List, Optional
import json
import logging

logger = logging.getLogger(__name__)


class VisualizationService:
    """Service for generating various types of visualizations"""
    
    @staticmethod
    def generate_bar_chart(df: pd.DataFrame, x_column: str, y_column: Optional[str] = None,
                          title: str = "Bar Chart", horizontal: bool = False) -> Dict[str, Any]:
        """Generate a bar chart"""
        try:
            if y_column:
                # Grouped data
                data = df[[x_column, y_column]].dropna()
                x_data = data[x_column].tolist()
                y_data = data[y_column].tolist()
            else:
                # Value counts
                value_counts = df[x_column].value_counts()
                x_data = value_counts.index.tolist()
                y_data = value_counts.values.tolist()
            
            if horizontal:
                fig = go.Figure(data=[go.Bar(x=y_data, y=x_data, orientation='h')])
                fig.update_layout(xaxis_title=y_column or "Count", yaxis_title=x_column)
            else:
                fig = go.Figure(data=[go.Bar(x=x_data, y=y_data)])
                fig.update_layout(xaxis_title=x_column, yaxis_title=y_column or "Count")
            
            fig.update_layout(title=title, template="plotly_white")
            
            return {
                "type": "bar",
                "config": json.loads(fig.to_json()),
                "html": fig.to_html(include_plotlyjs='cdn')
            }
            
        except Exception as e:
            logger.error(f"Error generating bar chart: {str(e)}")
            raise
    
    @staticmethod
    def generate_line_chart(df: pd.DataFrame, x_column: str, y_columns: List[str],
                           title: str = "Line Chart") -> Dict[str, Any]:
        """Generate a line chart"""
        try:
            fig = go.Figure()
            
            for y_col in y_columns:
                data = df[[x_column, y_col]].dropna()
                fig.add_trace(go.Scatter(
                    x=data[x_column],
                    y=data[y_col],
                    mode='lines+markers',
                    name=y_col
                ))
            
            fig.update_layout(
                title=title,
                xaxis_title=x_column,
                yaxis_title="Values",
                template="plotly_white"
            )
            
            return {
                "type": "line",
                "config": json.loads(fig.to_json()),
                "html": fig.to_html(include_plotlyjs='cdn')
            }
            
        except Exception as e:
            logger.error(f"Error generating line chart: {str(e)}")
            raise
    
    @staticmethod
    def generate_pie_chart(df: pd.DataFrame, column: str, title: str = "Pie Chart",
                          top_n: int = 10) -> Dict[str, Any]:
        """Generate a pie chart"""
        try:
            value_counts = df[column].value_counts().head(top_n)
            
            fig = go.Figure(data=[go.Pie(
                labels=value_counts.index.tolist(),
                values=value_counts.values.tolist(),
                textinfo='label+percent',
                hoverinfo='label+value+percent'
            )])
            
            fig.update_layout(title=title, template="plotly_white")
            
            return {
                "type": "pie",
                "config": json.loads(fig.to_json()),
                "html": fig.to_html(include_plotlyjs='cdn')
            }
            
        except Exception as e:
            logger.error(f"Error generating pie chart: {str(e)}")
            raise
    
    @staticmethod
    def generate_scatter_plot(df: pd.DataFrame, x_column: str, y_column: str,
                             color_column: Optional[str] = None,
                             title: str = "Scatter Plot") -> Dict[str, Any]:
        """Generate a scatter plot"""
        try:
            data = df[[x_column, y_column]].dropna()
            
            if color_column and color_column in df.columns:
                fig = px.scatter(
                    df,
                    x=x_column,
                    y=y_column,
                    color=color_column,
                    title=title,
                    template="plotly_white"
                )
            else:
                fig = go.Figure(data=[go.Scatter(
                    x=data[x_column],
                    y=data[y_column],
                    mode='markers'
                )])
                fig.update_layout(
                    title=title,
                    xaxis_title=x_column,
                    yaxis_title=y_column,
                    template="plotly_white"
                )
            
            return {
                "type": "scatter",
                "config": json.loads(fig.to_json()),
                "html": fig.to_html(include_plotlyjs='cdn')
            }
            
        except Exception as e:
            logger.error(f"Error generating scatter plot: {str(e)}")
            raise
    
    @staticmethod
    def generate_histogram(df: pd.DataFrame, column: str, bins: int = 30,
                          title: str = "Histogram") -> Dict[str, Any]:
        """Generate a histogram"""
        try:
            data = df[column].dropna()
            
            fig = go.Figure(data=[go.Histogram(
                x=data,
                nbinsx=bins,
                name=column
            )])
            
            fig.update_layout(
                title=title,
                xaxis_title=column,
                yaxis_title="Frequency",
                template="plotly_white"
            )
            
            return {
                "type": "histogram",
                "config": json.loads(fig.to_json()),
                "html": fig.to_html(include_plotlyjs='cdn')
            }
            
        except Exception as e:
            logger.error(f"Error generating histogram: {str(e)}")
            raise
    
    @staticmethod
    def generate_box_plot(df: pd.DataFrame, columns: List[str],
                         title: str = "Box Plot") -> Dict[str, Any]:
        """Generate a box plot"""
        try:
            fig = go.Figure()
            
            for col in columns:
                if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
                    fig.add_trace(go.Box(
                        y=df[col].dropna(),
                        name=col
                    ))
            
            fig.update_layout(
                title=title,
                yaxis_title="Values",
                template="plotly_white"
            )
            
            return {
                "type": "box",
                "config": json.loads(fig.to_json()),
                "html": fig.to_html(include_plotlyjs='cdn')
            }
            
        except Exception as e:
            logger.error(f"Error generating box plot: {str(e)}")
            raise
    
    @staticmethod
    def generate_heatmap(df: pd.DataFrame, columns: Optional[List[str]] = None,
                        title: str = "Correlation Heatmap") -> Dict[str, Any]:
        """Generate a correlation heatmap"""
        try:
            # Select numeric columns
            if columns:
                numeric_df = df[columns].select_dtypes(include=['number'])
            else:
                numeric_df = df.select_dtypes(include=['number'])
            
            if numeric_df.empty or len(numeric_df.columns) < 2:
                raise ValueError("Need at least 2 numeric columns for heatmap")
            
            # Calculate correlation
            corr_matrix = numeric_df.corr()
            
            fig = go.Figure(data=go.Heatmap(
                z=corr_matrix.values,
                x=corr_matrix.columns.tolist(),
                y=corr_matrix.columns.tolist(),
                colorscale='RdBu',
                zmid=0,
                text=corr_matrix.values.round(2),
                texttemplate='%{text}',
                textfont={"size": 10},
                colorbar=dict(title="Correlation")
            ))
            
            fig.update_layout(
                title=title,
                template="plotly_white",
                xaxis={'side': 'bottom'}
            )
            
            return {
                "type": "heatmap",
                "config": json.loads(fig.to_json()),
                "html": fig.to_html(include_plotlyjs='cdn')
            }
            
        except Exception as e:
            logger.error(f"Error generating heatmap: {str(e)}")
            raise
    
    @staticmethod
    def generate_auto_chart(df: pd.DataFrame, columns: List[str] = None) -> Dict[str, Any]:
        """Automatically generate the most appropriate chart based on data"""
        try:
            if columns is None or len(columns) == 0:
                columns = df.columns.tolist()
            
            numeric_cols = df[columns].select_dtypes(include=['number']).columns.tolist()
            categorical_cols = df[columns].select_dtypes(include=['object', 'category']).columns.tolist()
            
            # Decision logic
            if len(numeric_cols) >= 2:
                # Multiple numeric: correlation heatmap
                return VisualizationService.generate_heatmap(df, numeric_cols, "Auto: Correlation Heatmap")
            elif len(numeric_cols) == 1 and len(categorical_cols) >= 1:
                # One numeric, one categorical: bar chart
                return VisualizationService.generate_bar_chart(
                    df, categorical_cols[0], numeric_cols[0], "Auto: Bar Chart"
                )
            elif len(categorical_cols) >= 1:
                # Only categorical: pie chart
                return VisualizationService.generate_pie_chart(df, categorical_cols[0], "Auto: Pie Chart")
            elif len(numeric_cols) == 1:
                # One numeric: histogram
                return VisualizationService.generate_histogram(df, numeric_cols[0], title="Auto: Histogram")
            else:
                raise ValueError("Cannot determine appropriate chart type for selected columns")
                
        except Exception as e:
            logger.error(f"Error generating auto chart: {str(e)}")
            raise
