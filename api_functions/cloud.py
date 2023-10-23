import base64
import json
import requests
import json
import fitz  # PyMuPDF
import io
from PIL import Image
from langchain.schema.document import Document
import tempfile
from langchain.document_loaders import TextLoader


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
    api_key = 'ya29.a0AfB_byDta8qT2DOqAmN-TECG1UJwRa2ZyrrqYi1mpj6hnTyJXn888EeOMzhRaQ0n-XFZVg07oxtRchrv46jUpefUOBB4tp2LctrFHWg5NGeUFO2xH_OaEwbjU0ZkQpToy_JrWmivL0XvMH_ccxyb-CEpbZhJAekpBYBK-waCgYKAQgSARESFQGOcNnC0I2NIANdU6NqGnQsg4CFTw0173'
    headers = {
        "Authorization": f"Bearer {api_key}",
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
        return response_json


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


def convert_to_document(text: str, range_pages: list) -> list:
    # Create a temporary text file and write the data to it
    with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as temp_file:
        temp_file.write(text.encode('utf-8'))
        temp_path = temp_file.name

    # Use TextLoader with the temporary text file
    loader = TextLoader(temp_path)
    pages = loader.load_and_split()

    # Initialize a variable to keep track of the current index in the text
    current_index = 0

    # Iterate through the range_pages to update the metadata of Langchain documents
    for page_number, start_index, end_index in range_pages:
        current_index = 0
        for doc in pages:
            # Calculate the final index of the text in the current document
            final_index = current_index + len(doc.page_content)

            # Check if the final index is within the range of the current page
            if start_index <= final_index <= end_index:
                print("page added")
                # Add metadata for the page number
                doc.metadata["page"] = page_number

            else:
                # print("\n")
                print("not added")
                print(start_index , final_index , end_index, len(doc.page_content))
                # print("\n")
                # print(doc.page_content)
            
                        # Update the current index
            current_index = final_index

    return pages

def search_page(data_json: dict):
    text = data_json['document']['text']
    ranges_of_pages = []

    for i in range(len(data_json['document']['pages'])):

        startIndex = int(data_json['document']['pages'][i]['blocks'][1]['layout']['textAnchor']['textSegments'][0]['startIndex'])
        endIndex = int(data_json['document']['pages'][i]['blocks'][1]['layout']['textAnchor']['textSegments'][0]['endIndex'])
        ranges_of_pages.append((i,startIndex, endIndex))
    return ranges_of_pages




def main():
    # Replace this placeholder with your actual PDF file path
    pdf_file_path = "/home/cesarruiz/Desktop/A Brief Account of Microscopical Observations - Robert Brown.pdf"

    # Step 1: Request text and other data from a PDF file
    data_json = google_cloud_ocr_request(None, pdf_file_path)  # Access token is now None due to your changes

    # Step 2: Call the search_page function to get the range of pages
    range_pages = search_page(data_json)

    # Extract the text from the JSON response
    text = data_json['document']['text']

    # Step 3: Convert to Langchain Document and add metadata
    documents = convert_to_document(text, range_pages)

    # Print the documents to verify
    # for doc in documents:
    #     print(doc)
        # print("Metadata:", doc.metadata['page'])

if __name__ == "__main__":
    main()

