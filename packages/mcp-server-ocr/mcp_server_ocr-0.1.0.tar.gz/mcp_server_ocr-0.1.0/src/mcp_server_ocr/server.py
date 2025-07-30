import asyncio
import base64
import io
import os
from typing import Any, Dict, List, Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    ErrorData,
    GetPromptResult,
    Prompt,
    PromptArgument,
    PromptMessage,
    TextContent,
    Tool,
    INTERNAL_ERROR,
    INVALID_PARAMS,
)
from mcp.shared.exceptions import McpError
from pydantic import BaseModel, Field
from zhipuai import ZhipuAI
from PIL import Image


class OCRRequest(BaseModel):
    """Parameters for OCR request."""
    
    image_path: str = Field(description="Path to the image file to perform OCR on")
    prompt: Optional[str] = Field(
        default="请识别图片中的文字内容，保持原有格式输出",
        description="Custom prompt for OCR processing"
    )


class VideoOCRRequest(BaseModel):
    """Parameters for video OCR request."""
    
    video_path: str = Field(description="Path to the video file to perform OCR on")
    prompt: Optional[str] = Field(
        default="请识别视频中的文字内容，按时间顺序输出",
        description="Custom prompt for video OCR processing"
    )
    frame_interval: Optional[int] = Field(
        default=1,
        description="Extract frames every N seconds for OCR (default: 1 second)"
    )


