from google import genai
from google.genai.types import Tool, GenerateContentConfig, GoogleSearch
import json
import os
import json
import google.generativeai as gemini
from google.ai.generativelanguage_v1beta.types import content
import random

# define model
model_id = "gemini-2.0-flash"
# define tool
google_search_tool = Tool(
    google_search=GoogleSearch()
)

# define token


def configure_genai_api_key():
    tokens = ["Your token"]
    token = random.choice(tokens)
    client = genai.Client(api_key=token)
    return client


def configure_gemini_api_key():
    tokens = ["Your token"]
    token = random.choice(tokens)
    gemini.configure(api_key=token)


# check model
"""
# **分析條件**
請根據以下條件篩選符合的周線數據：

1. **具有前高點**：  
   - 在歷史數據中，曾經出現過較高的 `high` 值，並記錄該最高價與日期。  

2. **MA20 穿越條件 (`is_crossing_ma20`)**：  
   - 本週 K 線符合「**高點在上、低點在下、且 MA20 介於其中**」的形態：
     \[
     high > ma20 > low
     \]
   - **且** `close` 剛剛向上穿越 `ma20`，即：
     \[
     close_{本週} \geq ma20_{本週} \quad 且 \quad close_{前週} < ma20_{前週}
     \]
   - **若穿越已經發生在前 2 週及更早，則應標記為 `False`**。  

3. **MA20 靠近條件 (`is_near_ma20`)**：  
   - 若 `close` 與 `ma20` 的距離在 5% 內，則 `is_near_ma20 = True`：
     \[
     \left| \frac{close_{本週} - ma20_{本週}}{ma20_{本週}} \right| \leq 0.05
     \]
   - 若 `close` 與 `ma20` 的距離超過 5%，則 `False`。  

4. **買量訊號 (`buy_volume`)**：  
   - 若本週 `volume` 大於前 5 週的平均成交量，則 `buy_volume = True`：
     \[
     volume_{本週} > \frac{1}{5} \sum_{i=1}^{5} volume_{前 i 週}
     \]

5. **前高點 (`previous_high`)**：  
   - 在歷史數據中尋找最高的 `high` 值，並記錄其日期。  

---

## **輸入格式**
每個物件應包含以下資訊：

```json
{
  "id": 1,
  "date": "2024-02-23",
  "open": 105.5,
  "close": 110.0,
  "high": 115.0,
  "low": 108.0,
  "volume": 150000,
  "ma5": 109.0,
  "ma20": 109.5
}
## **輸出格式**
每個物件應包含以下資訊：

```json
{
  "is_crossing_ma20": true,
  "is_near_ma20": true,
  "buy_volume": true,
  "previous_high": {
    "price": 120.0,
    "date": "2023-12-15"
  }
}

"""
generation_config_check = {
    "temperature": 0.5,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_schema": content.Schema(
        type=content.Type.OBJECT,
        enum=[],
        required=["is_crossing_ma20", "is_near_ma20",
                  "buy_volume", "previous_high"],
        properties={
            "is_crossing_ma20": content.Schema(
                type=content.Type.BOOLEAN,
            ),
            "is_near_ma20": content.Schema(
                type=content.Type.BOOLEAN,
            ),
            "buy_volume": content.Schema(
                type=content.Type.BOOLEAN,
            ),
            "previous_high": content.Schema(
                type=content.Type.OBJECT,
                enum=[],
                required=["date", "price"],
                properties={
                    "date": content.Schema(
                        type=content.Type.STRING,
                    ),
                    "price": content.Schema(
                        type=content.Type.NUMBER,
                    ),
                },
            ),
        },
    ),
    "response_mime_type": "application/json",
}

