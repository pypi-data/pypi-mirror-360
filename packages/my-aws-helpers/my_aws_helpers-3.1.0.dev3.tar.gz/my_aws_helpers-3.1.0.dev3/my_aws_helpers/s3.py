import boto3
import io
import json
from typing import Optional, Any, Dict
from copy import copy
import os
import gzip
from enum import Enum
from my_aws_helpers.logging import select_powertools_logger


logger = select_powertools_logger("aws-helpers-s3")


class ContentType(str, Enum):
    plain_text = "text/plain"
    xml_content = "text/xml"
    json_content = "application/json"
    pdf_content = "application/pdf"


class ContentEncoding(str, Enum):
    gzip = "gzip"


class S3Location:
    bucket: str
    file_name: str
    location: str

    @classmethod
    def from_location(cls, location: str):
        bucket, file_name = location.split("/")[0], "/".join(location.split("/")[1:])
        return cls(bucket=bucket, file_name=file_name)

    def __init__(self, bucket: str, file_name: str) -> None:
        self.bucket = bucket
        self.file_name = file_name
        self.location = f"{self.bucket}/{self.file_name}"

    def serialise(self):
        return copy(vars(self))


class S3:
    client: boto3.client

    def __init__(
        self,
        client: Optional[boto3.client] = None,
        resource: Optional[boto3.resource] = None,
    ) -> None:
        self.client = client if client else self._get_client()
        self.resource = resource if resource else boto3.resource('s3')

    def _get_client(self) -> boto3.client:
        region_name = os.environ["AWS_DEFAULT_REGION"]
        s3_client = boto3.client("s3", region_name=region_name)
        endpoint_url = s3_client.meta.endpoint_url
        s3_client = boto3.client(
            "s3", region_name=region_name, endpoint_url=endpoint_url
        )
        return s3_client

    def _streaming_body_to_dict(self, payload):
        file_like_obj = io.BytesIO(payload.read())
        response = json.loads(file_like_obj.getvalue())
        return response

    def put_json_object(self, bucket_name: str, file_name: str, object: dict):
        return self.client.put_object(
            Body=json.dumps(object), Bucket=bucket_name, Key=file_name
        )

    def get_object(self, bucket_name: str, file_name: str):
        response = self.client.get_object(Bucket=bucket_name, Key=file_name)
        return self._streaming_body_to_dict(response["Body"])

    def get_presigned_url(
        self, bucket_name: str, file_name: str, expires_in: int = 3600
    ):
        return self.client.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": bucket_name,
                "Key": file_name,
            },
            ExpiresIn=expires_in,
        )

    def get_s3_location_from_bucket_file(
        bucket_name: str, file_name: str
    ) -> S3Location:
        return S3Location(bucket=bucket_name, file_name=file_name)

    def get_bucket_file_from_s3_location(s3_location: S3Location) -> S3Location:
        return S3Location.from_location(location=s3_location)

    def save_document_content(
        self,
        file_contents: bytes,
        s3_location: S3Location,
        content_encoding: str = "",
        content_type: str = "application/pdf",
        compress: bool = True,
    ) -> Optional[S3Location]:
        """
        saves document content to bucket, in file_name
        Options for content_type:
            "application/pdf"
            "text/plain"
            "application/json"
            probably more
        Options for content_encoding:
            "": default encoding
            "gzip": compressed contents
        """
        try:
            if compress or s3_location.file_name.endswith(".gz"):
                file_contents = gzip.compress(file_contents)
                content_encoding = ContentEncoding.gzip.value
            obj = self.resource.Object(s3_location.bucket, s3_location.file_name)
            obj.put(
                Body=file_contents,
                ContentType=content_type,
                ContentEncoding=content_encoding,
            )
            return s3_location
        except Exception as e:
            logger.exception(e)
            return None        

    def read_binary_from_s3(self, s3_location: S3Location) -> Optional[bytes]:
        try:
            obj = self.resource.Object(s3_location.bucket, s3_location.file_name)
            d_bytes = io.BytesIO()
            obj.download_fileobj(d_bytes)
            d_bytes.seek(0)
            if obj.content_encoding == ContentEncoding.gzip.value:
                try:
                    with gzip.GzipFile(fileobj=d_bytes) as gz_file:
                        return gz_file.read()
                except gzip.BadGzipFile:
                    d_bytes.seek(0)
            return d_bytes.read()
        except Exception as e:
            logger.exception(f"Failed to read binary from s3 due to {e}")
            return None

    def save_text_to_s3(self, text: str, s3_location: S3Location):
        try:
            file_contents = bytes(text.encode("UTF-8"))
            return self.save_document_content(
                file_contents=file_contents,
                s3_location=s3_location,
                content_type=ContentType.plain_text.value,
                compress=True,
                content_encoding=ContentEncoding.gzip.value,
            )
        except Exception as e:
            logger.exception(f"Failed to save text to s3 due to {e}")
            return None

    def save_xml_to_s3(self, xml_text: bytes, s3_location: S3Location):
        """
        xml_text tends to come from:
            root = lxml.etree.ElementTree().get_root()
            xml_text = ET.tostring(root, encoding='utf-8')
        """
        try:
            return self.save_document_content(
                file_contents=xml_text,
                s3_location=s3_location,
                content_type=ContentType.xml_content.value,
                compress=True,
                content_encoding=ContentEncoding.gzip.value,
            )
        except Exception as e:
            logger.exception(f"Failed to save xml text to s3 due to {e}")
            return None

    def save_xml_to_s3(self, pdf_content: bytes, s3_location: S3Location):
        """
        pdf_content tends to come from:
            PyMuPdf.Document().write()
        """
        try:
            return self.save_document_content(
                file_contents=pdf_content,
                s3_location=s3_location,
                content_type=ContentType.pdf_content.value,
                compress=True,
                content_encoding=ContentEncoding.gzip.value,
            )
        except Exception as e:
            logger.exception(f"Failed to save pdf to s3 due to {e}")
            return None

    def save_dict_to_s3(self, content: Dict[str, Any], s3_location: S3Location):
        """ """
        try:
            file_contents = bytes(json.dumps(content).encode("UTF-8"))
            return self.save_document_content(
                file_contents=file_contents,
                s3_location=s3_location,
                content_type=ContentType.json_content.value,
                compress=True,
                content_encoding=ContentEncoding.gzip.value,
            )
        except Exception as e:
            logger.exception(f"Failed to save dict to s3 due to {e}")
            return None
