import os
import json
import google.generativeai as genai
from google.ai.generativelanguage_v1beta.types import content
import random


def configure_genai_api_key():
    global token
    tokens = ["AIzaSyAmbyz82j6ORj6eto1lNJg30sNTvLi_Eag",
              "AIzaSyBWhebIzg0ngek1HFxSFtelDcwulPdnPMs",
              "AIzaSyDVacoH99_M6IH7jyU4oNOxDNOKFKLL3qQ"]
    token = random.choice(tokens)
    genai.configure(api_key=token)


# check model
"""
### **分析條件**
請根據以下條件篩選符合的周線數據：

1. **具有前高點**：前期股價曾達到較高水平。
2. **當前周線股價剛穿越 MA20，或是即將穿越 MA20**。
3. **若已經是前2根時出現穿越，則is_crossing_ma20、is_near_ma20都依該是false

---

### **輸入格式**
每個物件應包含以下資訊：
- `id`：識別碼
- `date`：日期（字串格式）
- `open`：開盤價
- `close`：收盤價
- `high`：最高價
- `low`：最低價
- `volume`：成交量
- `ma5`：5 周均線
- `ma20`：20 周均線

---

### **輸出格式**
每個物件應包含以下資訊：

#### **趨勢判斷**
- `is_crossing_ma20`（boolean）：若 `close` 剛剛穿越 `ma20`，則為 `true`，否則為 `false`。
- `is_near_ma20`（boolean）：若 `close` 接近 `ma20`（例如相差 1% 以內），則為 `true`，否則為 `false`。
- `previous_high`（float）：該標的的前高點股價。
"""
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_schema": content.Schema(
        type=content.Type.OBJECT,
        enum=[],
        required=["is_crossing_ma20", "is_near_ma20", "previous_high"],
        properties={
            "is_crossing_ma20": content.Schema(
                type=content.Type.BOOLEAN,
            ),
            "is_near_ma20": content.Schema(
                type=content.Type.BOOLEAN,
            ),
            "previous_high": content.Schema(
                type=content.Type.NUMBER,
            ),
        },
    ),
    "response_mime_type": "application/json",
}

check_model = genai.GenerativeModel(
    model_name="gemini-2.0-flash",
    generation_config=generation_config,
    system_instruction="語言: 中文繁體\n職位: 你是一個股票分析師\n職責: 分析傳入的資料\n分析方法: 請根據以下條件篩選符合的周線數據\n- 1. **具有前高點**：前期股價曾達到較高水平。\n- 2. **當前周線股價剛穿越 MA20，或是即將穿越 MA20**。\n- 3. **若已經是前2根時出現穿越，則is_crossing_ma20、is_near_ma20都依該是false\n---\n輸入: weeks[week,week,week]，weeks是json array，week是json object\n每個物件應包含以下資訊：\n- `id`：識別碼\n- `date`：日期（字串格式）\n- `open`：開盤價\n- `close`：收盤價\n- `high`：最高價\n- `low`：最低價\n- `volume`：成交量\n- `ma5`：5 周均線\n- `ma20`：20 周均線\n---\n### **輸出格式**\n每個物件應包含以下資訊：\n\n#### **趨勢判斷**\n- `is_crossing_ma20`（boolean）：若 `close` 剛剛穿越 `ma20`，則為 `true`，否則為 `false`。\n- `is_near_ma20`（boolean）：若 `close` 接近 `ma20`（例如相差 1% 以內），則為 `true`，否則為 `false`。\n- `previous_high`（float）：該標的的前高點股價。",
)

check_model_session = check_model.start_chat()


def predict_model(input):
    global check_model_session
    configure_genai_api_key()
    output = check_model_session.send_message(input)
    output = output.text
    return output


def search_model(input):
    pass
