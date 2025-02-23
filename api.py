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
        output = None
        if model == "predict":
            output = gemini.predict_model(input_json)
        elif model == "search":
            output = gemini.search_model(input_json)
        elif model == "result":
            output = gemini.result_model(input_json)
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


@api.route('/api/stock/code/<number>', methods=['GET'])
def callStockCode(number):
    """
    url: http://www.ccnet.com.tw/stock_code/code12.htm#13
    選取類別: 電子類23
    """
    if number == "23":
        # stock_codes = {
        #     "2301": "光寶", "2302": "麗正", "2303": "聯電", "2304": "誠洲", "2305": "全友", "2306": "宏電",
        #     "2308": "台達電", "2310": "旭麗", "2311": "日月光", "2312": "金寶", "2313": "華通", "2314": "台揚",
        #     "2315": "神達", "2316": "楠電", "2317": "鴻海", "2318": "佳錄", "2319": "大眾", "2320": "中強",
        #     "2321": "東訊", "2322": "致福", "2323": "中環", "2324": "仁寶", "2325": "矽品", "2326": "亞瑟",
        #     "2327": "國巨", "2328": "廣宇", "2329": "華泰", "2330": "台積電", "2331": "精英", "2332": "友訊",
        #     "2333": "碧悠", "2334": "國豐", "2335": "清三", "2336": "致伸", "2337": "旺宏", "2338": "光罩",
        #     "2340": "光磊", "2341": "英群", "2342": "茂矽", "2343": "精業", "2344": "華邦電", "2345": "智邦",
        #     "2346": "源興", "2347": "聯強", "2348": "力捷", "2349": "錸德", "2350": "環隆", "2351": "順德",
        #     "2352": "明電", "2353": "宏科", "2354": "華升", "2355": "敬鵬", "2356": "英業達", "2357": "華碩",
        #     "2358": "美格", "2359": "所羅門", "2360": "致茂", "2361": "鴻友", "2362": "藍天", "2363": "矽統",
        #     "2364": "倫飛", "2365": "昆盈", "2366": "亞旭", "2367": "耀華", "2368": "金像電", "2369": "菱生",
        #     "2370": "匯僑工", "2371": "大同", "2372": "台硝", "2373": "震旦行", "2374": "佳能", "2375": "智寶",
        #     "2376": "技嘉", "2377": "微星", "2378": "鴻運電", "2379": "瑞昱", "2380": "虹光", "2381": "華宇",
        #     "2382": "廣達", "2383": "台光電", "2384": "勝華", "2385": "群光", "2386": "國碁電", "2387": "精元",
        #     "2388": "威盛", "2389": "世昕", "2390": "云辰", "2391": "合勤", "2392": "正崴", "2393": "億光",
        #     "2394": "普立爾", "2395": "研華", "2396": "精碟", "2397": "友通", "2398": "博達", "2399": "映泰"
        # }
        stock_codes = {
            "2301": "光寶", "2303": "聯電",
            "2308": "台達電", "3711": "日月光投控",
            # "2315": "神達", "2317": "鴻海",
            # "2330": "台積電", "2331": "精英", "2332": "友訊",
            # "2337": "旺宏",
            # "2344": "華邦電", "2345": "智邦",
            # "2356": "英業達", "2357": "華碩",
            # "2359": "所羅門",
            # "2376": "技嘉", "2377": "微星",
            # "2382": "廣達", "2383": "台光電", "2395": "研華"
        }
        return jsonify({
            "success": True,
            "data": stock_codes
        })
    else:
        return jsonify({
            "success": False,
            "message": "Invalid number"
        })


if __name__ == '__main__':
    api.run(debug=True)
