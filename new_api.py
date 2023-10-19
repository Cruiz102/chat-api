from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List
from langchain.document_loaders import PyPDFLoader
import tempfile
from langchain.vectorstores import Weaviate
from langchain.callbacks import get_openai_callback
import weaviate
from fastapi.responses import JSONResponse

import weaviate
from langchain.vectorstores import Weaviate
from langchain.embeddings import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from fastapi import FastAPI, Request
import os
from threading import Thread
from queue import Queue, Empty
from collections.abc import Generator
from langchain.chains import RetrievalQA
from langchain.memory import ConversationBufferMemory
"""Main entrypoint for the app."""
import os
import weaviate
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Weaviate
from threading import Thread
from queue import Queue, Empty
from collections.abc import Generator
from langchain.callbacks.base import BaseCallbackHandler
from langchain.chains import ConversationalRetrievalChain

from protocols import ChatCompletionRequest, StreamChatCompletionResponseChoice, ChatMessage, UsageInfo, ChatCompletionResponse, StreamChatCompletionResponse, StreamChatMessage
import json

from langchain.chains import LLMChain
from langchain.llms import OpenAI
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
# Initialize FastAPI app
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to be more restrictive for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
prompt_template = """You are a research assistant tasked with answering questions about materials science and chemistry. You have access to a database of papers on these subjects which you can query, but have no other knowledge outside of this database. You should always first query the database for information on the concepts in the question.


{chat_history}

Question: {question}

"""
PROMPT = PromptTemplate.from_template(prompt_template)


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

    print(request)

    global run_id, feedback_recorded, trace_url, usage
    run_id = None
    trace_url = None
    feedback_recorded = False

    messages = request.messages
    print(type(messages))
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    for message in messages:
        print(message)
        memory.save_context(
            {"role": message["role"]}, {"content": message["content"]}
        )

    def stream() -> Generator:
        global run_id, trace_url, feedback_recorded, usage


        q = Queue()
        job_done = object()

        llm = ChatOpenAI(
            model= request.model,
            streaming=True,
            temperature=0,
            callbacks=[QueueCallback(q)],
        )

        def task():
            llm_chain = LLMChain(
                llm=llm,
                prompt=PROMPT,
                verbose=True,
                memory=memory)
         
            result = llm_chain.predict(question=messages[-1]["content"])
               
     

            q.put(job_done)

        t = Thread(target=task)
        t.start()


        while True:
            try:
                next_token = q.get(True, timeout=1)
                finish_reason_value = None  # Default to None

                if next_token is job_done:
                    finish_reason_value = "stop"  # Set to "stop" for the final response

    

                chat_response = StreamChatCompletionResponse(
            model=request.model,
            choices=[StreamChatCompletionResponseChoice(
                index=0, delta=StreamChatMessage( content=next_token if next_token is not job_done else ""),
                finish_reason=finish_reason_value
            )]
        )

                
                json_data = json.dumps(chat_response.dict())
            
                yield f"data: {json_data}\n\n"

                if next_token is job_done:
                    break

            except Empty:
                continue

    return StreamingResponse(stream(), media_type="text/event-stream")




if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080, reload=True)