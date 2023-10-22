# import base_tool
import weaviate
from langchain.vectorstores import Weaviate
from langchain.embeddings import OpenAIEmbeddings
from typing import List


def get_retriever(url: str,api_key: str,openai_key: str, class_name:str, atributes: List[str], text_key: str):
    weaviate_client = weaviate.Client(
        url=url,
        auth_client_secret=weaviate.AuthApiKey(api_key=api_key),
         additional_headers={
        "X-OpenAI-Api-Key": openai_key
    }
    )
    weaviate_client = Weaviate(
        client=weaviate_client,
        index_name= class_name,
        text_key=text_key,
        embedding=OpenAIEmbeddings(chunk_size=200),
        by_text=False,
        attributes=atributes,
    )
    return weaviate_client.as_retriever(search_kwargs=dict(k=3))



def create_class(class_name: str, client ):
    class_obj = {
        "class": class_name,
        "vectorizer": "text2vec-openai", 
        "moduleConfig": {
            "text2vec-openai": {},
            "generative-openai": {} 
            },
        "properties": [
            {
                "dataType": ["string"],
                "description": "Name of the document",
                "name": "document"
            },
            {
                "dataType": ["string"],
                "description": "Content of the Chunk",
                "name": "text"
            },
            {
                "dataType": ["int"],
                "description": "Page of the document where is the chunk",
                "name": "page"
            },

        ]
    }
    client.schema.create_class(class_obj)

def add_object(client, objects_list, class_name:str, object_class:str):
    client.batch.configure(batch_size=100)
    with client.batch as batch:
        for i, d in enumerate(objects_list):
            print(f"importing question: {i+1}")
            object = object_class
            
            
        #     {
        #      "document": d.metadata["source"],   
        #      "text": d.page_content,
        #      "page": d.metadata["page"]
        # }
            batch.add_data_object(
                data_object=object,
                class_name= class_name
            )