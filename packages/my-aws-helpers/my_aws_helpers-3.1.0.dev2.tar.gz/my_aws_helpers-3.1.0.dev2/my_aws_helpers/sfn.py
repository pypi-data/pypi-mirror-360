import boto3
from typing import Optional
import json
from uuid import uuid4
from my_aws_helpers.api import API
from my_aws_helpers.errors import *


class SFN:
    client: boto3.client

    def __init__(self, client: Optional[boto3.client] = None) -> None:
        self.client = client if client else boto3.client("stepfunctions")

    def start_execution(
        self,
        sfn_arn: str,
        event: Optional[dict] = None,
        name: Optional[str] = uuid4().hex,
    ):
        input_event = json.dumps(event) if event else event
        return self.client.start_execution(
            stateMachineArn=sfn_arn,
            name=name,
            input=input_event,
        )

    def handle_error_response(func):
        def wrapper(event, context):
            try:
                response = func(event, context)
                return API.response(code=200, body=json.dumps(response))
            except AlreadyExists as e:
                return API.response(code=201, body=json.dumps({"Success": f"{e}"}))
            except ClientError as e:
                return API.response(code=400, body=json.dumps({"Error": f"{e}"}))
            except NotFoundError as e:
                return API.response(code=404, body=json.dumps({"Error": f"{e}"}))
            except ServerError as e:
                return API.response(code=500, body=json.dumps({"Error": f"{e}"}))
            except Exception as e:
                return API.response(code=500, body=json.dumps({"Error": f"{e}"}))

        return wrapper
