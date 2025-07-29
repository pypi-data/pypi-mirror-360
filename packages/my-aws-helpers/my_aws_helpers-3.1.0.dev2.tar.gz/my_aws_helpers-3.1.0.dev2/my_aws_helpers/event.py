from __future__ import annotations
from typing import Optional
from datetime import datetime
from enum import Enum
from uuid import uuid4
from copy import copy
from boto3.dynamodb.conditions import Key
from my_aws_helpers.dynamo import BaseTableObject, DynamoSerialiser, BaseQueries, Dynamo

class EventDynamoKeys:
    @staticmethod
    def get_event_pk(id: str):
        return f"id##{id}"
    
    @staticmethod
    def get_event_sk(id: str):
        return f"id##{id}"    


class EventStatus(str, Enum):
    in_progress = "in_progress"
    success = "success"
    fail = "fail"


class Event(BaseTableObject):
    status: str
    message: str
    id: str
    created_timestamp: datetime

    def __init__(
        self,
        status: str,
        message: str,
        id: str = None,
        created_timestamp: datetime = None,
    ):
        super().__init__()
        self.status: str = self.set_status(status=status)
        self.message: str = message
        self.id: str = id if id else uuid4().hex
        self.created_timestamp: datetime = created_timestamp if created_timestamp else datetime.now()

    def set_status(self, status: str) -> str:
        if status not in list(EventStatus):
            raise Exception("Status must be a member of EventStatus")
        return status

    def _get_pk(self):
        return EventDynamoKeys.get_event_pk(self.id)
    
    def _get_sk(self):
        return EventDynamoKeys.get_event_sk(self.id)  

    @classmethod
    def _from_dynamo_representation(cls, obj: dict):
        """
        Deserialises this object from Dynamo Representation
        """
        this_obj = copy(obj)
        this_obj.pop('pk')
        this_obj.pop('sk')
        return cls(**this_obj)

    def _to_dynamo_representation(self):
        """
        Serialises this object to Dynamo Representation
        """
        obj = copy(vars(self))
        obj['pk'] = self._get_pk()
        obj['sk'] = self._get_sk()
        return DynamoSerialiser.object_serialiser(obj=obj)


class EventQueries(BaseQueries):
    def __init__(self, table_name, client: Optional[Dynamo] = None):
        super().__init__(table_name, client)

    def put_event(self, event: Event) -> Event:
        response = self.client.put_item(item = event._to_dynamo_representation())
        if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
            return event
        raise Exception(f"Failed to put object into dynamo table")
    
    def get_event_by_id(self, id: str):
        pk = EventDynamoKeys.get_event_pk(id=id)
        sk = EventDynamoKeys.get_event_sk(id=id)
        results = self.client.table.query(
            KeyConditionExpression=Key("pk").eq(pk) & Key("sk").eq(sk)
        )
        if len(results["Items"]) < 1:
            return None
        if len(results["Items"]) > 1:
            raise Exception(f"Should only be 1 event with id {id}")
        return Event._from_dynamo_representation(obj = results["Items"][0])

