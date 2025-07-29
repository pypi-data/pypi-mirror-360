'''
@ TOOL for Image Inspection
'''

import base64
import json
import mimetypes
import os
import uuid
from io import BytesIO
from typing import Optional
import requests
from dotenv import load_dotenv
from PIL import Image

from .tools import Tool
from ..models import MessageRole, Model

load_dotenv(override=True)


class VisualInspectorTool(Tool):
    name = "inspect_file_as_image"
    description = """
You cannot load files directly: use this tool to process image files and answer related questions.
This tool supports the following image formats: [".jpg", ".jpeg", ".png", ".gif", ".bmp"]. For other file types, use the appropriate inspection tool."""

    inputs = {
        "file_path": {
            "description": "The path to the file you want to read as an image. Must be a '.something' file, like '.jpg','.png','.gif'. If it is text, use the text_inspector tool instead! If it is audio, use the audio_inspector tool instead! DO NOT use this tool for an HTML webpage: use the web_search tool instead!",
            "type": "string",
        },
        "question": {
            "description": "[Optional]: Your question about the image content. Provide as much context as possible. Do not pass this parameter if you just want to get a description of the image.",
            "type": "string",
            "nullable": True,
        },
    }
    output_type = "string"

    def __init__(self, model: Model, text_limit: int):
        super().__init__()
        self.model = model
        self.text_limit = text_limit
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.base_url = os.getenv("OPENAI_API_BASE")

    def _validate_file_type(self, file_path: str):
        """Validate if the file type is a supported image format"""
        if not any(file_path.lower().endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".gif", ".bmp"]):
            raise ValueError("Unsupported file type. Use the appropriate tool for text/audio files.")

    def _resize_image(self, image_path: str) -> str:
        """Resize image to reduce its size"""
        img = Image.open(image_path)
        width, height = img.size
        img = img.resize((int(width / 2), int(height / 2)))
        new_image_path = f"resized_{os.path.basename(image_path)}"
        img.save(new_image_path)
        return new_image_path

    def _encode_image(self, image_path: str) -> str:
        if image_path.startswith("http"):
            user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0"
            request_kwargs = {
                "headers": {"User-Agent": user_agent},
                "stream": True,
            }

            response = requests.get(image_path, **request_kwargs)
            response.raise_for_status()
            content_type = response.headers.get("content-type", "")

            extension = mimetypes.guess_extension(content_type)
            if extension is None:
                extension = ".download"

            fname = str(uuid.uuid4()) + extension
            download_path = os.path.abspath(os.path.join("downloads", fname))

            with open(download_path, "wb") as fh:
                for chunk in response.iter_content(chunk_size=512):
                    fh.write(chunk)

            image_path = download_path

        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    def _encode_image_with_grayscale(self, image_path: str) -> dict:
        if image_path.startswith("http"):
            user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0"
            request_kwargs = {
                "headers": {"User-Agent": user_agent},
                "stream": True,
            }
            response = requests.get(image_path, **request_kwargs)
            response.raise_for_status()
            content_type = response.headers.get("content-type", "")

            extension = mimetypes.guess_extension(content_type)
            if extension is None:
                extension = ".download"

            fname = str(uuid.uuid4()) + extension
            download_path = os.path.abspath(os.path.join("downloads", fname))
            os.makedirs(os.path.dirname(download_path), exist_ok=True)

            with open(download_path, "wb") as fh:
                for chunk in response.iter_content(chunk_size=512):
                    fh.write(chunk)

            image_path = download_path

        with Image.open(image_path) as img:
            original_buffer = BytesIO()
            img.save(original_buffer, format=img.format)
            original_b64 = base64.b64encode(original_buffer.getvalue()).decode("utf-8")
            grayscale_img = img.convert("L")  # 转为灰度图
            grayscale_buffer = BytesIO()
            grayscale_img.save(grayscale_buffer, format=img.format)
            grayscale_b64 = base64.b64encode(grayscale_buffer.getvalue()).decode("utf-8")

        return original_b64, grayscale_b64

    def _process_image_with_idefics(self, image_path: str, question: str) -> str:
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image"},
                    {"type": "text", "text": question},
                ],
            },
        ]

        prompt = self.idefics_processor.apply_chat_template(messages, add_generation_prompt=True)
        
        def encode_local_image(image_path):
            image = Image.open(image_path).convert("RGB")
            buffer = BytesIO()
            image.save(buffer, format="JPEG")
            base64_image = base64.b64encode(buffer.getvalue()).decode("utf-8")
            return f"data:image/jpeg;base64,{base64_image}"

        image_string = encode_local_image(image_path)
        prompt_with_images = prompt.replace("<image>", "![]({}) ").format(image_string)

        payload = {
            "inputs": prompt_with_images,
            "parameters": {
                "return_full_text": False,
                "max_new_tokens": 200,
            },
        }

        try:
            result = json.loads(self.idefics_client.post(json=payload).decode())[0]
            return result
        except Exception as e:
            if "Payload Too Large" in str(e):
                new_image_path = self._resize_image(image_path)
                return self._process_image_with_idefics(new_image_path, question)
            raise RuntimeError(f"Image processing failed: {str(e)}") from e

    def _process_image_with_qwen(self, image_path: str, question: str) -> str:
        mime_type, _ = mimetypes.guess_type(image_path)
        # base64_image, base64_image_gray = self._encode_image_with_grayscale(image_path)
        base64_image = self._encode_image(image_path)

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": question},
                    {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{base64_image}"}},
                    # {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{base64_image_gray}"}},
                ]
            }
        ]
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        try:
            response = requests.post(
                url=f"{self.base_url}/chat/completions",
                headers=headers,
                json={
                    "model": "qwen/qwen2.5-vl-72b-instruct:free",
                    "messages": messages,
                    "max_tokens": self.text_limit
                }
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except requests.exceptions.HTTPError as e:
            if response.status_code == 413:  # Payload Too Large
                new_image_path = self._resize_image(image_path)
                return self._process_image_with_qwen(new_image_path, question)
            raise RuntimeError(f"API request failed: {str(e)}") from e

    def forward(self, file_path: str, question: Optional[str] = None) -> str:
        self._validate_file_type(file_path)
        
        if not question:
            question = "Please write a detailed caption for this image."
        # try:
        #     description = self._process_image_with_qwen(file_path, question)
        # except Exception as qwen_error:
        try:
            mime_type, _ = mimetypes.guess_type(file_path)
            base64_image = self._encode_image(file_path)
            payload = {
                "model": "gpt-4.1",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": question},
                            {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{base64_image}"}},
                            # {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{base64_image_gray}"}},
                        ],
                    }
                ],
                "max_tokens": 1000,
            }

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }

            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            description = response.json()["choices"][0]["message"]["content"]
        except Exception as gpt_error:
            return f"Visual processing failed: {str(gpt_error)}"

        if not question.startswith("Please write a detailed caption"):
            return description
        return f"You did not provide a particular question, so here is a detailed description of the image: {description}"