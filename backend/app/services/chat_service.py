"""
Chat with data service - Natural language data analysis
"""
import pandas as pd
import json
import re
from typing import Dict, Any, Optional
from app.ai.llm_provider import llm_provider
import logging

logger = logging.getLogger(__name__)


class ChatService:
    """Service for chatting with datasets using natural language"""
    
    @staticmethod
    def chat_with_data(df: pd.DataFrame, question: str, dataset_name: str = "dataset") -> Dict[str, Any]:
        """
        Process natural language question about dataset
        
        Args:
            df: DataFrame to query
            question: Natural language question
            dataset_name: Name of dataset for context
            
        Returns:
            Dict with answer, code, result, and optional chart_config
        """
        if not llm_provider.is_available():
            return {
                "answer": "AI is not available. Please configure OPENAI_API_KEY.",
                "error": "AI_UNAVAILABLE"
            }
        
        # Get dataset context
        context = ChatService._get_dataset_context(df)
        
        # Generate Pandas code
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
            
            # Determine if chart is appropriate
            chart_config = ChatService._suggest_chart(question, result, df)
            
            return {
                "answer": explanation,
                "code": code,
                "result": result.get("data"),
                "result_type": result.get("type"),
                "chart_config": chart_config
            }
            
        except Exception as e:
            logger.error(f"Error in chat_with_data: {str(e)}", exc_info=True)
            return {
                "answer": f"An error occurred: {str(e)}",
                "error": "UNEXPECTED_ERROR"
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
            
            prompt = f"""Generate a clear, concise answer to the user's question based on the analysis result.

Question: {question}

Result Type: {result_type}
Result Data: {json.dumps(data, default=str)}

Dataset has {len(df)} rows and {len(df.columns)} columns.

Provide a natural language answer that:
1. Directly answers the question
2. Includes the key number(s) or finding(s)
3. Is concise (2-3 sentences max)
4. Sounds conversational

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
            return f"Found {len(data)} values: {json.dumps(data, default=str)}"
        elif result_type == "dataframe":
            return f"Found {len(data)} rows matching your query."
        elif result_type == "list":
            return f"Found {len(data)} items: {', '.join(map(str, data[:5]))}{'...' if len(data) > 5 else ''}"
        else:
            return f"Result: {str(data)}"
    
    @staticmethod
    def _suggest_chart(question: str, result: Dict[str, Any], df: pd.DataFrame) -> Optional[Dict[str, Any]]:
        """Suggest appropriate chart configuration"""
        result_type = result.get("type")
        data = result.get("data")
        
        # Check if question suggests visualization
        viz_keywords = ['trend', 'over time', 'compare', 'distribution', 'relationship', 'chart', 'graph', 'plot', 'visualize', 'show']
        should_visualize = any(keyword in question.lower() for keyword in viz_keywords)
        
        if not should_visualize:
            return None
        
        # Determine chart type based on result
        if result_type == "series" and isinstance(data, dict):
            if len(data) <= 20:
                return {
                    "type": "bar",
                    "data": {
                        "labels": list(data.keys()),
                        "values": list(data.values())
                    },
                    "title": "Result Visualization"
                }
        
        elif result_type == "dataframe" and isinstance(data, list) and len(data) > 0:
            # Simple bar chart for first two columns
            if len(data[0]) >= 2:
                keys = list(data[0].keys())
                return {
                    "type": "bar",
                    "data": {
                        "labels": [row[keys[0]] for row in data],
                        "values": [row[keys[1]] for row in data]
                    },
                    "title": "Result Visualization"
                }
        
        return None
