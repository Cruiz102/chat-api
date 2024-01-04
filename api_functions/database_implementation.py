from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List
from langchain.document_loaders import PyPDFLoader
import tempfile
from langchain.vectorstores import Weaviate
import weaviate

import asyncio


def init_weaviate_client(url: str, weaviate_api_key: str,openai_api_key : str):
    client = weaviate.Client(url=url,
                         auth_client_secret=weaviate.AuthApiKey(api_key= weaviate_api_key),
    additional_headers={
        "X-OpenAI-Api-Key": openai_api_key
    }
                          )
    
    return client



async def check_if_class_is_created_async(client , class_name):

    try:
        response = await client.schema.get(class_name)
        if response:
            return True
    except:
        return False




def create_class( client , class_name: str,):
    class_obj = {
        "class": class_name,
        "vectorizer": "text2vec-openai",  
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

def add_object(client, objects_list, class_name):
    client.batch.configure(batch_size=100)
    with client.batch as batch:
        for i, d in enumerate(objects_list):
            print(f"importing question: {i+1}")
            object = {
            "text": d.page_content,
             "document": d.metadata.get("source", ""),   
             "page": d.metadata.get("page", 0)
        }
            batch.add_data_object(
                data_object=object,
                class_name= class_name
            )


if __name__ == "__main__":
    client = init_weaviate_client(url = 'https://researchcluster-h1x0s5a1.weaviate.network', weaviate_api_key='Rf26fdIA4bLpwBdSQypkS2Y8u4cQZbekMyi8', openai_api_key='')
    # create_class(client, "ML30")
    # print(client.schema.get("ML30"))
    # a = await check_if_class_is_created_async(client, "ML")
    a  = asyncio.run(check_if_class_is_created_async(client, "ML102"))
    print(a)