import requests
import json

# Replace this with your actual external IP from the kubectl command
EXTERNAL_IP = " 51.142.217.203"  # Replace with your IP

def test_model():
    # Test data
    test_data = {
            "texts": ["How much protein should a female eat", "summit define"],
            "instruction": "Given a web search query, retrieve relevant passages that answer the query:"
    }
    
    # Make the request
    try:
        response = requests.post(
                f"http://{EXTERNAL_IP}/encode",
                json=test_data,
                timeout=30
        )
        
        # Check if request was successful
        if response.status_code == 200:
            print("Success! Response:")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"Error: Status code {response.status_code}")
            print(response.text)
    
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")

if __name__ == "__main__":
    # Install required package if not already installed
    try:
        import requests
    except ImportError:
        print("Installing requests package...")
        import pip
        pip.main(['install', 'requests'])
    
    test_model()
