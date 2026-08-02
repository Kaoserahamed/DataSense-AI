"""
Test the actual API response for visualization
"""
import requests
import json

# Test with your local backend
url = "http://localhost:8000/chat/ask"
payload = {
    "dataset_id": 2,  # Your student dataset
    "question": "can you show the pie chart with necessary distributions",
    "save_history": False
}

response = requests.post(url, json=payload)
print(f"Status: {response.status_code}\n")

if response.status_code == 200:
    data = response.json()
    print("Response keys:", list(data.keys()))
    print("\nAnswer:", data.get("answer"))
    print("\nVisualization present:", "visualization" in data)
    
    if "visualization" in data:
        viz = data["visualization"]
        print("\nVisualization structure:")
        print(f"  Keys: {list(viz.keys())}")
        print(f"  Type: {viz.get('type')}")
        print(f"  Title: {viz.get('title')}")
        print(f"  Has HTML: {bool(viz.get('html'))}")
        print(f"  HTML length: {len(viz.get('html', ''))}")
        print(f"  Endpoint: {viz.get('endpoint')}")
        print(f"  Payload: {viz.get('payload')}")
        
        # Show first 200 chars of HTML
        if viz.get('html'):
            print(f"\nHTML preview: {viz['html'][:200]}...")
    else:
        print("\n❌ No visualization in response")
        print("Full response:", json.dumps(data, indent=2, default=str)[:500])
else:
    print("Error:", response.text)
