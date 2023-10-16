from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List
from langchain.document_loaders import PyPDFLoader
import tempfile
from langchain.vectorstores import Weaviate
import weaviate
from fastapi.responses import JSONResponse


from protocols import ChatCompletionRequest, StreamChatCompletionResponseChoice, ChatMessage
# Initialize FastAPI app
app = FastAPI()


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
    

class QueueCallback(BaseCallbackHandler):
    """Callback handler for streaming LLM responses to a queue."""

    # https://gist.github.com/mortymike/70711b028311681e5f3c6511031d5d43

    def __init__(self, q):
        self.q = q

    def on_llm_new_token(self, token: str, **kwargs: any) -> None:
        self.q.put(token)

    def on_llm_end(self, *args, **kwargs: any) -> None:
        return self.q.empty()



@app.post("/chat")
async def chat_endpoint(request: ChatCompletionRequest):
    global run_id, feedback_recorded, trace_url
    run_id = None
    trace_url = None
    feedback_recorded = False


    question = request.message
    chat_history = request.history
    print(chat_history)
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    for message in chat_history:
        print(message)
        memory.save_context(
            {"question": message.role}, {"result": message.content}
        )

    def stream() -> Generator:
        global run_id, trace_url, feedback_recorded

        q = Queue()
        job_done = object()

        llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            streaming=True,
            temperature=0,
            callbacks=[QueueCallback(q)],
        )

        def task():
            qa = ConversationalRetrievalChain.from_llm(llm=llm, chain_type="stuff", retriever=get_retriever(),condense_question_prompt=request.systemPrompt, memory = memory)
            result = qa({"question": question})
            q.put(job_done)

        t = Thread(target=task)
        t.start()


        while True:
            try:
                next_token = q.get(True, timeout=1)
                if next_token is job_done:
                    break

                chat_response = StreamChatCompletionResponseChoice(
                id= request.id,
                model=request.model,
                choices= StreamChatCompletionResponseChoice(
                    index= 0, delta= ChatMessage(role="assistant", content= next_token),
                    finish_reason= None
                ),  # Your choices here, possibly including `content`
                usage=UsageInfo(prompt_tokens=10, total_tokens=50)  # Example usage info
            )


                yield next_token
            except Empty:
                continue

    return StreamingResponse(stream())




if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080, reload=True)