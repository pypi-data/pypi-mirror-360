from dataclasses import dataclass
from typing import Union
from ecmind_blue_client.result import Result
from ecmind_blue_client.const import ImportActions


@dataclass
class DmsResult(Result):
    @property
    def object_id(self) -> Union[int, None]:
        """Contains the int value of the return Value ObjectID if exists else None"""
        if "ObjectID" in self.values:
            return self.values["ObjectID"]
        else:
            return None

    @property
    def object_type(self) -> Union[int, None]:
        """Contains the int value of the return Value ObjectType if exists else None"""
        if "ObjectType" in self.values:
            return self.values["ObjectType"]
        else:
            return None

    @property
    def import_action(self) -> Union[ImportActions, None]:
        """Contains the int value of the return Value ObjectType if exists else None"""

        if "Action" in self.values:
            return ImportActions[self.values["Action"]]
        else:
            return None