check_model = gemini.GenerativeModel(
    model_name="gemini-2.0-flash",
    generation_config=generation_config_check,
    system_instruction="# **分析條件**\n請根據以下條件篩選符合的周線數據：\n\n1. **具有前高點**：  \n   - 在歷史數據中，曾經出現過較高的 `high` 值，並記錄該最高價與日期。  \n\n2. **MA20 穿越條件 (`is_crossing_ma20`)**：  \n   - 本週 K 線符合「**高點在上、低點在下、且 MA20 介於其中**」的形態：\n     \\[\n     high > ma20 > low\n     \\]\n   - **且** `close` 剛剛向上穿越 `ma20`，即：\n     \\[\n     close_{本週} \\geq ma20_{本週} \\quad 且 \\quad close_{前週} < ma20_{前週}\n     \\]\n   - **若穿越已經發生在前 2 週及更早，則應標記為 `False`**。  \n\n3. **MA20 靠近條件 (`is_near_ma20`)**：  \n   - 若 `close` 與 `ma20` 的距離在 5% 內，則 `is_near_ma20 = True`：\n     \\[\n     \\left| \\frac{close_{本週} - ma20_{本週}}{ma20_{本週}} \\right| \\leq 0.05\n     \\]\n   - 若 `close` 與 `ma20` 的距離超過 5%，則 `False`。  \n\n4. **買量訊號 (`buy_volume`)**：  \n   - 若本週 `volume` 大於前 5 週的平均成交量，則 `buy_volume = True`：\n     \\[\n     volume_{本週} > \\frac{1}{5} \\sum_{i=1}^{5} volume_{前 i 週}\n     \\]\n\n5. **前高點 (`previous_high`)**：  \n   - 在歷史數據中尋找最高的 `high` 值，並記錄其日期。  \n\n---\n\n## **輸入格式**\n每個物件應包含以下資訊：\n\n```json\n{\n  \"id\": 1,\n  \"date\": \"2024-02-23\",\n  \"open\": 105.5,\n  \"close\": 110.0,\n  \"high\": 115.0,\n  \"low\": 108.0,\n  \"volume\": 150000,\n  \"ma5\": 109.0,\n  \"ma20\": 109.5\n}\n## **輸出格式**\n每個物件應包含以下資訊：\n\n```json\n{\n  \"is_crossing_ma20\": true,\n  \"is_near_ma20\": true,\n  \"buy_volume\": true,\n  \"previous_high\": {\n    \"price\": 120.0,\n    \"date\": \"2023-12-15\"\n  }\n}",
)

check_model_session = check_model.start_chat()

