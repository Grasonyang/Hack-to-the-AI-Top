### Hack to the AI Top 初賽

#### 📌 目標與方法

在股票市場中，投資人面對眾多選擇，因此我們希望透過 **語言模型 (LLM) + 新聞 + 指標判斷**，提供快速且方便的買點預測。

如何使用 code

0. git this project
1. `flask --app app run`
2. 準備 token，請至 google ai studio 獲取 token
3. 點擊 web server, 資料會自動載入

實作方法：

1. 周線作為長線基準(對我來說)
2. 新聞面
3. 統整

已知問題

1. api 有限制，無論是 yfinance、gemini，免費的速度還不錯，但量不能多
2. 一支股票代碼需要呼叫 2 次 yfinance(1d、1wk)、3 次 gemini(參見 functions/gemini.py、api.py/callGemini)
