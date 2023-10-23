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
from api_functions.cloud import should_use_ocr, main
from fastapi import FastAPI, File, UploadFile, HTTPException
import tempfile
from api_functions.database_implementation import init_weaviate_client, add_object, create_class
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import fitz  # PyMuPDF
import io
from PIL import Image
from fastapi import Form
# WEAVIATE_URL = os.environ["WEAVIATE_URL"]
# WEAVIATE_API_KEY = os.environ["WEAVIATE_API_KEY"]

import os


from pydantic import BaseModel

class UploadPDFRequest(BaseModel):
    url: str
    weaviate_api_key: str
    openai_api_key: str
    class_name: str


def list_pdf_files(directory):
    return [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.pdf')]


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to be more restrictive for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/upload_pdf/")
async def upload_pdf(
    url: str = Form(...),
    weaviate_api_key: str = Form(...),
    openai_api_key: str = Form(...),
    class_name: str = Form(...),
    file: UploadFile = File(...)):
    try:
        # Initialize Weaviate client
        client =init_weaviate_client(url=url, weaviate_api_key=weaviate_api_key, openai_api_key=openai_api_key)

        # Create a temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        pdf_path = temp_file.name

        # Write the uploaded content to this file
        content = await file.read()
        temp_file.write(content)
        temp_file.close()

        # Use PyPDFLoader to load and split the PDF
        # For now, use OCR is disabled
        if should_use_ocr(pdf_path) and False:
            main()
        else:
            loader = PyPDFLoader(pdf_path)
            pages = loader.load_and_split()

        # exist =  await check_if_class_is_created(client, class_name)

        try:
            create_class(client= client, class_name= class_name)
        except:
            print("Class already Exist")
         # Add the objects to Weaviate
        add_object(client, pages, class_name)


        return JSONResponse(content={"status": "success", "message": "Objects successfully added to Weaviate"})
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))
    


@app.post("/create_class/")
async def create_and_get_class(
    url: str = Form(...),
    weaviate_api_key: str = Form(...),
    openai_api_key: str = Form(...),
    class_name: str = Form(...),
):
    client =init_weaviate_client(url=url, weaviate_api_key=weaviate_api_key, openai_api_key=openai_api_key)
    create_class(client, class_name)
    class_schema = client.schema.get(class_name)
    print(class_schema)
    return {"message": "Class created and schema printed.", "schema": class_schema}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
