import os
import requests
from pathlib import Path

# Configuration
directory =   # Update this to the directory containing your PDF files
api_url =  # Endpoint URL
url =  # Endpoint URL
weaviate_api_key =  # Weaviate API Key
openai_api_key =   # OpenAI API Key
class_name = 'PAPERS'              # Class name for Weaviate

def upload_pdf(pdf_path):
    """Uploads a single PDF file to the specified endpoint."""
    files = {'file': (pdf_path.name, open(pdf_path, 'rb'), 'application/pdf')}
    data = {
        'url': url,
        'weaviate_api_key': weaviate_api_key,
        'openai_api_key': openai_api_key,
        'class_name': class_name
    }
    response = requests.post(api_url, files=files, data=data)
    return response

def process_directory(directory_path):
    """Processes all PDF files in the given directory."""
    path = Path(directory_path)
    for pdf_file in path.glob('*.pdf'):
        print(f"Uploading {pdf_file}...")
        response = upload_pdf(pdf_file)
        if response.status_code == 200:
            print(f"Successfully uploaded {pdf_file}.")
        else:
            print(f"Failed to upload {pdf_file}. Response: {response.text}")

if __name__ == '__main__':
    process_directory(directory)
