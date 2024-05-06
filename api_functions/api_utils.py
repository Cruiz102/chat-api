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
import shortuuid
import tiktoken
import uvicorn
from protocols import  ChatCompletionResponse, ChatCompletionResponseChoice, UsageInfo

get_bearer_token = HTTPBearer(auto_error=False)

async def check_api_key(
    auth: Optional[HTTPAuthorizationCredentials] = Depends(get_bearer_token),
) -> str:

        return auth



from typing import Dict, List

def list_files_recursively(directory: str, file_extensions: List[str]) -> Dict[str, List[str]]:
    """Lista todos los archivos con extensiones específicas en un directorio y subdirectorios de manera recursiva."""
    files_by_extension = {ext: [] for ext in file_extensions}
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            for ext in file_extensions:
                if file.endswith(ext):
                    files_by_extension[ext].append(os.path.join(root, file))
                    break  # Si el archivo coincide con una extensión, no es necesario comprobar las demás

    return files_by_extension


# async def check_api_key(
#     auth: Optional[HTTPAuthorizationCredentials] = Depends(get_bearer_token),
# ) -> str:

#         return auth