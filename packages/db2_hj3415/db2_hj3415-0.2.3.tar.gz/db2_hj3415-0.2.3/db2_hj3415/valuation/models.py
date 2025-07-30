from typing import Any

from pydantic import BaseModel, Field, field_validator, field_serializer, ConfigDict, model_validator, SerializationInfo
from datetime import datetime
import math

from utils_hj3415 import tools


class RedData(BaseModel):
    id: str | None = Field(default=None, alias="_id")
    코드: str
    날짜: datetime | None = Field(default=None)
    종목명: str

    사업가치: float | None
    지배주주당기순이익: float | None
    expect_earn: float | None

    재산가치: float | None
    유동자산: float | None
    유동부채: float | None
    투자자산: float | None
    투자부동산: float | None

    부채평가: float | None
    발행주식수: int | None

    자료제출일: list[str] | None = Field(default=None)
    주가: float | None
    red_price: float | None
    score: int | None

    @model_validator(mode='before')
    @classmethod
    def replace_nan_with_none(cls, values: dict) -> dict:
        return {
            k: (None if isinstance(v, float) and math.isnan(v) else v)
            for k, v in values.items()
        }

    @field_serializer("날짜")
    def serialize_날짜(self, value: datetime, info: SerializationInfo) -> str | datetime:
        # JSON 응답용일 때만 문자열로 직렬화
        if info.mode == 'json':
            return value.isoformat()
        return value

    @field_validator("코드")
    @classmethod
    def validate_코드(cls, v):
        if not tools.is_6digit(v):
            raise ValueError(f"code는 6자리 숫자형 문자열이어야 합니다. (입력값: {v})")
        return v

    model_config = ConfigDict(
        populate_by_name=True,
        str_strip_whitespace=True,
    )


class Evaluation(BaseModel):
    최근값: float | None = Field(default=None)
    시계열: dict[str, float] = Field(default_factory=dict)
    평가결과: dict[str, Any] = Field(default_factory=dict)
    model_config = ConfigDict(
        extra="allow"
    )


class MilData(BaseModel):
    id: str | None = Field(default=None, alias="_id")
    코드: str
    날짜: datetime | None = Field(default=None)
    종목명: str

    주주수익률: float | None
    이익지표: float | None

    # 투자수익률
    ROIC: Evaluation
    ROE: Evaluation
    ROA: Evaluation

    # 가치지표
    FCF: Evaluation
    PFCF: Evaluation
    PCR: Evaluation

    @model_validator(mode='before')
    @classmethod
    def replace_nan_with_none(cls, values: dict) -> dict:
        return {
            k: (None if isinstance(v, float) and math.isnan(v) else v)
            for k, v in values.items()
        }

    @field_serializer("날짜")
    def serialize_날짜(self, value: datetime, info: SerializationInfo) -> str | datetime:
        # JSON 응답용일 때만 문자열로 직렬화
        if info.mode == 'json':
            return value.isoformat()
        return value

    @field_validator("코드")
    @classmethod
    def validate_코드(cls, v):
        if not tools.is_6digit(v):
            raise ValueError(f"code는 6자리 숫자형 문자열이어야 합니다. (입력값: {v})")
        return v

    model_config = ConfigDict(
        populate_by_name=True,
        str_strip_whitespace=True,
    )


class BlueData(BaseModel):
    id: str | None = Field(default=None, alias="_id")
    코드: str
    날짜: datetime | None = Field(default=None)
    종목명: str

    유동비율: float

    재고자산회전율: Evaluation
    이자보상배율: Evaluation
    순운전자본회전율: Evaluation | None
    순부채비율: Evaluation

    자료제출일: list[str] | None = Field(default=None)

    @model_validator(mode='before')
    @classmethod
    def replace_nan_with_none(cls, values: dict) -> dict:
        return {
            k: (None if isinstance(v, float) and math.isnan(v) else v)
            for k, v in values.items()
        }

    @field_serializer("날짜")
    def serialize_날짜(self, value: datetime, info: SerializationInfo) -> str | datetime:
        # JSON 응답용일 때만 문자열로 직렬화
        if info.mode == 'json':
            return value.isoformat()
        return value

    @field_validator("코드")
    @classmethod
    def validate_코드(cls, v):
        if not tools.is_6digit(v):
            raise ValueError(f"code는 6자리 숫자형 문자열이어야 합니다. (입력값: {v})")
        return v

    model_config = ConfigDict(
        populate_by_name=True,
        str_strip_whitespace=True,
    )


class GrowthData(BaseModel):
    id: str | None = Field(default=None, alias="_id")
    코드: str
    날짜: datetime | None = Field(default=None)
    종목명: str

    매출액증가율: Evaluation

    @model_validator(mode='before')
    @classmethod
    def replace_nan_with_none(cls, values: dict) -> dict:
        return {
            k: (None if isinstance(v, float) and math.isnan(v) else v)
            for k, v in values.items()
        }

    @field_serializer("날짜")
    def serialize_날짜(self, value: datetime, info: SerializationInfo) -> str | datetime:
        # JSON 응답용일 때만 문자열로 직렬화
        if info.mode == 'json':
            return value.isoformat()
        return value

    @field_validator("코드")
    @classmethod
    def validate_코드(cls, v):
        if not tools.is_6digit(v):
            raise ValueError(f"code는 6자리 숫자형 문자열이어야 합니다. (입력값: {v})")
        return v

    model_config = ConfigDict(
        populate_by_name=True,
        str_strip_whitespace=True,
    )