class OCRService:
    def __init__(self):
        api_key = os.getenv("ZHIPU_API_KEY")
        if not api_key:
            raise ValueError("ZHIPU_API_KEY environment variable is required")
        
        self.client = ZhipuAI(api_key=api_key)
    
    def encode_image(self, image_path: str) -> str:
        """Encode image to base64 string."""
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            raise McpError(ErrorData(
                code=INTERNAL_ERROR,
                message=f"Failed to encode image: {str(e)}"
            ))
    
    async def ocr_image(self, image_path: str, prompt: str) -> str:
        """Perform OCR on an image using GLM-4.1V-Thinking-Flash."""
        try:
            if not os.path.exists(image_path):
                raise McpError(ErrorData(
                    code=INVALID_PARAMS,
                    message=f"Image file not found: {image_path}"
                ))
            
            # Encode image to base64
            base64_image = self.encode_image(image_path)
            
            # Call GLM-4.1V-Thinking-Flash API
            response = self.client.chat.completions.create(
                model="glm-4.1v-thinking-flash",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                temperature=0.1,
                max_tokens=4000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            raise McpError(ErrorData(
                code=INTERNAL_ERROR,
                message=f"OCR processing failed: {str(e)}"
            ))
    
    async def ocr_video(self, video_path: str, prompt: str, frame_interval: int = 1) -> str:
        """Perform OCR on video frames using GLM-4.1V-Thinking-Flash."""
        try:
            if not os.path.exists(video_path):
                raise McpError(ErrorData(
                    code=INVALID_PARAMS,
                    message=f"Video file not found: {video_path}"
                ))
            
            # For now, return a placeholder implementation
            # In a real implementation, you would:
            # 1. Extract frames from video at specified intervals
            # 2. Perform OCR on each frame
            # 3. Combine results with timestamps
            
            return f"Video OCR functionality is not yet implemented. Would process: {video_path}"
            
        except Exception as e:
            raise McpError(ErrorData(
                code=INTERNAL_ERROR,
                message=f"Video OCR processing failed: {str(e)}"
            ))


async def main():
    """Main entry point for the OCR MCP server."""
    
    # Initialize OCR service
    try:
        ocr_service = OCRService()
    except ValueError as e:
        print(f"Error initializing OCR service: {e}")
        return
    
    server = Server("mcp-ocr")
    
    @server.list_tools()
    async def list_tools() -> List[Tool]:
        return [
            Tool(
                name="ocr_image",
                description="Perform OCR (Optical Character Recognition) on an image file using GLM-4.1V-Thinking-Flash. Extracts text content from images.",
                inputSchema=OCRRequest.model_json_schema(),
            ),
            Tool(
                name="ocr_video",
                description="Perform OCR on video frames using GLM-4.1V-Thinking-Flash. Extracts text content from video frames at specified intervals.",
                inputSchema=VideoOCRRequest.model_json_schema(),
            ),
        ]
    
    @server.list_prompts()
    async def list_prompts() -> List[Prompt]:
        return [
            Prompt(
                name="ocr_image",
                description="Extract text from an image using OCR",
                arguments=[
                    PromptArgument(
                        name="image_path",
                        description="Path to the image file",
                        required=True
                    ),
                    PromptArgument(
                        name="prompt",
                        description="Custom prompt for OCR processing",
                        required=False
                    ),
                ],
            ),
            Prompt(
                name="ocr_video",
                description="Extract text from video frames using OCR",
                arguments=[
                    PromptArgument(
                        name="video_path",
                        description="Path to the video file",
                        required=True
                    ),
                    PromptArgument(
                        name="prompt",
                        description="Custom prompt for video OCR processing",
                        required=False
                    ),
                    PromptArgument(
                        name="frame_interval",
                        description="Extract frames every N seconds",
                        required=False
                    ),
                ],
            ),
        ]
    
    @server.call_tool()
    async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
        if name == "ocr_image":
            try:
                args = OCRRequest(**arguments)
            except ValueError as e:
                raise McpError(ErrorData(code=INVALID_PARAMS, message=str(e)))
            
            result = await ocr_service.ocr_image(args.image_path, args.prompt)
            return [TextContent(type="text", text=f"OCR Result for {args.image_path}:\n\n{result}")]
        
        elif name == "ocr_video":
            try:
                args = VideoOCRRequest(**arguments)
            except ValueError as e:
                raise McpError(ErrorData(code=INVALID_PARAMS, message=str(e)))
            
            result = await ocr_service.ocr_video(args.video_path, args.prompt, args.frame_interval)
            return [TextContent(type="text", text=f"Video OCR Result for {args.video_path}:\n\n{result}")]
        
        else:
            raise McpError(ErrorData(
                code=INVALID_PARAMS,
                message=f"Unknown tool: {name}"
            ))
    
    @server.get_prompt()
    async def get_prompt(name: str, arguments: Dict[str, Any] | None) -> GetPromptResult:
        if not arguments:
            raise McpError(ErrorData(code=INVALID_PARAMS, message="Arguments are required"))
        
        if name == "ocr_image":
            image_path = arguments.get("image_path")
            if not image_path:
                raise McpError(ErrorData(code=INVALID_PARAMS, message="image_path is required"))
            
            prompt = arguments.get("prompt", "请识别图片中的文字内容，保持原有格式输出")
            
            try:
                result = await ocr_service.ocr_image(image_path, prompt)
                return GetPromptResult(
                    description=f"OCR result for {image_path}",
                    messages=[
                        PromptMessage(
                            role="user",
                            content=TextContent(type="text", text=result)
                        )
                    ],
                )
            except McpError as e:
                return GetPromptResult(
                    description=f"Failed to process {image_path}",
                    messages=[
                        PromptMessage(
                            role="user",
                            content=TextContent(type="text", text=str(e))
                        )
                    ],
                )
        
        elif name == "ocr_video":
            video_path = arguments.get("video_path")
            if not video_path:
                raise McpError(ErrorData(code=INVALID_PARAMS, message="video_path is required"))
            
            prompt = arguments.get("prompt", "请识别视频中的文字内容，按时间顺序输出")
            frame_interval = arguments.get("frame_interval", 1)
            
            try:
                result = await ocr_service.ocr_video(video_path, prompt, frame_interval)
                return GetPromptResult(
                    description=f"Video OCR result for {video_path}",
                    messages=[
                        PromptMessage(
                            role="user",
                            content=TextContent(type="text", text=result)
                        )
                    ],
                )
            except McpError as e:
                return GetPromptResult(
                    description=f"Failed to process {video_path}",
                    messages=[
                        PromptMessage(
                            role="user",
                            content=TextContent(type="text", text=str(e))
                        )
                    ],
                )
        
        else:
            raise McpError(ErrorData(
                code=INVALID_PARAMS,
                message=f"Unknown prompt: {name}"
            ))
    
    # Initialize and run server
    options = server.create_initialization_options()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, options, raise_exceptions=True)


if __name__ == "__main__":
    asyncio.run(main())