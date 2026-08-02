"""
Test transformation detection
"""
import pandas as pd
from app.services.chat_service import ChatService

# Create sample data with categorical columns
data = {
    'student_id': [1, 2, 3, 4, 5],
    'gender': ['Male', 'Female', 'Male', 'Female', 'Male'],
    'grade': ['A', 'B', 'A', 'C', 'B'],
    'score': [90, 85, 92, 78, 88]
}

df = pd.DataFrame(data)

question = "can you convert categorical columns into numerical columns"

print(f"Testing question: {question}")
print(f"DataFrame shape: {df.shape}")
print(f"Columns: {df.columns.tolist()}\n")

result = ChatService.chat_with_data(df, question, dataset_name="test_data", dataset_id=1)

print("Answer:")
print(result.get("answer"))
print("\n" + "="*80 + "\n")

if "result" in result:
    print("Preview of encoded data:")
    import json
    print(json.dumps(result["result"][:2], indent=2))
