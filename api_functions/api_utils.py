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
from protocols import  ChatCompletionResponse, ChatCompletionResponseChoice, UsageInfo

get_bearer_token = HTTPBearer(auto_error=False)

async def check_api_key(
    auth: Optional[HTTPAuthorizationCredentials] = Depends(get_bearer_token),
) -> str:

        return auth





# async def check_api_key(
#     auth: Optional[HTTPAuthorizationCredentials] = Depends(get_bearer_token),
# ) -> str:

#         return auth