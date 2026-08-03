"""
Chat with data service - Natural language data analysis
Updated: 2026-08-02 - Added AI-powered visualization generation
"""
import pandas as pd
import json
import re
from typing import Dict, Any, Optional
from app.ai.llm_provider import llm_provider
from app.services.visualization_service import VisualizationService
import logging

logger = logging.getLogger(__name__)


class ChatService:
    """Service for chatting with datasets using natural language"""
    
    @staticmethod
    def chat_with_data(df: pd.DataFrame, question: str, dataset_name: str = "dataset", dataset_id: int = None) -> Dict[str, Any]:
        """
        Process natural language question about dataset
        
        Args:
            df: DataFrame to query
            question: Natural language question
            dataset_name: Name of dataset for context
            dataset_id: ID of dataset for visualization
            
        Returns:
            Dict with answer, code, result, and optional visualization
        """
        if not llm_provider.is_available():
            return {
                "answer": "AI is not available. Please configure OPENAI_API_KEY.",
                "error": "AI_UNAVAILABLE"
            }
        
        # Get dataset context
        context = ChatService._get_dataset_context(df)
        
        # Check if this is a data transformation request
        transform_result = ChatService._detect_transformation_request(df, question, context, dataset_id)
        if transform_result:
            return transform_result
        
        # Check if this is a visualization request
        viz_result = ChatService._detect_and_generate_visualization(df, question, context, dataset_id)
        if viz_result:
            return viz_result
        
        # Generate Pandas code for data analysis
        prompt = ChatService._create_code_generation_prompt(question, context, dataset_name)
        
        try:
            llm_response = llm_provider.generate_completion(prompt, temperature=0.1)
            
            # Extract code from response
            code = ChatService._extract_code(llm_response)
            
            if not code:
                return {
                    "answer": "Could not generate code for your question. Please rephrase.",
                    "error": "CODE_GENERATION_FAILED"
                }
            
            # Execute code safely
            result = ChatService._execute_code_safely(df, code)
            
            if result.get("error"):
                return {
                    "answer": f"Error executing query: {result['error']}",
                    "error": "EXECUTION_ERROR",
                    "code": code
                }
            
            # Generate explanation
            explanation = ChatService._generate_explanation(question, result, df)
            
            return {
                "answer": explanation,
                "code": code,
                "result": result.get("data"),
                "result_type": result.get("type")
            }
            
        except Exception as e:
            logger.error(f"Error in chat_with_data: {str(e)}", exc_info=True)
            return {
                "answer": f"An error occurred: {str(e)}",
                "error": "UNEXPECTED_ERROR"
            }
    
    @staticmethod
    def _detect_and_generate_visualization(df: pd.DataFrame, question: str, context: str, dataset_id: int = None) -> Optional[Dict[str, Any]]:
        """
        Detect if the question requests a visualization and generate it using AI
        
        Returns visualization dict or None if not a viz request
        """
        # Keywords that indicate visualization request
        viz_keywords = [
            'plot', 'chart', 'graph', 'visualize', 'visualization', 'show me',
            'draw', 'display', 'histogram', 'bar chart', 'pie chart', 'line chart',
            'scatter', 'heatmap', 'box plot', 'distribution', 'trend', 'correlation'
        ]
        
        question_lower = question.lower()
        is_viz_request = any(keyword in question_lower for keyword in viz_keywords)
        
        if not is_viz_request:
            return None
        
        # Use AI to determine appropriate visualization
        prompt = f"""You are a data visualization expert. Based on the user's question and dataset information, determine the best visualization and extract parameters.

{context}

User Question: {question}

Available chart types:
1. bar - Bar chart (needs: x_column, optional: y_column, horizontal)
2. line - Line chart (needs: x_column, y_columns as list)
3. pie - Pie chart (needs: column, optional: top_n)
4. scatter - Scatter plot (needs: x_column, y_column, optional: color_column)
5. histogram - Histogram (needs: column, optional: bins)
6. box - Box plot (needs: columns as list)
7. heatmap - Correlation heatmap (optional: columns as list)

Respond with ONLY a JSON object in this exact format:
{{
    "chart_type": "bar|line|pie|scatter|histogram|box|heatmap",
    "parameters": {{
        "x_column": "column_name",
        "y_column": "column_name",
        "y_columns": ["col1", "col2"],
        "column": "column_name",
        "columns": ["col1", "col2"],
        "color_column": "column_name",
        "bins": 30,
        "top_n": 10,
        "horizontal": false
    }},
    "title": "Descriptive title for the chart",
    "explanation": "Brief explanation of what this visualization shows"
}}

Only include parameters relevant to the chosen chart type. Use actual column names from the dataset.

JSON response:"""
        
        try:
            llm_response = llm_provider.generate_completion(prompt, temperature=0.2)
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', llm_response, re.DOTALL)
            if not json_match:
                logger.warning("Could not extract JSON from visualization prompt response")
                return None
            
            viz_config = json.loads(json_match.group(0))
            chart_type = viz_config.get("chart_type")
            parameters = viz_config.get("parameters", {})
            title = viz_config.get("title", "Visualization")
            explanation = viz_config.get("explanation", "Here's your visualization")
            
            if not chart_type:
                return None
            
            # Generate the visualization
            viz_result = None
            endpoint = None
            payload = None
            
            if chart_type == "bar":
                endpoint = "bar-chart"
                payload = {
                    "dataset_id": dataset_id,
                    "x_column": parameters.get("x_column"),
                    "y_column": parameters.get("y_column"),
                    "title": title,
                    "horizontal": parameters.get("horizontal", False)
                }
                if payload["x_column"]:
                    viz_result = VisualizationService.generate_bar_chart(
                        df, payload["x_column"], payload["y_column"], title, payload["horizontal"]
                    )
            
            elif chart_type == "line":
                endpoint = "line-chart"
                y_cols = parameters.get("y_columns", [])
                if not y_cols and parameters.get("y_column"):
                    y_cols = [parameters["y_column"]]
                payload = {
                    "dataset_id": dataset_id,
                    "x_column": parameters.get("x_column"),
                    "y_columns": y_cols,
                    "title": title
                }
                if payload["x_column"] and payload["y_columns"]:
                    viz_result = VisualizationService.generate_line_chart(
                        df, payload["x_column"], payload["y_columns"], title
                    )
            
            elif chart_type == "pie":
                endpoint = "pie-chart"
                payload = {
                    "dataset_id": dataset_id,
                    "column": parameters.get("column"),
                    "title": title,
                    "top_n": parameters.get("top_n", 10)
                }
                if payload["column"]:
                    viz_result = VisualizationService.generate_pie_chart(
                        df, payload["column"], title, payload["top_n"]
                    )
            
            elif chart_type == "scatter":
                endpoint = "scatter-plot"
                payload = {
                    "dataset_id": dataset_id,
                    "x_column": parameters.get("x_column"),
                    "y_column": parameters.get("y_column"),
                    "color_column": parameters.get("color_column"),
                    "title": title
                }
                if payload["x_column"] and payload["y_column"]:
                    viz_result = VisualizationService.generate_scatter_plot(
                        df, payload["x_column"], payload["y_column"], payload["color_column"], title
                    )
            
            elif chart_type == "histogram":
                endpoint = "histogram"
                payload = {
                    "dataset_id": dataset_id,
                    "column": parameters.get("column"),
                    "bins": parameters.get("bins", 30),
                    "title": title
                }
                if payload["column"]:
                    viz_result = VisualizationService.generate_histogram(
                        df, payload["column"], payload["bins"], title
                    )
            
            elif chart_type == "box":
                endpoint = "box-plot"
                payload = {
                    "dataset_id": dataset_id,
                    "columns": parameters.get("columns", []),
                    "title": title
                }
                if payload["columns"]:
                    viz_result = VisualizationService.generate_box_plot(
                        df, payload["columns"], title
                    )
            
            elif chart_type == "heatmap":
                endpoint = "heatmap"
                payload = {
                    "dataset_id": dataset_id,
                    "columns": parameters.get("columns"),
                    "title": title
                }
                viz_result = VisualizationService.generate_heatmap(
                    df, payload["columns"], title
                )
            
            if viz_result:
                return {
                    "answer": explanation,
                    "visualization": {
                        "type": chart_type,
                        "title": title,
                        "html": viz_result.get("html"),
                        "config": viz_result.get("config"),
                        "endpoint": endpoint,
                        "payload": payload
                    }
                }
            
        except Exception as e:
            logger.error(f"Error generating visualization: {str(e)}", exc_info=True)
            # Fall back to regular analysis if visualization fails
            return None
        
        return None
    
    @staticmethod
    def _detect_transformation_request(df: pd.DataFrame, question: str, context: str, dataset_id: int = None) -> Optional[Dict[str, Any]]:
        """
        Detect if the question requests a data transformation
        
        Returns transformation guidance or None if not a transformation request
        """
        # Keywords that indicate transformation request
        transform_keywords = [
            'encode', 'encoding', 'one-hot', 'onehot', 'dummy', 'dummies',
            'convert categorical', 'transform categorical', 'label encode',
            'normalize', 'standardize', 'scale', 'fill missing', 'impute',
            'remove duplicates', 'drop duplicates', 'remove outliers'
        ]
        
        question_lower = question.lower()
        is_transform_request = any(keyword in question_lower for keyword in transform_keywords)
        
        if not is_transform_request:
            return None
        
        # Detect specific transformation type
        if any(kw in question_lower for kw in ['encode', 'one-hot', 'onehot', 'dummy', 'convert categorical']):
            # Get categorical columns
            categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
            
            if not categorical_cols:
                return {
                    "answer": "There are no categorical columns in this dataset to encode."
                }
            
            # Show preview of encoding
            encoded_preview = pd.get_dummies(df, columns=categorical_cols[:2] if len(categorical_cols) > 2 else categorical_cols)
            
            answer = f"""Yes, categorical columns can be converted to numerical using one-hot encoding.

**Categorical columns found:** {', '.join(categorical_cols)}

**Impact:**
- Current columns: {len(df.columns)}
- After encoding: {len(encoded_preview.columns)} columns
- New binary columns will be created for each category

**⚠️ Important:** To save this transformation permanently, use the Data Cleaning API or page.

**API Endpoint to save:**
```
POST /cleaning/encode-categorical
{{
  "dataset_id": {dataset_id},
  "columns": {json.dumps(categorical_cols)},
  "method": "onehot",
  "save_as_new": true,
  "new_name": "{dataset_name}_encoded.csv"
}}
```

**Or use the Data Cleaning page:**
1. Go to **Data Cleaning**
2. Select **"Encode Categorical"**
3. Choose columns: {', '.join(categorical_cols)}
4. Method: **One-Hot Encoding**
5. Click **"Save as New Dataset"**

**Preview of new columns (first 10):**
{', '.join(list(encoded_preview.columns)[:10])}{'...' if len(encoded_preview.columns) > 10 else ''}"""
            
            return {
                "answer": answer,
                "code": f"# Preview of one-hot encoding\nresult = pd.get_dummies(df, columns={categorical_cols})",
                "result": encoded_preview.head(5).to_dict(orient='records'),
                "result_type": "dataframe",
                "transformation_action": {
                    "type": "encode",
                    "endpoint": "/cleaning/encode-categorical",
                    "payload": {
                        "dataset_id": dataset_id,
                        "columns": categorical_cols,
                        "method": "onehot",
                        "save_as_new": True,
                        "new_name": f"{dataset_name}_encoded.csv"
                    }
                }
            }
        
        # Generic transformation response
        return {
            "answer": "⚠️ **Data transformations in chat are temporary!**\n\nTo permanently save transformations, use the **Data Cleaning** page where you can:\n- Remove duplicates\n- Fill missing values\n- Encode categorical variables\n- Normalize/standardize numeric columns\n- Remove outliers\n- And more...\n\nAll changes can be saved as a new dataset to preserve your original data."
        }
    
    @staticmethod
    def _get_dataset_context(df: pd.DataFrame) -> str:
        """Get dataset context for prompt"""
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        
        sample_data = df.head(3).to_dict(orient='records')
        
        context = f"""Dataset Information:
- Total Rows: {len(df)}
- Total Columns: {len(df.columns)}
- Numeric Columns: {', '.join(numeric_cols) if numeric_cols else 'None'}
- Categorical Columns: {', '.join(categorical_cols) if categorical_cols else 'None'}

Sample Data (first 3 rows):
{json.dumps(sample_data, indent=2, default=str)}

All Column Names: {', '.join(df.columns.tolist())}
"""
        return context
    
    @staticmethod
    def _create_code_generation_prompt(question: str, context: str, dataset_name: str) -> str:
        """Create prompt for code generation"""
        return f"""You are a data analysis assistant. Generate Python Pandas code to answer the user's question about their dataset.

{context}

User Question: {question}

Generate ONLY the Pandas code needed to answer this question. The DataFrame is available as 'df'.

Rules:
1. Use ONLY Pandas operations (no other libraries)
2. Code must be safe (no file operations, no imports, no exec/eval)
3. Return a single value, Series, or small DataFrame
4. Use proper aggregation functions (mean, sum, count, etc.)
5. Handle missing values appropriately
6. Keep it simple and efficient
7. Do NOT include any explanations, just code

Format your response EXACTLY like this:
```python
# Your pandas code here
result = df['column'].mean()  # Example
```

Generate the code now:"""
    
    @staticmethod
    def _extract_code(llm_response: str) -> Optional[str]:
        """Extract Python code from LLM response"""
        # Try to find code block
        code_match = re.search(r'```python\n(.*?)\n```', llm_response, re.DOTALL)
        if code_match:
            return code_match.group(1).strip()
        
        # Try without language specifier
        code_match = re.search(r'```\n(.*?)\n```', llm_response, re.DOTALL)
        if code_match:
            return code_match.group(1).strip()
        
        # If no code block, try to extract any Python-looking code
        lines = llm_response.split('\n')
        code_lines = [line for line in lines if 'df[' in line or 'df.' in line or 'result' in line]
        if code_lines:
            return '\n'.join(code_lines).strip()
        
        return None
    
    @staticmethod
    def _execute_code_safely(df: pd.DataFrame, code: str) -> Dict[str, Any]:
        """Execute generated code safely in restricted environment"""
        # Security checks
        dangerous_keywords = ['import', 'exec', 'eval', 'open', 'file', '__', 'os.', 'sys.', 'subprocess']
        for keyword in dangerous_keywords:
            if keyword in code.lower():
                return {"error": f"Unsafe operation detected: {keyword}"}
        
        try:
            # Create safe namespace with only df available
            namespace = {
                'df': df.copy(),
                'pd': pd,
                'len': len,
                'str': str,
                'int': int,
                'float': float,
                'sum': sum,
                'min': min,
                'max': max,
                'round': round
            }
            
            # Execute code
            exec(code, namespace)
            
            # Get result
            result = namespace.get('result')
            
            if result is None:
                return {"error": "Code did not produce a result variable"}
            
            # Convert result to serializable format
            if isinstance(result, pd.Series):
                return {
                    "type": "series",
                    "data": result.to_dict()
                }
            elif isinstance(result, pd.DataFrame):
                return {
                    "type": "dataframe",
                    "data": result.to_dict(orient='records')[:100]  # Limit to 100 rows
                }
            elif isinstance(result, (int, float, str, bool)):
                return {
                    "type": "scalar",
                    "data": result
                }
            elif isinstance(result, list):
                return {
                    "type": "list",
                    "data": result[:100]  # Limit to 100 items
                }
            elif isinstance(result, dict):
                return {
                    "type": "dict",
                    "data": result
                }
            else:
                return {
                    "type": "other",
                    "data": str(result)
                }
                
        except Exception as e:
            logger.error(f"Error executing code: {str(e)}", exc_info=True)
            return {"error": str(e)}
    
    @staticmethod
    def _generate_explanation(question: str, result: Dict[str, Any], df: pd.DataFrame) -> str:
        """Generate natural language explanation of result"""
        if not llm_provider.is_available():
            return ChatService._generate_fallback_explanation(result)
        
        try:
            data = result.get("data")
            result_type = result.get("type")
            
            # Format data preview for better AI understanding
            data_preview = data
            if result_type == "dataframe" and isinstance(data, list) and len(data) > 10:
                data_preview = data[:10]  # Only show first 10 rows to AI
            
            prompt = f"""Generate a clear, helpful answer to the user's question based on the analysis result.

Question: {question}

Result Type: {result_type}
Result Data: {json.dumps(data_preview, default=str, indent=2)}

Dataset Info: {len(df)} rows, {len(df.columns)} columns
Column Names: {', '.join(df.columns.tolist())}

Your answer should:
1. DIRECTLY answer what the user asked
2. Include specific numbers and findings from the data
3. Be clear and conversational (2-4 sentences)
4. If it's summary statistics (min/max/mean/std), explain what they mean in context
5. Highlight the most important insights

Answer:"""
            
            explanation = llm_provider.generate_completion(prompt, temperature=0.3)
            return explanation.strip()
            
        except Exception as e:
            logger.error(f"Error generating explanation: {str(e)}")
            return ChatService._generate_fallback_explanation(result)
    
    @staticmethod
    def _generate_fallback_explanation(result: Dict[str, Any]) -> str:
        """Generate simple explanation without AI"""
        data = result.get("data")
        result_type = result.get("type")
        
        if result_type == "scalar":
            return f"The result is: {data}"
        elif result_type == "series":
            # Format series as a readable list
            if isinstance(data, dict) and len(data) > 0:
                items = [f"{k}: {v}" for k, v in list(data.items())[:5]]
                more = f" (and {len(data) - 5} more)" if len(data) > 5 else ""
                return f"Results:\n" + "\n".join(items) + more
            return f"Found {len(data)} values"
        elif result_type == "dataframe":
            if isinstance(data, list) and len(data) > 0:
                # Check if this looks like summary statistics
                first_row = data[0]
                if any(key in str(first_row) for key in ['min', 'max', 'mean', 'std', 'count']):
                    return f"Here are the summary statistics. See the table below for details."
                return f"Found {len(data)} rows. See the table below for details."
            return f"Found {len(data)} rows matching your query."
        elif result_type == "list":
            return f"Found {len(data)} items: {', '.join(map(str, data[:5]))}{'...' if len(data) > 5 else ''}"
        else:
            return f"Result: {str(data)}"
