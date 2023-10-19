import json
import requests

# Your OpenAI API key
OPENAI_API_KEY = "?"

# API endpoint
url = 'http://0.0.0.0:3000/chat'

# Headers
headers = {
    
    "Authorization": f"Bearer {OPENAI_API_KEY}"
}

# Data payload
data = {
    "model": "gpt-3.5-turbo",
    "messages": [{"role": "user", "content": "Say this Broooooo!!!!"}],
    "temperature": 0.7,
    "stream": True
    
}

# Make the API call
response = requests.post(url, headers=headers, json=data)
print(response)
# Check if the request was successful
if response.status_code == 200:
    try:
        # Parse the JSON response
        response_json = response.json()
        print(response_json)

        # Serialize the JSON object to a string
        json_str = json.dumps(response_json, indent=4)

        # Print the serialized JSON
        print(json_str)

        # Save the serialized JSON to a text file
        with open('output.txt', 'w') as f:
            f.write(json_str)
        pass

    except json.JSONDecodeError:
        print("Failed to decode JSON.")
else:
    print(f"API call failed. Status code: {response.status_code}. Reason: {response.text}")
