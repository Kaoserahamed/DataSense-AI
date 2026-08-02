"""
Test explanation generation for summary stats
"""
import pandas as pd
from app.services.chat_service import ChatService

# Create sample data
data = {
    'study_hours': [2, 4, 6, 3, 5, 7, 4, 6, 8, 5],
    'attendance': [75, 85, 95, 80, 90, 98, 88, 92, 99, 87],
    'exam_score': [68, 78, 88, 73, 83, 93, 80, 85, 95, 84]
}

df = pd.DataFrame(data)

question = "what is the lowest and highest from this"

print(f"Testing question: {question}\n")

result = ChatService.chat_with_data(df, question, dataset_name="student_data", dataset_id=1)

print("Answer:")
print(result.get("answer"))
print("\n" + "="*80)

if "result" in result:
    print("\nResult data:")
    import json
    print(json.dumps(result["result"], indent=2, default=str))
