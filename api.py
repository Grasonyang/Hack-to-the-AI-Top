from flask import Blueprint, request, jsonify
import yfinance as yf
import pandas as pd
import json
import functions.indicator as indicators
import functions.gemini as gemini

api = Blueprint('api', __name__)


@api.route('/api/gemini/<model>', methods=['POST'])
def callGemini(model):
    """"""
    try:
        input_json = request.form.get('input')
        input = json.loads(input_json)
        output = None
        if model == "predict":
            output = gemini.predict_model(input)
        elif model == "search":
            output = gemini.search_model(input)
        return jsonify({
            "success": True,
            "data": output
        })
    except Exception as e:
        print(e)
        return jsonify({
            "success": False,
            "message": f"callGemini例外錯誤: {str(e)}"
        })
    pass


@api.route('/api/yfinance/<ticker>/<start_date>/<end_date>/<interval>', methods=['GET'])
def callYfinance(ticker, start_date, end_date, interval) -> jsonify:
    """
    1. 股票資訊傳入
    2. 取得股票資料
    3. 計算技術指標, 參見 functions/indicator.py
    """
    try:
        stock_data = yf.download(
            ticker, start=start_date, end=end_date, interval=interval)
        if stock_data.empty:
            return jsonify({
                "success": False,
                "message": "資料為空"
            })
        # set indicators
        stock_data = indicators.getMovingAverages(stock_data)
        # finish set indicators, start to convert df to json object
        stock_data = stock_data.fillna(0)
        stock_data_df_to_json = []
        i = 0  # id
        for index, row in stock_data.iterrows():
            stock_data_df_to_json.append({
                "id": i,
                "date": index.strftime("%Y-%m-%d"),
                "open": row['Open'].item(),
                "close": row['Close'].item(),
                "high": row['High'].item(),
                "low": row['Low'].item(),
                "volume": row['Volume'].item(),
                "ma5": row['MA5'].item(),
                "ma20": row['MA20'].item()
            })
            i += 1
        return jsonify({
            "success": True,
            "data": stock_data_df_to_json
        })

    except Exception as e:
        print(e)
        return jsonify({
            "success": False,
            "message": f"callYfinance例外錯誤: {str(e)}"
        })


if __name__ == '__main__':
    api.run(debug=True)
