import asyncio
import argparse
import json
import logging
import os
from typing import Generator, Optional, Union, Dict, List, Any

import aiohttp
import fastapi
from fastapi import Depends, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.security.http import HTTPAuthorizationCredentials, HTTPBearer
import httpx
from pydantic import BaseSettings
import shortuuid
import tiktoken
import uvicorn
from protocols import APIChatCompletionRequest, ChatCompletionResponse, ChatCompletionResponseChoice, ChatCompletionRequest, UsageInfo

app_settings = AppSettings()
app = fastapi.FastAPI()
headers = {"User-Agent": "FastChat API Server"}
get_bearer_token = HTTPBearer(auto_error=False)



async def check_api_key(
    auth: Optional[HTTPAuthorizationCredentials] = Depends(get_bearer_token),
) -> str:
    if app_settings.api_keys:
        if auth is None or (token := auth.credentials) not in app_settings.api_keys:
            raise HTTPException(
                status_code=401,
                detail={
                    "error": {
                        "message": "",
                        "type": "invalid_request_error",
                        "param": None,
                        "code": "invalid_api_key",
                    }
                },
            )
        return token
    else:
        # api_keys not set; allow all
        return None


async def check_model(request: ChatCompletionRequest, token: str) -> Optional[JSONResponse]:
    controller_address = app_settings.controller_address
    ret = None

    models = await fetch_remote(controller_address + "/list_models", None, "models")
    if request.model not in models:
        ret = create_error_response(
            ErrorCode.INVALID_MODEL,
            f"Only {'&&'.join(models)} allowed now, your model {request.model}",
        )
    return ret


def check_requests(request) -> Optional[JSONResponse]:
    # Check all params
    if request.max_tokens is not None and request.max_tokens <= 0:
        return create_error_response(
            ErrorCode.PARAM_OUT_OF_RANGE,
            f"{request.max_tokens} is less than the minimum of 1 - 'max_tokens'",
        )
    if request.n is not None and request.n <= 0:
        return create_error_response(
            ErrorCode.PARAM_OUT_OF_RANGE,
            f"{request.n} is less than the minimum of 1 - 'n'",
        )
    if request.temperature is not None and request.temperature < 0:
        return create_error_response(
            ErrorCode.PARAM_OUT_OF_RANGE,
            f"{request.temperature} is less than the minimum of 0 - 'temperature'",
        )
    if request.temperature is not None and request.temperature > 2:
        return create_error_response(
            ErrorCode.PARAM_OUT_OF_RANGE,
            f"{request.temperature} is greater than the maximum of 2 - 'temperature'",
        )
    if request.top_p is not None and request.top_p < 0:
        return create_error_response(
            ErrorCode.PARAM_OUT_OF_RANGE,
            f"{request.top_p} is less than the minimum of 0 - 'top_p'",
        )
    if request.top_p is not None and request.top_p > 1:
        return create_error_response(
            ErrorCode.PARAM_OUT_OF_RANGE,
            f"{request.top_p} is greater than the maximum of 1 - 'temperature'",
        )
    if request.stop is not None and (
        not isinstance(request.stop, str) and not isinstance(request.stop, list)
    ):
        return create_error_response(
            ErrorCode.PARAM_OUT_OF_RANGE,
            f"{request.stop} is not valid under any of the given schemas - 'stop'",
        )

    return None

def _add_to_set(s, new_stop):
    if not s:
        return
    if isinstance(s, str):
        new_stop.add(s)
    else:
        new_stop.update(s)

async def get_conv(model_name: str, worker_addr: str):
    conv_template = conv_template_map.get((worker_addr, model_name))
    if conv_template is None:
        conv_template = await fetch_remote(
            worker_addr + "/worker_get_conv_template", {"model": model_name}, "conv"
        )
        conv_template_map[(worker_addr, model_name)] = conv_template
    return conv_template


