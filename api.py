from flask import Blueprint, request, jsonify
import yfinance as yf
import pandas as pd
import functions.indicator as indicators
api = Blueprint('api', __name__)


@api.route('/api/yfinance/<ticker>/<start_date>/<end_date>/<interval>', methods=['GET'])
def getData(ticker, start_date, end_date, interval) -> jsonify:
    """
    1. 股票資訊傳入
    2. 取得股票資料
    3. 計算技術指標
    4. 儲存資料到資料庫
    """

    # get stock data
    try:
        stock_data = yf.download(
            ticker, start=start_date, end=end_date, interval=interval)
        if stock_data.empty:
            return jsonify({
                "success": False,
                "message": "資料為空"
            })
        # set indicators
        stock_data = indicators.getMACD(stock_data)
        stock_data = indicators.getKDJ(stock_data)
        # print("finish get indicators")
        # set nan to 0
        stock_data = stock_data.fillna(0)
        # print(stock_data)
        # save stock data to csv
        stock_data.to_csv(f'{ticker}_{start_date}_{end_date}.csv')
        # reset index to ensure keys are serializable
        stock_data_df_to_json = []
        i = 0
        for index, row in stock_data.iterrows():
            stock_data_df_to_json.append({
                "id": i,
                "date": index.strftime("%Y-%m-%d"),
                "open": row['Open'].item(),
                "close": row['Close'].item(),
                "high": row['High'].item(),
                "low": row['Low'].item(),
                "volume": row['Volume'].item(),
                "macd": row['MACD'].item(),
                "macd_signal": row['MACD_Signal'].item(),
                "macd_hist": row['MACD_Hist'].item(),
                "k": row['K'].item(),
                "d": row['D'].item(),
                "j": row['J'].item(),
            })
            i += 1
        # print("finish df to json object")
        # print(stock_data_df_to_json)
        return jsonify({
            "success": True,
            "data": stock_data_df_to_json
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"getData例外錯誤: {str(e)}"
        })


def callAPI():
    pass
