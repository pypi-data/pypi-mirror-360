from typing import List, Any, Optional
from datetime import datetime, date
import boto3
from abc import ABC, abstractmethod
from decimal import Decimal, Context 

from my_aws_helpers.logging import select_powertools_logger

logger = select_powertools_logger("aws-helpers-dynamo")

class MetaData:
    """
    This class is a convenience class,
    each of its attributes will be attached to objects that inherit from `BaseTableObject`
    """

    created_by: Optional[str]
    created_on: Optional[datetime]
    updated_by: Optional[str]
    updated_on: Optional[datetime]

    def set_timestamp(self, ts: Any) -> datetime:
        """Be absolutely sure timestamps are datetimes"""
        if isinstance(ts, datetime):
            return ts
        else:
            return datetime.now()

    def __init__(self, **kwargs) -> None:
        self.created_by = (
            kwargs["created_by"] if kwargs.get("created_by") else self._get_user()
        )
        self.updated_by = (
            kwargs["updated_by"] if kwargs.get("updated_by") else self._get_user()
        )
        self.created_on = self.set_timestamp(ts=kwargs.get("created_on"))
        self.updated_on = self.set_timestamp(ts=kwargs.get("updated_on"))

    def _get_user(self):
        """This should probably do some clever thing to get the actual user details from the token or something"""
        return ""


class BaseTableObject:
    """
    An Abstract class that helps ensure your objects
    conform to the AssetTable schema and
    implement serialisation/deserialisation for Dynamo
    """

    @abstractmethod
    def _get_pk(self):
        raise NotImplementedError()

    @abstractmethod
    def _get_sk(self):
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    def _from_dynamo_representation(cls):
        """
        Deserialises this object from Dynamo Representation
        """
        pass

    @abstractmethod
    def _to_dynamo_representation(self):
        """
        Serialises this object to Dynamo Representation
        """
        pass

    def _optional_get(self, kwargs: dict, key: str, default: Any):
        return kwargs.get(key) if kwargs.get(key) else default

    def __init__(self) -> None:
        pass
        


class DynamoSerialiser:

    @staticmethod
    def _serialise(obj: Any):
        if isinstance(obj, datetime) or isinstance(obj, date):
            return obj.isoformat()
        if isinstance(obj, float):
            ctx = Context(prec = 38)
            return ctx.create_decimal_from_float(obj)
        return obj
    
    @staticmethod
    def object_serialiser(obj: Any):
        if isinstance(obj, list):
            return [DynamoSerialiser.object_serialiser(obj=obj) for obj in obj]
        if isinstance(obj, dict):
            return {k: DynamoSerialiser.object_serialiser(v) for k, v in obj.items()}
        return DynamoSerialiser._serialise(obj=obj)

class Dynamo:
    table: boto3.resource

    def __init__(self, table_name: str) -> None:
        ddb = boto3.resource("dynamodb")
        self.table = ddb.Table(table_name)

    def put_item(self, item: dict):
        return self.table.put_item(Item=item)

    def get_item(self, item: dict):
        return self.table.get_item(Item=item)

    def delete_item(self, item: dict):
        return self.table.delete_item(Item=item)

    def batch_put(self, items: List[dict]) -> None:
        with self.table.batch_writer() as batch:
            for item in items:
                batch.put_item(Item=item)
        return

    def batch_delete(self, items: List[dict]) -> None:
        with self.table.batch_writer() as batch:
            for item in items:
                batch.delete_item(Key=item)
        return

    def _deep_scan(self):
        response = self.table.scan()
        items: List = response["Items"]
        while response.get("LastEvaluatedKey") is not None:
            response = self.table.scan(ExclusiveStartKey = response["LastEvaluatedKey"])
            if response.get("Items") is not None:
                items.extend(response["Items"])
            if response.get("LastEvaluatedKey") is None:
                break
        return items

    def delete_table_items(self, partition_key_name: str = "pk", sort_key_name: str = "sk") -> bool:
        try:
            items = self._deep_scan()
            delete_repr_items = [
                {
                    partition_key_name: item[partition_key_name],
                    sort_key_name: item[sort_key_name],
                }
                for item in items
            ]
            self.batch_delete(items = delete_repr_items)
            return True
        except Exception as e:
            logger.exception(f'Failed to delete table items due to {e}')
            return False

    def to_dynamo_representation(obj: dict):
        """
        Attempts to put common datatype transformations in one spot
        """
        new_obj = dict()
        for key, value in obj.items():
            new_obj[key] = _datatype_map(value=value)
        return new_obj


def _datatype_map(value: Any):
    if isinstance(value, float):
        return Decimal(str(value))
    if (isinstance(value, date)) or (isinstance(value, datetime)):
        return value.isoformat()
    if isinstance(value, list):
        return [_datatype_map(value=item) for item in value]
    if isinstance(value, dict):
        new_obj = dict()
        for k, v in value.items():
            new_obj[k] = _datatype_map(value=v)
        return new_obj
    return value

class BaseQueries(ABC):
    table_name: str

    def __init__(self, table_name: str, client: Optional[Dynamo] = None) -> None:
        self.table_name = table_name
        self.client = self._get_client() if client is None else client

    def _get_client(self):
        return Dynamo(table_name=self.table_name)
    
    def _iterative_query(self, query_kwargs: dict) -> List[dict]:
        results = list()
        last_evaluated_key = "not none"
        exclusive_start_key = None
        while last_evaluated_key is not None:
            if exclusive_start_key is not None:
                query_kwargs["ExclusiveStartKey"] = exclusive_start_key
            result = self.client.table.query(**query_kwargs)
            results += result["Items"]
            last_evaluated_key = result.get("LastEvaluatedKey")
            exclusive_start_key = last_evaluated_key
        return results