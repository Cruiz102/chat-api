import base64
import json
import requests
import json
import fitz  # PyMuPDF
import io
from PIL import Image


def create_request_json(pdf_file_path: str):
    # Read and base64 encode the PDF content
    with open(pdf_file_path, "rb") as file:
        encoded_content = base64.b64encode(file.read()).decode("utf-8")

    # Create a dictionary for the request body
    request_body = {
        "raw_document": {
            "content": encoded_content,
            "mime_type": "application/pdf"
        }
    }
    return request_body

def google_cloud_ocr_request(access_token: str, pdf_file_path: str):
    # Get the access token
    # Replace this with your own method of getting an access token if necessary
    # Set the headers for the request
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json; charset=utf-8",
    }

    # Load the request data from a file
    data = create_request_json(pdf_file_path)

    # Set the URL for the request
    url = "https://us-documentai.googleapis.com/v1/projects/1011211656054/locations/us/processors/1303fb43a9f38f8/processorVersions/pretrained-ocr-v1.0-2020-09-23:process"

    # Make the request
    response = requests.post(url, headers=headers, json=data)

    # Check for a valid response
    if response.status_code == 200:
        # Parse the JSON response
        response_json = response.json()

        with open('/home/cesarruiz/output.json', 'w') as json_file:
            json.dump(response_json, json_file, indent=4)

        # Get the base64-encoded image from the response
        text = response_json['document']['text']


        print(text)


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