async def get_gen_params(
    model_name: str,
    worker_addr: str,
    messages: Union[str, List[Dict[str, str]]],
    *,
    temperature: float,
    top_p: float,
    max_tokens: Optional[int],
    echo: Optional[bool],
    stop: Optional[Union[str, List[str]]],
) -> Dict[str, Any]:
    conv = await get_conv(model_name, worker_addr)
    conv = Conversation(
        name=conv["name"],
        system_template=conv["system_template"],
        system_message=conv["system_message"],
        roles=conv["roles"],
        messages=list(conv["messages"]),  # prevent in-place modification
        offset=conv["offset"],
        sep_style=SeparatorStyle(conv["sep_style"]),
        sep=conv["sep"],
        sep2=conv["sep2"],
        stop_str=conv["stop_str"],
        stop_token_ids=conv["stop_token_ids"],
    )

    if isinstance(messages, str):
        prompt = messages
    else:
        for message in messages:
            msg_role = message["role"]
            if msg_role == "system":
                conv.set_system_message(message["content"])
            elif msg_role == "user":
                conv.append_message(conv.roles[0], message["content"])
            elif msg_role == "assistant":
                conv.append_message(conv.roles[1], message["content"])
            else:
                raise ValueError(f"Unknown role: {msg_role}")

        # Add a blank message for the assistant.
        conv.append_message(conv.roles[1], None)
        prompt = conv.get_prompt()

    gen_params = {
        "model": model_name,
        "prompt": prompt,
        "temperature": temperature,
        "top_p": top_p,
        "max_new_tokens": max_tokens,
        "echo": echo,
        "stop_token_ids": conv.stop_token_ids,
    }

    new_stop = set()
    _add_to_set(stop, new_stop)
    _add_to_set(conv.stop_str, new_stop)

    gen_params["stop"] = list(new_stop)

    logger.debug(f"==== request ====\n{gen_params}")
    return gen_params


@app.post("/v1/chat/completions")
async def create_chat_completion(request: ChatCompletionRequest,  token: str = Depends(check_api_key)):
    """Creates a completion for the chat message"""
    error_check_ret = await check_model(request)
    if error_check_ret is not None:
        return error_check_ret
    error_check_ret = check_requests(request)
    if error_check_ret is not None:
        return error_check_ret


    gen_params = await get_gen_params(
        request.model,
        worker_addr,
        request.messages,
        temperature=request.temperature,
        top_p=request.top_p,
        max_tokens=request.max_tokens,
        echo=False,
        stop=request.stop,
    )
    gen_params["max_new_tokens"] = await check_length(
        request,
        gen_params["prompt"],
        gen_params["max_new_tokens"],
        worker_addr,
    )

    if request.stream:
        generator = chat_completion_stream_generator(
            request.model, gen_params, request.n, worker_addr
        )
        return StreamingResponse(generator, media_type="text/event-stream")

    choices = []
    chat_completions = []
    for i in range(request.n):
        content = asyncio.create_task(generate_completion(gen_params, worker_addr))
        chat_completions.append(content)
    try:
        all_tasks = await asyncio.gather(*chat_completions)
    except Exception as e:
        return create_error_response(ErrorCode.INTERNAL_ERROR, str(e))
    usage = UsageInfo()
    for i, content in enumerate(all_tasks):
        if content["error_code"] != 0:
            return create_error_response(content["error_code"], content["text"])
        choices.append(
            ChatCompletionResponseChoice(
                index=i,
                message=ChatMessage(role="assistant", content=content["text"]),
                finish_reason=content.get("finish_reason", "stop"),
            )
        )
        if "usage" in content:
            task_usage = UsageInfo.parse_obj(content["usage"])
            for usage_key, usage_value in task_usage.dict().items():
                setattr(usage, usage_key, getattr(usage, usage_key) + usage_value)

    return ChatCompletionResponse(model=request.model, choices=choices, usage=usage)


def create_openai_api_server():
    parser = argparse.ArgumentParser(
        description="FastChat ChatGPT-Compatible RESTful API server."
    )
    parser.add_argument("--host", type=str, default="localhost", help="host name")
    parser.add_argument("--port", type=int, default=8000, help="port number")
    parser.add_argument(
        "--allow-credentials", action="store_true", help="allow credentials"
    )
    parser.add_argument(
        "--api-keys",
        type=lambda s: s.split(","),
        help="Optional list of comma separated API keys",
    )
    parser.add_argument(
        "--ssl",
        action="store_true",
        required=False,
        default=False,
        help="Enable SSL. Requires OS Environment variables 'SSL_KEYFILE' and 'SSL_CERTFILE'.",
    )
    args = parser.parse_args()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=args.allowed_origins,
        allow_credentials=args.allow_credentials,
        allow_methods=args.allowed_methods,
        allow_headers=args.allowed_headers,
    )
    app_settings.controller_address = args.controller_address
    app_settings.api_keys = args.api_keys

    logger.info(f"args: {args}")
    return args


if __name__ == "__main__":
    args = create_openai_api_server()
    if args.ssl:
        uvicorn.run(
            app,
            host=args.host,
            port=args.port,
            log_level="info",
            ssl_keyfile=os.environ["SSL_KEYFILE"],
            ssl_certfile=os.environ["SSL_CERTFILE"],
        )
    else:
        uvicorn.run(app, host=args.host, port=args.port, log_level="info")