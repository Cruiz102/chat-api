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
WEAVIATE_DOCS_INDEX_NAME = "Research2"
app = FastAPI()
# WEAVIATE_URL = os.environ["WEAVIATE_URL"]
# WEAVIATE_API_KEY = os.environ["WEAVIATE_API_KEY"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from typing import List, Optional
class HistoryItem(BaseModel):
    question: str
    result: str

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[HistoryItem]]
    systemPrompt: str





from langchain.prompts import PromptTemplate
prompt_template = """You are a research assistant tasked with answering questions about materials science and chemistry. You have access to a database of papers on these subjects which you can query, but have no other knowledge outside of this database. You should always first query the database for information on the concepts in the question.

For example, given the following input question:
-----START OF EXAMPLE INPUT QUESTION-----
What are the properties of graphene in high-pressure environments?
-----END OF EXAMPLE INPUT QUESTION-----
Your research flow should be:

Query your search tool for information on 'Graphene properties in high-pressure environments' to get as much context as you can about it.
Then, query your search tool for information on 'Graphene' to get as much context as you can about it.
Answer the question with the context you have gathered.
For another example, given the following input question:
-----START OF EXAMPLE INPUT QUESTION-----
How is quantum chemistry applied in designing new materials?
-----END OF EXAMPLE INPUT QUESTION-----
Your research flow should be:

Query your search tool for information on 'Quantum chemistry in material design' to get as much context as you can about it.
Answer the question as you now have enough context.
Include accurate references from the papers in your answer if relevant to the question. If you can't find the answer, DO NOT make up an answer. Just say you don't know.

Answer the following question as best you can with the following context:
{chat_history}

Question: {question}

"""
PROMPT = PromptTemplate.from_template(prompt_template)

chain_type_kwargs = {"prompt": PROMPT}
def get_retriever():
    weaviate_client = weaviate.Client(
        url=WEAVIATE_URL,
        auth_client_secret=weaviate.AuthApiKey(api_key=WEAVIATE_API_KEY),
    )
    weaviate_client = Weaviate(
        client=weaviate_client,
        index_name=WEAVIATE_DOCS_INDEX_NAME,
        text_key="text",
        embedding=OpenAIEmbeddings(chunk_size=200),
        by_text=False,
        attributes=["document", "page"],
    )
    return weaviate_client.as_retriever(search_kwargs=dict(k=3))


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
async def chat_endpoint(request: ChatRequest):
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
            {"question": message.question}, {"result": message.result}
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
            qa = ConversationalRetrievalChain.from_llm(llm=llm, chain_type="stuff",condense_question_prompt=request.systemPrompt, memory = memory)
            result = qa({"question": question})
            q.put(job_done)

        t = Thread(target=task)
        t.start()

        content = ""

        while True:
            try:
                next_token = q.get(True, timeout=1)
                if next_token is job_done:
                    break
                content += next_token
                yield next_token
            except Empty:
                continue

    return StreamingResponse(stream())



if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080, reload=True)