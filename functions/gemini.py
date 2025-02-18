import os
import json
import google.generativeai as genai
from google.ai.generativelanguage_v1beta.types import content


def configure_genai_api_key(api_key):
    os.environ["GEMINI_API_KEY"] = api_key
    genai.configure(api_key=api_key)


# create the model 1
"""
    你是一個專業的股票分析師，根據過去 30 天的股票數據，分析是否出現買入訊號。數據包含：
    0. Prompt輸入要求
    - "你是一個專業的股票分析師，根據過去 30 天的股票數據，分析是否出現買入訊號。並根據給予的數據進行條件分析、判斷"
    - "你預測的不正確 {{reason}}，請重新預測。"
    1. 開盤價 (open)
    2. 收盤價 (close)
    3. 最高價 (high)
    4. 最低價 (low)
    5. 成交量 (volume)
    6. MACD 指標：
    - ``macd`` (快線 - 慢線)
    - `macd_signal` (MACD 信號線)
    - `macd_hist` (MACD 柱狀圖)
    7. KDJ 指標：
    - `K`
    - `D`
    - `J`

    請根據以下條件進行判斷：
    1. **MACD 黃金交叉**：`macd` 上穿 `macd_signal`
    2. **KDJ 黃金交叉**：`K` 線上穿 `D` 線
    3. **成交量是否放大**：最近 3 天的成交量均值是否高於過去 30 天的成交量均值
    4. **是否為合適的買點**：
    - 當 `MACD` 黃金交叉、`KDJ` 黃金交叉且成交量放大時，則判定為合適的買點
    - 如果任一條件不滿足，則判定為不適合買入

    5. **適合的入場價格**：
    - 如果 `buy_signal = true`，則 `entry_price` 建議為當日收盤價 (`close`)
    - 如果 `buy_signal = false`，則 `entry_price` 仍提供當日收盤價，但需附上不建議買入的原因

    請輸出 JSON 格式結果，包含以下欄位：
    - `"macd_cross"`: 是否發生 MACD 黃金交叉 (true/false)
    - `"kdj_cross"`: 是否發生 KDJ 黃金交叉 (true/false)
    - `"volume_increase"`: 是否成交量放大 (true/false)
    - `"buy_signal"`: 是否為合適的買點 (true/false)
    - `"entry_price"`: 建議的買入價格 (當日收盤價或計算出的進場價)
    - `"reason"`: 文字說明為何適合/不適合買入，包含 MACD、KDJ、成交量的判斷邏輯

    ---

    ### **JSON 輸出範例**
    #### **適合買入的情況**
    ```json
    {
    "macd_cross": true,
    "kdj_cross": true,
    "volume_increase": true,
    "buy_signal": true,
    "entry_price": 120.5,
    "reason": "MACD 出現黃金交叉 (macd 上穿 macd_signal)，KDJ 亦出現黃金交叉 (K 上穿 D)，且成交量較過去 30 天均量提升，確認市場有資金流入，建議買入，入場價格為當日收盤價 120.5。"
    }

    ### **JSON 輸出範例**
    #### **適合買入的情況**
    ```json
    {
    "macd_cross": true,
    "kdj_cross": false,
    "volume_increase": true,
    "buy_signal": false,
    "entry_price": 118.3,
    "reason": "雖然 MACD 出現黃金交叉 (macd 上穿 macd_signal)，且成交量放大，但 KDJ 尚未形成黃金交叉 (K 未上穿 D)，顯示短線動能不足，仍有可能回調，因此不建議買入，當日收盤價為 118.3。"
    } or {
    "macd_cross": true,
    "kdj_cross": true,
    "volume_increase": false,
    "buy_signal": false,
    "entry_price": 125.7,
    "reason": "MACD 及 KDJ 均已形成黃金交叉，技術面偏多，但成交量未見明顯增加，顯示市場缺乏資金支持，可能是假突破，當日收盤價為 125.7，暫不建議進場。"
    }
"""
generation_config1 = {
    "temperature": 0.5,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_schema": content.Schema(
        type=content.Type.OBJECT,
        enum=[],
        required=["macd_cross", "kdj_cross", "volume_increase",
                  "buy_signal", "entry_price", "reason"],
        properties={
            "macd_cross": content.Schema(
                type=content.Type.BOOLEAN,
            ),
            "kdj_cross": content.Schema(
                type=content.Type.BOOLEAN,
            ),
            "volume_increase": content.Schema(
                type=content.Type.BOOLEAN,
            ),
            "buy_signal": content.Schema(
                type=content.Type.BOOLEAN,
            ),
            "entry_price": content.Schema(
                type=content.Type.NUMBER,
            ),
            "reason": content.Schema(
                type=content.Type.STRING,
            ),
        },
    ),
    "response_mime_type": "application/json",
}

