from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List
from langchain.document_loaders import PyPDFLoader
import tempfile
from langchain.vectorstores import Weaviate
import weaviate
# Initialize FastAPI app
app = FastAPI()

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


import fitz  # PyMuPDF
import io
from PIL import Image

def count_images_and_pages(pdf_path):
    pdf_document = fitz.open(pdf_path)
    page_count = len(pdf_document)
    image_count = 0

    for page_number in range(page_count):
        page = pdf_document.load_page(page_number)
        img_list = page.get_images(full=True)
        image_count += len(img_list)

    pdf_document.close()
    return page_count, image_count

def should_use_ocr(pdf_path):
    page_count, image_count = count_images_and_pages(pdf_path)
    print(page_count, image_count)
    if image_count / page_count >= 0.9:
        return True  # Use OCR
    else:
        return False  # Use PDF Reader

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



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080, reload=True)