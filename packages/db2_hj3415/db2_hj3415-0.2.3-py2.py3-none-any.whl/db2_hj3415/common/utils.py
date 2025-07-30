# 자주 쓰는 간단한 유틸 함수
import pandas as pd
import numpy as np

def df_to_dict_replace_nan(df: pd.DataFrame) -> list[dict]:
    # NaN → None으로 변환
    return df.replace({np.nan: None}).to_dict(orient="records")

import json
from bson import json_util
from pydantic import BaseModel

def pretty_print(obj):
    def convert(o):
        if isinstance(o, BaseModel):
            return o.model_dump(by_alias=True)
        if isinstance(o, dict):
            return {k: convert(v) for k, v in o.items()}
        if isinstance(o, list):
            return [convert(v) for v in o]
        return o  # 기본값 (예: str, int, float 등)

    data = convert(obj)

    print(json.dumps(data, indent=2, ensure_ascii=False, default=json_util.default))