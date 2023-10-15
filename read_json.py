
import json
import base64
from PIL import Image
from io import BytesIO
import matplotlib.pyplot as plt
# Load the request data from a file
# Replace 'path/to/request.json' with the path to your JSON request file
with open('/home/cesarruiz/Projects/langchain/output.json', 'r') as file:
    data = json.load(file)
    print(type(data))
    # print(type(data['document']['pages'][0]))
    # print(data['document']['text'][3700: 3700+100])
    # startIndex = int(data['document']['pages'][13]['blocks'][0]['layout']['textAnchor']['textSegments'][0]['startIndex'])
    # endIndex = int(data['document']['pages'][13]['blocks'][-1]['layout']['textAnchor']['textSegments'][0]['endIndex'])
    # print(data['document']['text'][startIndex : endIndex])
    # for i in data['document']['pages'][0]['image']:
    #     print(i[0])
        # print(i['layout']['textAnchor']['textSegments'][0]["startIndex"])
        # print(i['layout']['textAnchor']['textSegments'][0]["endIndex"])

# Get the base64-encoded image from the response
encoded_image = data['document']['pages'][-1]['image']['content']

# Decode the base64-encoded image
decoded_image = base64.b64decode(encoded_image)

# Create a writable memory buffer for the image
image_data = BytesIO(decoded_image)

# Read the image using the Pillow library
image = Image.open(image_data)

# image.save("qwerty.png")
# plt.imshow(image)
# plt.axis('off')  # Don't show the axes for clarity
# plt.show()



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




def search_page(data_json: dict, startIndex:int , endIndex:int):
    text = data_json['document']['text']
    ranges_of_pages = []

    for i in range(len(data['document']['pages'])):
        startIndex = int(data['document']['pages'][13]['blocks'][0]['layout']['textAnchor']['textSegments'][0]['startIndex'])
        endIndex = int(data['document']['pages'][13]['blocks'][-1]['layout']['textAnchor']['textSegments'][0]['endIndex'])
        ranges_of_pages.append((i,startIndex, endIndex))
    return ranges_of_pages






# Usage:
pdf_path = '/home/cesarruiz/Projects/langchain/small_api/research_pdfs/A Brief Account of Microscopical Observations - Robert Brown.pdf'
if should_use_ocr(pdf_path):
    print("Use OCR")
else:
    print("Use PDF Reader")