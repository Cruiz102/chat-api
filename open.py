import json
from langchain.document_loaders import TextLoader
import tempfile
with open('/home/cesarruiz/Projects/langchain/output.json', 'r') as file:
    data_json = json.load(file)
    # print(data_json['document']['pages'][3]['blocks'][1]['layout']['textAnchor']['textSegments'][0]['startIndex'])
    startIndex = int(data_json['document']['pages'][0]['blocks'][1]['layout']['textAnchor']['textSegments'][0]['startIndex'])
    endIndex = int(data_json['document']['pages'][0]['blocks'][1]['layout']['textAnchor']['textSegments'][0]['endIndex'])
    # with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as temp_file:
    #     temp_file.write(data.encode('utf-8'))
    #     temp_path = temp_file.name

    # loader = TextLoader(temp_path)
    # pages = loader.load_and_split()
    # pages[0].metadata["page"] = 4
    # print(pages[0])

# print("\n\n\n\n\n\n   HOLLLLAA")
# import json
# from langchain.document_loaders import JSONLoader
# file_path='./example_data/facebook_chat.json'
# data = json.loads(Path(file_path).read_text())