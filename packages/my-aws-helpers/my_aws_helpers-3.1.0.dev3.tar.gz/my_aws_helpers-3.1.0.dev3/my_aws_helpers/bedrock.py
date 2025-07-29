from __future__ import annotations
import boto3
from botocore.config import Config
import json
import time
import os
import io
from typing import Optional, List, Dict
from enum import Enum
import pymupdf
import concurrent.futures
from dataclasses import dataclass

class PromptType(str, Enum):
    transaction_headers = "transactions_headers_prompt_v2.txt"
    transactions = "transactions_prompt.txt"
    # json = "json_system_prompt.txt"
    markdown = "markdown_system_prompt.txt"


@dataclass
class TokenUsage:
    input_tokens: int
    output_tokens: int
    total_tokens: int

    @classmethod
    def from_dict(cls, data: Dict[str, int]) -> TokenUsage:
        return cls(
            input_tokens=data.get('inputTokens', 0),
            output_tokens=data.get('outputTokens', 0),
            total_tokens=data.get('totalTokens', 0),
        )


@dataclass
class OCRResult:
    content: List[Dict[str, str]]
    token_usage: TokenUsage
    page_number: int

    @classmethod
    def from_dict(cls, data: Dict) -> OCRResult:
        return cls(
            content = data.get("content", []),
            token_usage = TokenUsage.from_dict(data.get("token_usage", {})),
            page_number = data.get("page_number", 0)
        )


class Bedrock:
    def __init__(
        self,
        model_id: str = "apac.anthropic.claude-3-5-sonnet-20241022-v2:0",
        logger = None,
        sleep_time: float = 1.0,
    ):

        self.session = Bedrock._set_session_params()
        self.logger = logger
        region_name = "ap-southeast-2"
        if self.session is None:
            self.session = boto3.Session(region_name = region_name)
        self.sleep_time = sleep_time
        
        custom_config = Config(
            retries={
                'max_attempts': 2,  # Total attempts = 1 initial + 1 retry
                'mode': 'standard',  # or 'adaptive'
            }
        )      
        self.client = self.session.client("bedrock-runtime", region_name=region_name, config = custom_config)
        self.model_id = model_id

    @staticmethod
    def _set_session_params():
        try:
            aws_access_key_id = os.environ["AWS_ACCESS_KEY_ID"]
            aws_secret_access_key = os.environ["AWS_SECRET_ACCESS_KEY"]
            aws_session_token = os.environ["AWS_SESSION_TOKEN"]
            region_name = os.environ["AWS_DEFAULT_REGION"]
            return boto3.Session(
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                aws_session_token=aws_session_token,
                region_name=region_name
            )
        except Exception as e:
            print(e)
            return None

    def _get_prompt(self, prompt_type: str) -> Optional[str]:
        if prompt_type not in list(PromptType):
            raise Exception(f"Error: Invalid prompt type")
        
        path = os.path.join(os.path.dirname(__file__), "prompts", prompt_type)
        try:
            with open(path, "r") as f:
                prompt = f.read()
                return prompt
        except Exception as e:
            self.logger.exception(f"Failed to get {prompt_type} prompt due to {e}")
        return None

    def _ocr(
        self, 
        prompt: str, 
        image_bytes: bytes,
        page_number: Optional[int] = 0
    ) -> Optional[OCRResult]:
        system_prompt = [{"text": prompt}]
        message = [
            {
                "role": "user",
                "content": [
                    {
                        "image": {
                            "format": "png",
                            "source": {
                                "bytes": image_bytes,
                            }
                        }
                    }
                ]
            }
        ]
        retries = 3
        for i in range(retries):
            self.logger.info(f"Attempt number {i} for {self.model_id} converse")
            try:
                response = self.client.converse(modelId = self.model_id, messages = message, system = system_prompt)
                if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                    break
            except Exception as e:
                self.logger.exception(f"Error during conversation due to {e}")
                if i >= len(retries) - 1: raise Exception(e)
                time.sleep(self.sleep_time)
                continue
        
        result = {}
        result["content"] = json.loads(response["output"]["message"]["content"][0]["text"])
        result["token_usage"] = response["usage"]
        result["page_number"] = page_number
        return OCRResult.from_dict(data = result)
    
    def _parallel_ocr(
            self, 
            image_bytes_list: List[bytes], 
            prompt: str,
            max_workers: int = 10,
    ):
        execution_futures = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            for i, img in enumerate(image_bytes_list):
                self.logger.info(f"Starting OCR for page: {i}")
                time.sleep(self.sleep_time)  # Stagger start time
                future = executor.submit(self._ocr, prompt=prompt, image_bytes=img)
                execution_futures.append(future)

        # Wait for all tasks and collect results in order of submission
        results = [future.result() for future in execution_futures if future.result() is not None]
        return results
    
    def get_ocr_result(
        self,
        pdf_bytes: io.BytesIO, 
        prompt_type: str,
        zoom: int = 7,
    ) -> List[OCRResult]:
        try:
            self.logger.info("Getting OCR Results")
            document = pymupdf.open(stream=pdf_bytes, filetype="pdf")
            pages: List[pymupdf.Page] = [p for p in document]

            image_bytes_list: List[bytes] = list()
            for i, p in enumerate(pages):
                try:
                    image_bytes: bytes = p.get_pixmap(matrix = pymupdf.Matrix(zoom, zoom)).tobytes("png")
                    image_bytes_list.append(image_bytes)
                except Exception as e:
                    self.logger.error(f"Could not get pix map for page {i}")
                    continue
            header_ocr_result = None
            if len(image_bytes_list) > 1:
                headers_prompt = self._get_prompt(prompt_type=PromptType.transaction_headers.value)
                for i in range(2):
                    # try to get headers from the first or second page
                    header_ocr_result = self._ocr(prompt=headers_prompt, image_bytes=image_bytes_list[i])
                    if header_ocr_result is None:
                        self.logger.info(f"No ocr result returned when getting headers {PromptType.transaction_headers.value}")
                    headers = header_ocr_result.content.get("headers")
                    if (len(headers) < 1) or (headers is None):
                        continue
                    else:
                        break

            transactions_prompt = self._get_prompt(prompt_type=prompt_type)
            if header_ocr_result:
                transactions_prompt = transactions_prompt.replace("#### TABLE HEADERS ####", json.dumps(header_ocr_result.content))

            self.logger.info("Got Prompt")
            results = list()

            results = self._parallel_ocr(image_bytes_list=image_bytes_list, prompt=transactions_prompt)

            # for i, image_bytes in enumerate(image_bytes_list):
            #     self.logger.info(f"Starting OCR for page: {i}")
            #     results.append(self._ocr(image_bytes=image_bytes, prompt=transactions_prompt))
            return results
        except Exception as e:
            self.logger.exception(e)
            return []
            