model1 = genai.GenerativeModel(
    model_name="gemini-2.0-flash",
    generation_config=generation_config1,
    system_instruction="你是一個專業的股票分析師，根據過去 30 天的股票數據，分析是否出現買入訊號。數據包含：\n0. Prompt輸入要求\n   - \"你是一個專業的股票分析師，根據過去 30 天的股票數據，分析是否出現買入訊號。並根據給予的數據進行條件分析、判斷\"\n   - \"你預測的不正確 {{reason}}，請重新預測。\"\n1. 開盤價 (open)\n2. 收盤價 (close)\n3. 最高價 (high)\n4. 最低價 (low)\n5. 成交量 (volume)\n6. MACD 指標：\n   - `macd` (快線 - 慢線)\n   - `macd_signal` (MACD 信號線)\n   - `macd_hist` (MACD 柱狀圖)\n7. KDJ 指標：\n   - `K`\n   - `D`\n   - `J`\n\n請根據以下條件進行判斷：\n1. **MACD 黃金交叉**：`macd` 上穿 `macd_signal`\n2. **KDJ 黃金交叉**：`K` 線上穿 `D` 線\n3. **成交量是否放大**：最近 3 天的成交量均值是否高於過去 30 天的成交量均值\n4. **是否為合適的買點**：\n   - 當 `MACD` 黃金交叉、`KDJ` 黃金交叉且成交量放大時，則判定為合適的買點\n   - 如果任一條件不滿足，則判定為不適合買入\n\n5. **適合的入場價格**：\n   - 如果 `buy_signal = true`，則 `entry_price` 建議為當日收盤價 (`close`)\n   - 如果 `buy_signal = false`，則 `entry_price` 仍提供當日收盤價，但需附上不建議買入的原因\n\n請輸出 JSON 格式結果，包含以下欄位：\n- `\"macd_cross\"`: 是否發生 MACD 黃金交叉 (true/false)\n- `\"kdj_cross\"`: 是否發生 KDJ 黃金交叉 (true/false)\n- `\"volume_increase\"`: 是否成交量放大 (true/false)\n- `\"buy_signal\"`: 是否為合適的買點 (true/false)\n- `\"entry_price\"`: 建議的買入價格 (當日收盤價或計算出的進場價)\n- `\"reason\"`: 文字說明為何適合/不適合買入，包含 MACD、KDJ、成交量的判斷邏輯\n\n---\n\n### **JSON 輸出範例**\n#### **適合買入的情況**\n```json\n{\n  \"macd_cross\": true,\n  \"kdj_cross\": true,\n  \"volume_increase\": true,\n  \"buy_signal\": true,\n  \"entry_price\": 120.5,\n  \"reason\": \"MACD 出現黃金交叉 (macd 上穿 macd_signal)，KDJ 亦出現黃金交叉 (K 上穿 D)，且成交量較過去 30 天均量提升，確認市場有資金流入，建議買入，入場價格為當日收盤價 120.5。\"\n}\n\n### **JSON 輸出範例**\n#### **適合買入的情況**\n```json\n{\n  \"macd_cross\": true,\n  \"kdj_cross\": false,\n  \"volume_increase\": true,\n  \"buy_signal\": false,\n  \"entry_price\": 118.3,\n  \"reason\": \"雖然 MACD 出現黃金交叉 (macd 上穿 macd_signal)，且成交量放大，但 KDJ 尚未形成黃金交叉 (K 未上穿 D)，顯示短線動能不足，仍有可能回調，因此不建議買入，當日收盤價為 118.3。\"\n} or {\n  \"macd_cross\": true,\n  \"kdj_cross\": true,\n  \"volume_increase\": false,\n  \"buy_signal\": false,\n  \"entry_price\": 125.7,\n  \"reason\": \"MACD 及 KDJ 均已形成黃金交叉，技術面偏多，但成交量未見明顯增加，顯示市場缺乏資金支持，可能是假突破，當日收盤價為 125.7，暫不建議進場。\"\n}\n\n",
)
history1 = []
chat_session1 = model1.start_chat(history=history1)
# create the model 2
"""
    你是一個專業的股票交易評估師，你的任務是根據 **額外 5 天的數據**，驗證 **過去 30 天的分析結果是否準確**。
    你需要評估上一個模型 (`Prompt 1`) 依照30天預測的輸出是否與實際市場走勢相符，並給出 1~10 分的評價。

    **輸入數據包含：**
    1. **過去 35 天的股票數據**（包含開盤價、收盤價、最高價、最低價、成交量、MACD、KDJ 等）
    2. **上一個預測的 JSON 輸出 (`Prompt 1`)**，包含：
    - `macd_cross`
    - `kdj_cross`
    - `volume_increase`
    - `buy_signal`
    - `entry_price`
    - `reason`
    3. **驗證標準**：
    - 若 `buy_signal = true`，則評估未來 5 天的最高價是否高於 `entry_price` 至少 **3%**，若達標則視為成功。
    - 若 `buy_signal = false`，則評估未來 5 天的最低價是否 **未曾低於 entry_price 3%**，若達標則視為成功。
    - 若 MACD/KDJ 指標走勢驗證了前一個判斷，則加分。
    - 若成交量在預測後確實放大，則加分。

    ### **JSON 輸出格式**
    請輸出 JSON，包含以下欄位：
    - `"previous_prediction"`: **上一個預測的 JSON**（原封不動回傳）
    - `"score"`: 1~10 分的評估結果
    - `"pass"`: `true/false`，若 `score > 8` 則為 `true`
    - `"validation_reason"`: 解釋評分的原因
    - `"adjusted_entry_price"`: 若 `pass = false`，則提供修正後的進場價格，否則與原始 `entry_price` 相同
    - `"recommend_reanalysis"`: 若 `pass = false` 則為 `true`，表示應重新評估交易機會

    ---

    ### **JSON 輸出範例**
    #### **預測成功（通過驗證）**
    ```json
    {
    "previous_prediction": {
        "macd_cross": true,
        "kdj_cross": true,
        "volume_increase": true,
        "buy_signal": true,
        "entry_price": 120.5,
        "reason": "MACD、KDJ 黃金交叉，且成交量放大，市場資金流入，適合買入。"
    },
    "score": 9,
    "pass": true,
    "validation_reason": "預測後 5 天內，股價最高達到 125.0，漲幅超過 3%，符合預測，判定通過。",
    "adjusted_entry_price": 120.5,
    "recommend_reanalysis": false
    }
    #### **預測失敗（需要重新分析）**
    ```json
    {
    "previous_prediction": {
        "macd_cross": true,
        "kdj_cross": true,
        "volume_increase": true,
        "buy_signal": true,
        "entry_price": 120.5,
        "reason": "MACD、KDJ 黃金交叉，且成交量放大，市場資金流入，適合買入。"
    },
    "score": 6,
    "pass": false,
    "validation_reason": "買入後 5 天內，股價最高僅達到 122.0，未超過 3% 漲幅，且成交量未進一步放大，應考慮當日是賣多、賣少、買多、買少這種基本的依據判斷。",
    "adjusted_entry_price": 118.0,
    "recommend_reanalysis": true
    }
"""
generation_config2 = {
    "temperature": 0.5,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_schema": content.Schema(
        type=content.Type.OBJECT,
        enum=[],
        required=["previous_prediction", "score", "pass", "validation_reason",
                  "adjusted_entry_price", "recommend_reanalysis"],
        properties={
            "previous_prediction": content.Schema(
                type=content.Type.OBJECT,
                enum=[],
                required=["macd_cross", "kdj_cross", "volume_increase",
                          "buy_signal", "entry_price", "reason"],
                properties={
                    "macd_cross": content.Schema(
                        type=content.Type.BOOLEAN,
                    ),
                    "kdj_cross": content.Schema(
                        type=content.Type.BOOLEAN,
                    ),
                    "volume_increase": content.Schema(
                        type=content.Type.BOOLEAN,
                    ),
                    "buy_signal": content.Schema(
                        type=content.Type.BOOLEAN,
                    ),
                    "entry_price": content.Schema(
                        type=content.Type.NUMBER,
                    ),
                    "reason": content.Schema(
                        type=content.Type.STRING,
                    ),
                },
            ),
            "score": content.Schema(
                type=content.Type.INTEGER,
            ),
            "pass": content.Schema(
                type=content.Type.BOOLEAN,
            ),
            "validation_reason": content.Schema(
                type=content.Type.STRING,
            ),
            "adjusted_entry_price": content.Schema(
                type=content.Type.NUMBER,
            ),
            "recommend_reanalysis": content.Schema(
                type=content.Type.BOOLEAN,
            ),
        },
    ),
    "response_mime_type": "application/json",
}

