from langchain.vectorstores import Weaviate
from langchain.llms import OpenAI
from langchain.chains import ChatVectorDBChain
import weaviate
from langchain.chains import ConversationalRetrievalChain
from langchain.embeddings import OpenAIEmbeddings
import os
client = weaviate.Client(url='!',
                         auth_client_secret=weaviate.AuthApiKey(api_key='!'),
    additional_headers={
        "X-OpenAI-Api-Key": os.environ["OPENAI_API_KEY"]
    }
                          )

vectorstore = Weaviate(client, index_name="Test", text_key="text", by_text= False,
                    
                       embedding=OpenAIEmbeddings(chunk_size=200)).as_retriever()



# response = client.schema.get("Test")
# print(response)

MyOpenAI = OpenAI(temperature=0.2,
    openai_api_key="!")

qa = ConversationalRetrievalChain.from_llm(MyOpenAI, retriever=vectorstore)

chat_history = []

print("Welcome to the Weaviate ChatVectorDBChain Demo!")
print("Please enter a question or dialogue to get started!")

while True:
    query = input("")
    result = qa({"question": query, "chat_history": chat_history})
    print(result["answer"])
    chat_history = [(query, result["answer"])]