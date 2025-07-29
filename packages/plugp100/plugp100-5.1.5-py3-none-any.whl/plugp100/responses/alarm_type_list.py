from dataclasses import dataclass
from typing import List, Any

from plugp100.common.functional.tri import Try


@dataclass
class AlarmTypeList(object):
    tones: List[str]

    @staticmethod
    def try_from_json(kwargs: dict[str, Any]) -> Try["AlarmTypeList"]:
        return Try.of(lambda: AlarmTypeList(kwargs.get("alarm_type_list", [])))
