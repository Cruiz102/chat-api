# from langchain.chat_models import ChatOpenAI
# from langchain.prompts.chat import (
#     ChatPromptTemplate,
#     SystemMessagePromptTemplate,
#     AIMessagePromptTemplate,
#     HumanMessagePromptTemplate,
# )
# from langchain.schema import AIMessage, HumanMessage, SystemMessage



# chat = ChatOpenAI(temperature=0)


# messages = [
#     SystemMessage(
#         content="You are a helpful assistant that translates English to French."
#     ),
#     HumanMessage(
#         content="Translate this sentence from English to French. I love programming."
#     ),
# ]
# print(chat(messages))

import requests
import json

# Define the API endpoint and headers
url = "https://api.openai.com/v1/chat/completions"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer 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",  # Replace YOUR_OPENAI_API_KEY with the actual API key
}

# Define the payload (request data)
payload = {
    "model": "gpt-3.5-turbo",
    "messages": [{"role": "user", "content": "Say this is a test!"}],
    "temperature": 0.7,
}

# Make the POST request
response = requests.post(url, headers=headers, data=json.dumps(payload))
js = response.json()
# Check if the request was successful
if response.status_code == 200:
    print("Success:", js)
    print("Success:", js["choices"][0]["message"]["content"])
    
else:
    print("Failed:", response.status_code, response.json())