# result model
"""
根據提供的 **週線數據 (`week_data`)**、**均線狀態 (`week_check_ma`)** 及 **市場新聞 (`news`)**，預測未來股價趨勢，並計算 **市場評級（1~100）**。

## **市場評級計算方式**
市場評級初始分數為 **50 分（中性）**，並根據以下條件加分或扣分：

- **技術面：**
  - `is_crossing_ma20 = True`（股價剛剛突破 MA20） → **+20**
  - `is_near_ma20 = True`（股價接近 MA20） → **+10**
  - `buy_volume = True`（成交量大於前 5 週均量） → **+20**
  - 突破前高 (`previous_high.price`) → **+15**
  - **低於 MA20 回落** → **-20**
  - **成交量低迷（低於前 5 週均量）** → **-15**

- **消息面：**
  - **新聞正向 (`news` 包含 "利好")** → **+15**
  - **新聞負向 (`news` 包含 "利空")** → **-15**

評分計算：
```python
score = 50  # 初始分數

# 加分條件
if is_crossing_ma20: score += 20
if is_near_ma20: score += 10
if buy_volume: score += 20
if week_check_ma["previous_high"]["price"] and week_data[-1]["close"] > week_check_ma["previous_high"]["price"]:
    score += 15
if "利好" in news: score += 15

# 扣分條件
if week_data[-1]["close"] < week_data[-1]["ma20"]: score -= 20
if not buy_volume: score -= 15
if "利空" in news: score -= 15

# 限制分數範圍在 1 ~ 100
score = max(1, min(score, 100))
---
## **輸入格式**
```json
{
  "week_data": [
    {
      "id": 1,
      "date": "2024-02-23",
      "open": 105.5,
      "close": 110.0,
      "high": 115.0,
      "low": 108.0,
      "volume": 150000,
      "ma5": 109.0,
      "ma20": 109.5
    }........
  ],
  "week_check_ma": {
    "buy_volume": false,
    "is_crossing_ma20": false,
    "is_near_ma20": false,
    "previous_high": {
      "date": "",
      "price": 100
    }
  },
  "news": "市場樂觀，政策利好"
}
---
## **輸出格式**
```json
{
  "score": number,
  "reason": string 說明加減分,
}
"""
generation_config_result = {
    "temperature": 0.4,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_schema": content.Schema(
        type=content.Type.OBJECT,
        enum=[],
        required=["score", "reason"],
        properties={
            "score": content.Schema(
                type=content.Type.NUMBER,
            ),
            "reason": content.Schema(
                type=content.Type.STRING,
            ),
        },
    ),
    "response_mime_type": "application/json",
}
result_model = gemini.GenerativeModel(
    model_name="gemini-2.0-flash",
    generation_config=generation_config_result,
    system_instruction="根據提供的 **週線數據 (`week_data`)**、**均線狀態 (`week_check_ma`)** 及 **市場新聞 (`news`)**，預測未來股價趨勢，並計算 **市場評級（1~100）**。\n\n## **市場評級計算方式**\n市場評級初始分數為 **50 分（中性）**，並根據以下條件加分或扣分：\n\n- **技術面：**\n  - `is_crossing_ma20 = True`（股價剛剛突破 MA20） → **+20**\n  - `is_near_ma20 = True`（股價接近 MA20） → **+10**\n  - `buy_volume = True`（成交量大於前 5 週均量） → **+20**\n  - 突破前高 (`previous_high.price`) → **+15**\n  - **低於 MA20 回落** → **-20**\n  - **成交量低迷（低於前 5 週均量）** → **-15**\n\n- **消息面：**\n  - **新聞正向 (`news` 包含 \"利好\")** → **+15**\n  - **新聞負向 (`news` 包含 \"利空\")** → **-15**\n\n評分計算：\n```python\nscore = 50  # 初始分數\n\n# 加分條件\nif is_crossing_ma20: score += 20\nif is_near_ma20: score += 10\nif buy_volume: score += 20\nif week_check_ma[\"previous_high\"][\"price\"] and week_data[-1][\"close\"] > week_check_ma[\"previous_high\"][\"price\"]:\n    score += 15\nif \"利好\" in news: score += 15\n\n# 扣分條件\nif week_data[-1][\"close\"] < week_data[-1][\"ma20\"]: score -= 20\nif not buy_volume: score -= 15\nif \"利空\" in news: score -= 15\n\n# 限制分數範圍在 1 ~ 100\nscore = max(1, min(score, 100))\n---\n## **輸入格式**\n```json\n{\n  \"week_data\": [\n    {\n      \"id\": 1,\n      \"date\": \"2024-02-23\",\n      \"open\": 105.5,\n      \"close\": 110.0,\n      \"high\": 115.0,\n      \"low\": 108.0,\n      \"volume\": 150000,\n      \"ma5\": 109.0,\n      \"ma20\": 109.5\n    }........\n  ],\n  \"week_check_ma\": {\n    \"buy_volume\": false,\n    \"is_crossing_ma20\": false,\n    \"is_near_ma20\": false,\n    \"previous_high\": {\n      \"date\": \"\",\n      \"price\": 100\n    }\n  },\n  \"news\": \"市場樂觀，政策利好\"\n}\n---\n## **輸出格式**\n```json\n{\n  \"score\": number,\n  \"reason\": string 說明加減分,\n}\n",
)
result_model_session = result_model.start_chat()


def predict_model(input):
    global check_model_session
    configure_gemini_api_key()
    output = check_model_session.send_message(input)
    output = output.text
    return output


def result_model(input):
    global result_model_session
    configure_gemini_api_key()
    output = result_model_session.send_message(input)
    output = output.text
    return output


def search_model(input):
    client = configure_genai_api_key()
    search_model = client.models.generate_content(
        model=model_id,
        contents=input,
        config=GenerateContentConfig(
            tools=[google_search_tool],
            response_modalities=["TEXT"],
        )
    )

    results = {
        "texts": [],
        "urls": []
    }

    for candidate in search_model.candidates:
        # Extract text content
        for part in candidate.content.parts:
            results["texts"].append(part.text)

        # Extract URLs and titles
        for chunk in candidate.grounding_metadata.grounding_chunks:
            results["urls"].append({
                "title": chunk.web.title,
                "url": chunk.web.uri
            })
    print(results)
    return results
