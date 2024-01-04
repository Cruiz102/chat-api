from langchain.vectorstores import Weaviate
from langchain.llms import OpenAI
from langchain.chains import ChatVectorDBChain
import weaviate
from langchain.chains import ConversationalRetrievalChain
from langchain.embeddings import OpenAIEmbeddings
import os
client = weaviate.Client(url=os.getenv("WEAVIATE_URL"),
                         auth_client_secret=weaviate.AuthApiKey(api_key=os.getenv("WEAVIATE_API_KEY")),
    additional_headers={
        "X-OpenAI-Api-Key": os.environ["OPENAI_API_KEY"]
    }
                          )

vectorstore = Weaviate(client, index_name=os.getenv("CLASSNAME"), text_key="text",
                    
                       embedding=OpenAIEmbeddings(chunk_size=200)).as_retriever()



# response = client.schema.get("ML104")
# print(response)

MyOpenAI = OpenAI(temperature=0,
    openai_api_key=os.environ["OPENAI_API_KEY"])

qa = ConversationalRetrievalChain.from_llm(MyOpenAI, retriever=vectorstore)

chat_history = []

print("Welcome to the Weaviate ChatVectorDBChain Demo!")
print("Please enter a question or dialogue to get started!")

while True:
    query = input("")
    result = qa({"question": query, "chat_history": chat_history})
    print(result["answer"])
    chat_history = [(query, result["answer"])]