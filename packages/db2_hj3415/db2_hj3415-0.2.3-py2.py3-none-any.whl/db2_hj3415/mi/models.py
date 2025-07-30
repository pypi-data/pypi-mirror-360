from datetime import datetime
from bson import ObjectId
from pydantic import BaseModel, Field, field_validator, field_serializer, ConfigDict
from . import DATE_FORMAT


class Common(BaseModel):
    id: str | None = Field(default=None, alias="_id")
    날짜: datetime

    @field_validator("id", mode="before")
    @classmethod
    def cast_objectid(cls, v):
        return str(v) if isinstance(v, ObjectId) else v

    @field_validator("날짜", mode="before")
    @classmethod
    def parse_date(cls, v):
        # ① 이미 datetime 이면 그대로 통과
        if isinstance(v, datetime):
            return v
        # ② YYYY.MM.DD 형태의 순수 문자열
        if isinstance(v, str) and len(v) == 10:
            return datetime.strptime(v, DATE_FORMAT)
        # ③ ISO-8601 문자열도 허용하고 싶다면
        if isinstance(v, str):
            try:
                return datetime.fromisoformat(v)
            except ValueError:
                pass
        raise TypeError("잘못된 날짜 형식")

    # 날짜 필드 ISO 직렬화
    @field_serializer("날짜", when_used="json")
    def serialize_date(self, v: datetime) -> str:
        return v.isoformat()

    model_config = ConfigDict(
        populate_by_name=True,
        str_strip_whitespace=True,
    )

class Aud(Common):
    등락률: str = Field(alias="등략률")
    전일대비: float
    종가: float

class Chf(Common):
    등락률: str = Field(alias="등략률")
    전일대비: float
    종가: float

class Gbond3y(Common):
    등락률: str = Field(alias="등략률")
    전일대비: float
    종가: float

class Gold(Common):
    등락률: str = Field(alias="등략률")
    전일대비: float
    종가: float

class Kosdaq(Common):
    거래대금: int
    거래량: int
    등락률: str = Field(alias="등략률")
    전일비: float
    체결가: float

class Kospi(Common):
    거래대금: int
    거래량: int
    등락률: str = Field(alias="등략률")
    전일비: float
    체결가: float

class Silver(Common):
    등락률: str = Field(alias="등략률")
    전일대비: float
    종가: float

class Sp500(Common):
    고가: float
    시가: float
    저가: float
    전일대비: float
    종가: float

class Usdidx(Common):
    등락률: str = Field(alias="등략률")
    인덱스: float
    전일대비: float

class Usdkrw(Common):
    매매기준율: float
    송금받으실때: float = Field(alias="송금 받으실 때")
    송금보내실때: float = Field(alias="송금 보내실 때")
    전일대비: float
    현찰로사실때: float = Field(alias="현찰로 사실 때")
    현찰로파실때: float = Field(alias="현찰로 파실 때")

class Wti(Common):
    등락률: str = Field(alias="등략률")
    전일대비: float
    종가: float



