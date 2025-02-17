def getMACD(df, fastperiod=12, slowperiod=26, signalperiod=9):
    """
    計算 MACD 指標（不使用 TA-Lib）。
    """
    EMA_fast = df['Close'].ewm(span=fastperiod, adjust=False).mean()
    EMA_slow = df['Close'].ewm(span=slowperiod, adjust=False).mean()
    MACD = EMA_fast - EMA_slow
    Signal = MACD.ewm(span=signalperiod, adjust=False).mean()
    Histogram = MACD - Signal
    df['MACD'] = MACD
    df['MACD_Signal'] = Signal
    df['MACD_Hist'] = Histogram
    return df


def getKDJ(df, period=9):
    """
    計算 KDJ 指標（不使用 TA-Lib）。
    """
    Lowest_Low = df['Low'].rolling(window=period).min()
    Highest_High = df['High'].rolling(window=period).max()
    RSV = ((df['Close'] - Lowest_Low) /
           (Highest_High - Lowest_Low)) * 100  # 修正這裡
    df['K'] = RSV.ewm(span=3, adjust=False).mean()
    df['D'] = df['K'].ewm(span=3, adjust=False).mean()
    df['J'] = 3 * df['K'] - 2 * df['D']
    return df


def getRSI(df, period=14):
    """
    計算 RSI 指標（不使用 TA-Lib）。
    """
    delta = df['Close'].diff()
    up, down = delta.copy(), delta.copy()
    up[up < 0] = 0
    down[down > 0] = 0
    roll_up = up.rolling(window=period).mean()
    roll_down = down.abs().rolling(window=period).mean()
    RS = roll_up / roll_down
    RSI = 100.0 - (100.0 / (1.0 + RS))
    df['RSI'] = RSI
    return df
