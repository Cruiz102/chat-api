from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List
from langchain.document_loaders import PyPDFLoader
import tempfile
from langchain.vectorstores import Weaviate
import weaviate


client = weaviate.Client(
url=WEAVIATE_URL,
auth_client_secret=weaviate.AuthApiKey(api_key=WEAVIATE_API_KEY),
additional_headers={
    "X-OpenAI-Api-Key": os.environ["OPENAI_API_KEY"]
}
)

class Weaviate_Object(BaseModel):
    text: datetime
    document: Tuple[int, int]
    page: int
    extracted_method: str
    author: str


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
                "description": "Content of the Chunk",
                "name": "text"
            },
            {
                "dataType": ["string"],
                "description": "Name of the document",
                "name": "document"
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
             "document": d.metadata["source"],   
             "page": d.metadata["page"]
        }
        batch.add_data_object(
            data_object=object,
            class_name= class_name
        )
