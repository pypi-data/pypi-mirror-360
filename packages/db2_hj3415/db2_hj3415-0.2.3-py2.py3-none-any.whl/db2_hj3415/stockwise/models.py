from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict

class User(BaseModel):
    id: str | None = Field(default=None, alias="_id")
    username: str
    nickname: str | None
    email: EmailStr
    password_hash: str
    created_at: datetime = Field(default_factory=datetime.now)
    is_active: bool = False
    roles: list[str] = Field(default_factory=lambda: ["user"])

    model_config = ConfigDict(populate_by_name=True)

class Portfolio(BaseModel):
    id: str | None = Field(default=None, alias="_id")
    user_id: str  # MongoDB의 ObjectId를 str로 저장
    코드: str
    종목명: str | None = None
    purchase_date: datetime
    purchase_price: float
    quantity: int

    target_price: float | None = None
    stop_loss_price: float | None = None
    memo: str | None = None
    tags: list[str] | None = []
    is_favorite: bool = False
    last_updated: datetime | None = None

    model_config = ConfigDict(populate_by_name=True)

