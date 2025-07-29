from typing import Optional, Dict, Any
from datetime import datetime, date
import json
from my_aws_helpers.errors import *


class API:

    def _serialise(obj):
        if isinstance(obj, datetime) or isinstance(obj, date):
            return obj.isoformat()
        return obj
    
    def response_serialiser(response: Any):
        if isinstance(response, list):
            return [API.response_serialiser(obj) for obj in response]
        if isinstance(response, dict):
            for k, v in response.items():
                response[k] = API.response_serialiser(v)
            return response
        return API._serialise(response)       

    def response(code: int, body: Optional[str] = None):
        return {
            "statusCode": code,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": body,
        }

    def get_optional_query_string_param(event: dict, param: str) -> Optional[Any]:
        query_string_params = event.get("queryStringParameters")
        if query_string_params is None:
            return None
        else:
            return query_string_params.get(param)

    def get_optional_body_param(event: dict, param: str):
        body = event.get("body")
        if body is None:
            return None
        else:
            body = json.loads(body)
        param_value = body.get(param)
        return param_value

    def parse_payload(event: Dict[str, Any]):
        payload = {}
        if event.get("queryStringParameters"):
            payload["queryStringParameters"] = event["queryStringParameters"]
        if event.get("pathParameters"):
            payload["pathParameters"] = event["pathParameters"]
        if event.get("body"):
            payload["body"] = json.loads(event["body"])
        return payload

    def handle_error_response(func):
        def wrapper(event, context):
            try:
                response = func(event, context)
                return API.response(code=200, body=json.dumps(response))
            except ClientError as e:
                return API.response(code=400, body=json.dumps({"Error": f"{e}"}))
            except NotFoundError as e:
                return API.response(code=404, body=json.dumps({"Error": f"{e}"}))
            except ServerError as e:
                return API.response(code=500, body=json.dumps({"Error": f"{e}"}))
            except Exception as e:
                return API.response(code=500, body=json.dumps({"Error": f"{e}"}))

        return wrapper
