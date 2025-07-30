from bson import ObjectId
from pydantic import BaseModel, Field, field_serializer, ConfigDict, field_validator
from datetime import datetime
from . import DATE_FORMAT

class Common(BaseModel):
    id: str | None = Field(default=None, alias="_id")
    코드: str
    날짜: datetime

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

    @field_validator("id", mode="before")
    @classmethod
    def cast_objectid(cls, v):
        return str(v) if isinstance(v, ObjectId) else v

    @field_serializer("날짜")
    def serialize_날짜(self, value: datetime) -> str:
        return value.isoformat()

    model_config = ConfigDict(
        populate_by_name=True,
        str_strip_whitespace=True,
    )



class CodeName(BaseModel):
    코드: str
    종목명: str | None

class C101(Common):
    종목명: str | None
    bps: int | None
    eps: int | None
    pbr: float | None
    per: float | None
    개요: str | None
    거래대금: int | None
    거래량: int | None
    발행주식: int | None
    배당수익률: float | None
    베타52주: float | None
    수익률: float | None
    수익률1M: float | None
    수익률1Y: float | None
    수익률3M: float | None
    수익률6M: float | None
    시가총액: int | None
    업종: str | None
    업종per: float | None
    외국인지분율: float | None
    유동비율: float | None
    전일대비: int | None

    주가: int | None
    최고52: int | None
    최저52: int | None


class 항목값y(BaseModel):
    항목: str
    전년대비: float | None
    전년대비_1: float | None = Field(default=None, alias="전년대비 1")

    model_config = ConfigDict(
        populate_by_name=True,
        extra="allow"
    )

class 항목값q(BaseModel):
    항목: str
    전분기대비: float | None

    model_config = ConfigDict(extra="allow")


class C103(Common):
    손익계산서q: list[항목값q]
    손익계산서y: list[항목값y]
    재무상태표q: list[항목값q]
    재무상태표y: list[항목값y]
    현금흐름표q: list[항목값q]
    현금흐름표y: list[항목값y]


class C104(Common):
    수익성y: list[항목값y] | None = None
    성장성y: list[항목값y] | None = None
    안정성y: list[항목값y] | None = None
    활동성y: list[항목값y] | None = None
    가치분석y: list[항목값y] | None = None

    수익성q: list[항목값q] | None = None
    성장성q: list[항목값q] | None = None
    안정성q: list[항목값q] | None = None
    활동성q: list[항목값q] | None = None
    가치분석q: list[항목값q] | None = None


class 기업데이터(BaseModel):
    항목: str
    항목2: str

    model_config = ConfigDict(extra="allow")


class C106(Common):
    q: list[기업데이터]
    y: list[기업데이터]


class C108(Common):
    제목: str | None = None
    내용: list[str] | None = None
    목표가: int | None = None
    분량: str | None = None
    작성자: str | None = None
    제공처: str | None = None
    투자의견: str | None = None

    # ▸ 핵심: str 단일 입력을 리스트로 자동 변환
    @field_validator("내용", mode="before")
    @classmethod
    def _normalize_content(cls, v):
        if v is None:
            return None  # 그대로 둡니다.
        if isinstance(v, str):
            return [v]  # 단일 문자열 → 리스트로 래핑
        if isinstance(v, list):
            # 요소가 문자열이 아니면 문자열로 캐스팅하거나 에러를 던질 수도 있습니다.
            return [str(item) for item in v]
        raise TypeError("내용 필드는 str 이나 str 리스트여야 합니다.")


class Dart(BaseModel):
    id: str | None = Field(default=None, alias="_id")
    stock_code: str | None= None # 종목 코드 (6자리)
    rcept_dt: datetime | None = None # 접수 일자 (YYYYMMDD)

    corp_cls: str  # 기업 구분 (예: 'K', 'Y', 'N')
    corp_code: str  # 고유 회사 코드 (8자리)
    corp_name: str  # 회사 이름
    flr_nm: str  # 제출자 (예: '코스닥시장본부')
    rcept_no: str  # 접수 번호
    report_nm: str  # 보고서 이름
    rm: str  # 비고 (예: '코')

    '''
    클라이언트 ── "20250701" ──▶ parse_date() ──▶ datetime(2025,7,1) ──▶ 모델 저장
                                                             │
                       model_dump() / JSON 응답               ▼
    클라이언트 ◀─ "2025-07-01T00:00:00" ◀─ serialize_date() ◀─ datetime
    '''

    @field_validator("id", mode="before")
    @classmethod
    def cast_objectid(cls, v):
        return str(v) if isinstance(v, ObjectId) else v

    @field_validator("rcept_dt", mode="before")
    @classmethod
    def parse_date(cls, v):
        # ① 이미 datetime 이면 그대로 통과
        if isinstance(v, datetime):
            return v
        # ② YYYYMMDD 형태의 순수 8자리 문자열
        if isinstance(v, str) and len(v) == 8 and v.isdigit():
            return datetime.strptime(v, "%Y%m%d")
        # ③ ISO-8601 문자열도 허용하고 싶다면
        if isinstance(v, str):
            try:
                return datetime.fromisoformat(v)
            except ValueError:
                pass
        raise TypeError("잘못된 rcept_dt 형식")

    # 날짜 필드 ISO 직렬화
    @field_serializer("rcept_dt", when_used="json")
    def serialize_date(self, v: datetime) -> str:
        return v.isoformat()

    model_config = ConfigDict(
        populate_by_name=True,
        str_strip_whitespace=True,
    )