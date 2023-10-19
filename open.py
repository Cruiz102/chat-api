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

# import requests
# import json


# # Define the payload (request data)
# payload = {
#     "model": "gpt-3.5-turbo",
#     "messages": [{"role": "user", "content": "Say this is a test!"}],
#     "temperature": 0.7,
# }

# # Make the POST request
# response = requests.post(url, headers=headers, data=json.dumps(payload))
# js = response.json()
# # Check if the request was successful
# if response.status_code == 200:
#     print("Success:", js)
#     print("Success:", js["choices"][0]["message"]["content"])
    
# else:
#     print("Failed:", response.status_code, response.json())
from langchain.chains import LLMChain
from langchain.llms import OpenAI
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from typing import Union, List, Dict
# template = """You are a chatbot having a conversation with a human.

# {chat_history}
# Human: {human_input}
# Chatbot:"""

# prompt = PromptTemplate(
#     input_variables=["chat_history", "human_input"], template=template
# )
# memory = ConversationBufferMemory(memory_key="chat_history")

# llm = OpenAI()
# llm_chain = LLMChain(
#     llm=llm,
#     prompt=prompt,
#     verbose=True,
#     memory=memory,
# )

# result = llm_chain.predict(human_input="Hi there my friend")

# print(result)


messages: Union[str, List[Dict[str, str]]] =  None
messages = 8

print(type(messages))