model2 = genai.GenerativeModel(
    model_name="gemini-2.0-flash",
    generation_config=generation_config2,
    system_instruction="你是一個專業的股票交易評估師，你的任務是根據 **額外 5 天的數據**，驗證 **過去 30 天的分析結果是否準確**。  \n你需要評估上一個模型 (`Prompt 1`) 依照30天預測的輸出是否與實際市場走勢相符，並給出 1~10 分的評價。  \n\n**輸入數據包含：**  \n1. **過去 35 天的股票數據**（包含開盤價、收盤價、最高價、最低價、成交量、MACD、KDJ 等）  \n2. **上一個預測的 JSON 輸出 (`Prompt 1`)**，包含：\n   - `macd_cross`\n   - `kdj_cross`\n   - `volume_increase`\n   - `buy_signal`\n   - `entry_price`\n   - `reason`\n3. **驗證標準**：\n   - 若 `buy_signal = true`，則評估未來 5 天的最高價是否高於 `entry_price` 至少 **3%**，若達標則視為成功。\n   - 若 `buy_signal = false`，則評估未來 5 天的最低價是否 **未曾低於 entry_price 3%**，若達標則視為成功。\n   - 若 MACD/KDJ 指標走勢驗證了前一個判斷，則加分。\n   - 若成交量在預測後確實放大，則加分。\n\n### **JSON 輸出格式**\n請輸出 JSON，包含以下欄位：\n- `\"previous_prediction\"`: **上一個預測的 JSON**（原封不動回傳）\n- `\"score\"`: 1~10 分的評估結果\n- `\"pass\"`: `true/false`，若 `score > 8` 則為 `true`\n- `\"validation_reason\"`: 解釋評分的原因\n- `\"adjusted_entry_price\"`: 若 `pass = false`，則提供修正後的進場價格，否則與原始 `entry_price` 相同\n- `\"recommend_reanalysis\"`: 若 `pass = false` 則為 `true`，表示應重新評估交易機會\n\n---\n\n### **JSON 輸出範例**\n#### **預測成功（通過驗證）**\n```json\n{\n  \"previous_prediction\": {\n    \"macd_cross\": true,\n    \"kdj_cross\": true,\n    \"volume_increase\": true,\n    \"buy_signal\": true,\n    \"entry_price\": 120.5,\n    \"reason\": \"MACD、KDJ 黃金交叉，且成交量放大，市場資金流入，適合買入。\"\n  },\n  \"score\": 9,\n  \"pass\": true,\n  \"validation_reason\": \"預測後 5 天內，股價最高達到 125.0，漲幅超過 3%，符合預測，判定通過。\",\n  \"adjusted_entry_price\": 120.5,\n  \"recommend_reanalysis\": false\n}\n#### **預測失敗（需要重新分析）**\n```json\n{\n  \"previous_prediction\": {\n    \"macd_cross\": true,\n    \"kdj_cross\": true,\n    \"volume_increase\": true,\n    \"buy_signal\": true,\n    \"entry_price\": 120.5,\n    \"reason\": \"MACD、KDJ 黃金交叉，且成交量放大，市場資金流入，適合買入。\"\n  },\n  \"score\": 6,\n  \"pass\": false,\n  \"validation_reason\": \"買入後 5 天內，股價最高僅達到 122.0，未超過 3% 漲幅，且成交量未進一步放大，應考慮當日是賣多、賣少、買多、買少這種基本的依據判斷。\",\n  \"adjusted_entry_price\": 118.0,\n  \"recommend_reanalysis\": true\n}",
)
history2 = []
chat_session2 = model2.start_chat(history=history2)


def send_message1(input, token):
    global chat_session1, history1
    configure_genai_api_key(token)
    output = chat_session1.send_message(input)
    output = output.text
    if len(history1) > 12:
        history1.pop(0)
        history1.pop(0)

    history1.append({
        "role": "user",
        "parts": [input]
    })
    history1.append({
        "role": "model",
        "parts": [output]
    })
    return output


def send_message2(input, token):
    global chat_session2, history2
    configure_genai_api_key(token)
    output = chat_session2.send_message(input)
    output = output.text
    if len(history2) > 12:
        history1.pop(0)
        history1.pop(0)
    history2.append({
        "role": "user",
        "parts": [input]
    })
    history2.append({
        "role": "model",
        "parts": [output]
    })
    return output
