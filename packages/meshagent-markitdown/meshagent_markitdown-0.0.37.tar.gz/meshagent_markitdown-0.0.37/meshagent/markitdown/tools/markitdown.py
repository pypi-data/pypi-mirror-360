import fal_client
import aiohttp
import mimetypes
import uuid
import base64
from typing import Optional
from urllib.parse import urlparse
from openapi_core import OpenAPI
import json
import os
from meshagent.api import EmptyResponse, JsonResponse, FileResponse
from meshagent.tools import Tool, Toolkit, ToolContext, TextResponse, get_bytes_from_url, BlobStorage, RemoteToolkit
from copy import deepcopy
import logging
import urllib.parse
import asyncio
import aiofiles
import markitdown

logger = logging.getLogger("markitdown")



supported_extensions = { 
  ".pdf",
  ".docx",
  ".pptx",
  ".docx",
  ".heic",
  ".xlsx",
  # TODO: actually supports more formats, do we want others?  
}

class FileMarkItDownTool(Tool):
    def __init__(self):
        super().__init__(
            name = "markitdown_from_file",
            title = "MarkItDown File Adapter",
            description="Read the contents of a PDF or Office document from a file path",   
            input_schema = {
                "type" : "object",
                "additionalProperties" : False,
                "required" : [ "path" ],
                "properties" : {
                    "path" : {
                        "type" : "string"
                    }
                }
            })
        
    async def execute(self, *, context: ToolContext, path: str):

        filename, ext = os.path.splitext(path)
        if ext in supported_extensions:
            file : FileResponse = await context.room.storage.download(path=path)
            logger.info("adding office metadata for file: {path}".format(path=path))
            async with aiofiles.tempfile.NamedTemporaryFile('wb', suffix=ext) as f:
                await f.write(file.data)
                logger.info("tmp: {path}".format(path=f.name))
                converter = markitdown.MarkItDown()
                def convert():
                    return converter.convert(f.name)

                result = await asyncio.get_event_loop().run_in_executor(None, convert)

                return TextResponse(text=result.text_content)
        else:
            return EmptyResponse()


class UrlMarkItDownTool(Tool):
    def __init__(self, blob_storage: Optional[BlobStorage]  = None):
        super().__init__(
            name = "markitdown_from_url",
            title = "MarkItDown URL Adapter",
            description = "Read the contents of a PDF or Office document from a URL",
            input_schema = {
                "type" : "object",
                "additionalProperties" : False,
                "required" : [ "url" ],
                "properties" : {
                    "url" : {
                        "type" : "string"
                    }
                }
            })

        self._blob_storage = blob_storage
        self._session = aiohttp.ClientSession()
        
    async def execute(self, *, context: ToolContext, url: str):
        
        blob = await get_bytes_from_url(url=url, blob_storage=self._blob_storage)
        
        ext = mimetypes.guess_extension(blob.mime_type)
        if ext in supported_extensions:
            async with aiofiles.tempfile.NamedTemporaryFile('wb', suffix=ext) as f:

                # TODO: should protect against too large files with maximum file length?
                await f.write(blob.data)
                
                converter = markitdown.MarkItDown()
                def convert():
                    return converter.convert(f.name)

                result = await  asyncio.get_event_loop().run_in_executor(None, convert)

                return TextResponse(text=result.text_content)
        else:
            raise Exception("Unsupported file type, you cannot use this tool to retreive its content")
        

class AskUserMarkItDownTool(Tool):
    def __init__(self):
        super().__init__(
            name = "markitdown_from_user",
            title = "Read a file from a user",
            description = "Read the contents of a PDF or Office document the user. Requires ask_user_file tool to be available at runtime",
            input_schema = {
                "type": "object",
                "additionalProperties": False,
                "required": ["title", "description"],
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "a very short description suitable for a dialog title",
                    },
                    "description": {
                        "type": "string",
                        "description":
                            "helpful information that explains why this information is being collected and how it will be used",
                    },
                },
            }
        )
        
    async def execute(self, *, context: ToolContext, title: str, description: str):
        
        who = context.caller
        if context.on_behalf_of != None:
            who = context.on_behalf_of

        file_response : FileResponse = await context.room.agents.invoke_tool(
            participant_id=who.id,
            toolkit="ui",
            tool="ask_user_for_file",
            arguments={
                "title": title,
                "description":description
            }
        )

        
        ext = mimetypes.guess_extension(file_response.mime_type)

        logger.info(f"got file: {file_response.mime_type} {ext}")
        
        if ext in supported_extensions:
            async with aiofiles.tempfile.NamedTemporaryFile('wb', suffix=ext) as f:

                # TODO: should protect against too large files with maximum file length?
                await f.write(file_response.data)
                
                converter = markitdown.MarkItDown()
                def convert():
                    return converter.convert(f.name)

                result = await  asyncio.get_event_loop().run_in_executor(None, convert)

                return JsonResponse(json={
                    "filename" : file_response.name,
                    "mime_type" : file_response.mime_type,
                    "content" : result.text_content
                })
        else:
            raise Exception("Unsupported file type, you cannot use this tool to retreive its content")

class MarkItDownToolkit(RemoteToolkit):
    def __init__(self, blob_storage: Optional[BlobStorage] = None, name = "meshagent.markitdown"):
        super().__init__(
            name=name,
            title="markitdown",
            description="MarkItDown is a utility for converting various files to Markdown",   
            tools=[
                FileMarkItDownTool(),
                UrlMarkItDownTool(blob_storage=blob_storage),
                AskUserMarkItDownTool(),
            ])
