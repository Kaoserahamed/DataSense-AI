"""
Test script to verify visualization generation in chat
"""
import pandas as pd
from app.services.chat_service import ChatService

# Create sample data similar to student performance
data = {
    'study_hours': [2, 4, 6, 3, 5, 7, 4, 6, 8, 5],
    'attendance': [75, 85, 95, 80, 90, 98, 88, 92, 99, 87],
    'sleep_hours': [6, 7, 8, 6.5, 7.5, 8, 7, 7.5, 8, 7],
    'previous_grades': [65, 75, 85, 70, 80, 90, 78, 83, 92, 81],
    'final_exam_score': [68, 78, 88, 73, 83, 93, 80, 85, 95, 84]
}

df = pd.DataFrame(data)

# Test visualization request
question = "show me a heatmap of the correlations between numeric columns"

print(f"Testing question: {question}")
print(f"DataFrame shape: {df.shape}")
print(f"Columns: {df.columns.tolist()}\n")

result = ChatService.chat_with_data(df, question, dataset_name="test_data", dataset_id=1)

print("Result keys:", result.keys())
print("\nAnswer:", result.get("answer"))

if "visualization" in result:
    print("\n✓ Visualization detected!")
    viz = result["visualization"]
    print(f"  Type: {viz.get('type')}")
    print(f"  Title: {viz.get('title')}")
    print(f"  Has HTML: {bool(viz.get('html'))}")
    print(f"  Endpoint: {viz.get('endpoint')}")
else:
    print("\n✗ No visualization generated")
    if "error" in result:
        print(f"  Error: {result['error']}")
