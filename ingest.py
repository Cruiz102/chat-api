"""Load html from files, clean up, split, ingest into Weaviate."""
import logging
import os
from bs4 import BeautifulSoup
import weaviate
from langchain.document_loaders import PyPDFLoader
from langchain.document_loaders.recursive_url_loader import RecursiveUrlLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Weaviate
from langchain.document_transformers import Html2TextTransformer
import argparse

# WEAVIATE_URL = os.environ["WEAVIATE_URL"]
# WEAVIATE_API_KEY = os.environ["WEAVIATE_API_KEY"]




import requests

url = "https://api.unstructured.io/general/v0/general"

headers = {
    "accept": "application/json",
    "unstructured-api-key": "9FsDd5baDfsROnTkpP5089F6Ce67Ob"
}

data = {
    "strategy": "hi_res",
    #  "hi_res_model_name": "chipper"
}

file_path = "/home/cesarruiz/Desktop/A Brief Account of Microscopical Observations - Robert Brown.pdf"
file_data = {'files': open(file_path, 'rb')}

response = requests.post(url, headers=headers, files=file_data, data=data)

file_data['files'].close()

json_response = response.json()
# print(json_response)
print(type(json_response))

for i, value in json_response.items():
    print(value)

import os

def list_pdf_files(directory):
    return [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.pdf')]



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

def add_object(client, objects_list, class_name):
    client.batch.configure(batch_size=100)
    with client.batch as batch:
        for i, d in enumerate(objects_list):
            print(f"importing question: {i+1}")
            object = {
             "document": d.metadata["source"],   
             "text": d.page_content,
             "page": d.metadata["page"]
        }
        batch.add_data_object(
            data_object=object,
            class_name= class_name
        )


@app.post("/upload_pdf/")
async def upload_pdf(file: UploadFile = File(...), class_name: str = ""):
    try:
        # Create a temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        pdf_path = temp_file.name

        # Write the uploaded content to this file
        content = await file.read()
        temp_file.write(content)
        temp_file.close()

        # Use PyPDFLoader to load and split the PDF
        if should_use_ocr(pdf_path):
            use_cloud()
        else:
            loader = PyPDFLoader(pdf_path)
            pages = loader.load_and_split()

        # Add the objects to Weaviate
        add_object(client, weaviate_objects, class_name)

        return JSONResponse(content={"status": "success", "message": "Objects successfully added to Weaviate"})
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))
    



def ingest_docs(args, client):
    documents = list_pdf_files(args.pdf_folder)
    # Check for errors when loading the pdfs
    if not isinstance(documents, str):
        assert(documents)
    for doc in documents:
        # print(doc)
        # pass
        # # print(type(doc))
        loader = PyPDFLoader(doc)
        s = loader.load_and_split()
        for i in s:
            print("-----------")
            print(i)
            print("-----------")
            print()

        # pages = loader.load_and_split()
        # add_object(client, pages, args.class_name)


    
    # vectorstore = Weaviate(
    #     client,
    #     WEAVIATE_DOCS_INDEX_NAME,
    #     "text",
    #     embedding=embedding,
    #     by_text=False,
    #     attributes=["source"],
    # )
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest PDFs into Weaviate database.")
    parser.add_argument("--pdf_folder", type=str, help="Path to the folder containing PDFs.", required=True)
    parser.add_argument("--class_name", type=str, help="Class where to save the object in the schema.", required=True)
    parser.add_argument("--new_class", type=str, help="Class where to save the object in the schema.", required=True)

    # args = parser.parse_args()
#     client = weaviate.Client(
#     url=WEAVIATE_URL,
#     auth_client_secret=weaviate.AuthApiKey(api_key=WEAVIATE_API_KEY),
#     additional_headers={
#         "X-OpenAI-Api-Key": os.environ["OPENAI_API_KEY"]
#     }
# )
#     if args.new_class:
#         create_class(args.class_name, client)
    # from langchain.document_loaders import UnstructuredFileLoader

    # loader = UnstructuredFileLoader("/home/cesarruiz/Desktop/A Brief Account of Microscopical Observations - Robert Brown.pdf")
    # from unstructured.partition.pdf import partition_pdf
    # elements = partition_pdf(filename="/home/cesarruiz/Desktop/A Brief Account of Microscopical Observations - Robert Brown.pdf")
    # titles = [elem for elem in elements if elem.category == "Title"]

    # for title in titles:
    #     print(title.text)
    



    # s = loader.load_and_split()
    # for i in s:
    #     print("-----------")
    #     print(i)
    #     print("-----------")
    #     print()
    # ingest_docs(args, None)