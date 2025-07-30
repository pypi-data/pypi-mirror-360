from typing import Any, Optional, cast

import datetime

import boto3

from . import DataType, LastRun, ProspectDatabase


class DynamoDBLastRun(LastRun):
    """
    LastRun DynamoDB implementation.

    States will be saved in AWS DynamoDB.
    """

    def __init__(self, table: Any, key: str) -> None:
        super().__init__()
        self._db = table
        self._key = key

        key_: dict[str, str] = {
            'k': self._key,
            's': 'x',
        }

        response = self._db.get_item(
            Key=key_
        )

        self._data = cast(DataType, response.get('Item') or key_)

    def mark_successful_run(self) -> None:
        self._data['successful'] = {
            'datetime': datetime.datetime.now(datetime.UTC).isoformat(),
            'host': self.hostname  # is ignored on checking successful_less_than_24hour_ago
        }
        self._db.put_item(Item=self._data)

    def mark_failed_run_per_current_host(self) -> None:
        if 'failed' not in self._data:
            self._data['failed'] = {}

        self._data['failed'][self.hostname] = {
            'datetime': datetime.datetime.now(datetime.UTC).isoformat()
        }
        self._db.put_item(Item=self._data)


class DynamoDB(ProspectDatabase):
    """
    DynamoDB's implementation of database

    Documentation:
        https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#table
    """
    def __init__(self, dynamodb_resource: Optional[Any] = None) -> None:
        super().__init__()
        self._db = (dynamodb_resource or boto3.resource('dynamodb')).Table('scraper-bot')

    def __contains__(self, prospect: dict[str, str]) -> bool:
        response = self._db.get_item(
            Key={
                'k': str(prospect['product_id']),
                's': 'x',
            }
        )

        return 'Item' in response

    def write(self, prospect: dict[str, str]) -> None:
        """Save product"""
        prospect['k'] = str(prospect['product_id'])
        prospect['s'] = 'x'
        self._db.put_item(
            Item=prospect
        )

    def last_run(self, key: str) -> LastRun:
        return DynamoDBLastRun(table=self._db, key=key)
