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
from api_functions.api_utils import list_files_recursively
import fitz  # PyMuPDF
import io
from PIL import Image
from fastapi import Form
from langchain.text_splitter import (
    Language,
    RecursiveCharacterTextSplitter,
)
# WEAVIATE_URL = os.environ["WEAVIATE_URL"]
# WEAVIATE_API_KEY = os.environ["WEAVIATE_API_KEY"]

import os


from pydantic import BaseModel

class UploadPDFRequest(BaseModel):
    url: str
    weaviate_api_key: str
    openai_api_key: str
    class_name: str

class DirectoryRequest(BaseModel):
    directory: str
    url: str
    weaviate_api_key: str
    openai_api_key: str
    class_name: str


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to be more restrictive for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def split_text_into_chunks(file: str):
    pass



@app.post("/upload_data/")
async def upload_data(
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

        file_extension = file.filename.split('.')[-1].lower()


        if file_extension == 'pdf':
            loader = PyPDFLoader(pdf_path)
            pages = loader.load_and_split()
        elif file_extension in ['py', 'js', 'ts', 'c']:
            # Lee el contenido del archivo de código fuente
            with open(pdf_path, 'r', encoding='utf-8') as code_file:
                code_content = code_file.read()

            # Procesa el contenido del archivo de código
            python_splitter = RecursiveCharacterTextSplitter.from_language(
                language=Language.PYTHON, chunk_size=512, chunk_overlap=0
            )
            python_docs = python_splitter.create_documents([code_content])
        
        

        try:
            create_class(client= client, class_name= class_name)
        except:
            print("Class already Exist")
         # Add the objects to Weaviate
        add_object(client, pages, class_name)


        return JSONResponse(content={"status": "success", "message": "Objects successfully added to Weaviate"})
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))
    

# ... [importaciones existentes] ...

@app.post("/process_directory/")
async def process_directory(request: DirectoryRequest):
    try:
        client = init_weaviate_client(
            url=request.url,
            weaviate_api_key=request.weaviate_api_key,
            openai_api_key=request.openai_api_key
        )



        try:
            create_class(client, request.class_name)
        except Exception as e:
            print(f"Class already exists or error creating class: {e}")


        # Lista de extensiones de archivos a procesar
        file_extensions = ['.pdf', '.py', '.js', '.ts', '.c']

        # Obtén un diccionario de archivos por extensión
        files_by_extension = list_files_recursively(request.directory, file_extensions)

        for ext, files in files_by_extension.items():
            for file_path in files:
                filename = os.path.basename(file_path)
                if ext == '.pdf':
                    # Procesa archivos PDF
                    loader = PyPDFLoader(file_path)
                    pages = loader.load_and_split()
                    add_object(client, pages, request.class_name)

                elif ext in ['.py', '.js', '.ts', '.c']:
                    # Procesa archivos de código
                    with open(file_path, 'r', encoding='utf-8') as code_file:
                        code_content = code_file.read()

                    # Ajusta el lenguaje según la extensión del archivo
                    language = Language.PYTHON if ext == '.py' else Language.OTHER
                    python_splitter = RecursiveCharacterTextSplitter.from_language(
                        language=language, chunk_size=512, chunk_overlap=0
                    )
                    python_docs = python_splitter.create_documents([code_content], metadatas=[{"source": filename}])
                    add_object(client, python_docs, request.class_name)

        return JSONResponse(content={"status": "success", "message": "Processed files in the directory and its subdirectories"})
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
