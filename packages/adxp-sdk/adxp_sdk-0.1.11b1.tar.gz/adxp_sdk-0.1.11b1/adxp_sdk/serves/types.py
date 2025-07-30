import json
from enum import Enum, unique


@unique
class BaseEnum(str, Enum):
    @property
    def describe(self):
        return self.name, self.value

    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self) -> str:
        return json.dumps(self.value)

    def __eq__(self, v):
        try:
            return self.value == self.of(v).value
        except ValueError:
            return False

    @classmethod
    def _missing_(cls, type):
        try:
            if isinstance(type, str):
                matched = [item for item in cls if item.value.lower() == type.lower()]
            else:
                matched = [item for item in cls if item.value == type]
            return matched[0]

        except IndexError:
            raise ValueError(f"'{type}' is not in {cls.__name__}")

    def ignore_case(self) -> str:
        return str(self.value).lower()

    @classmethod
    def of(cls, type):
        return cls._missing_(type)

    @classmethod
    def choices(cls) -> list[tuple[str, str]]:
        return [(item.value, item.name) for item in cls]


def values_callable(x: Enum | BaseEnum):
    # (cls._member_map_[name] for name in cls._member_names_)
    return [e.value for e in x]


class HeaderKeys(BaseEnum):
    """Required Header keys of Agent App"""

    AIP_TOKEN = "aip-token"  # middleware에서 aip-token으로 변경
    AIP_USER = "aip-user"
    AIP_TRANSACTION_ID = "aip-transaction-id"
    AIP_APP_SERVING_ID = "aip-app-serving-id"
    AIP_COMPANY = "aip-company"
    AIP_DEPARTMENT = "aip-department"
    AIP_CHAT_ID = "aip-chat-id"
    AIP_SECRET_MODE = "secret-mode"
    AIP_APP_ID = "aip-app-id"