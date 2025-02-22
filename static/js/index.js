class API {
  async gemini(model, input) {
    let apiUrl = `/api/gemini/${model}`;
    return new Promise((resolve, reject) => {
      $.ajax({
        url: apiUrl,
        method: "POST",
        data: {
          input: JSON.stringify(input),
        },
        dataType: "json",
        success: function (e) {
          console.log("gemini:", e);
          resolve(e);
        },
        error: function (error) {
          console.error("Error:", error);
          reject(error);
        },
      });
    });
  }
  async yfinance(ticker, start_date, end_date, interval) {
    let apiUrl = `/api/yfinance/${ticker}/${start_date}/${end_date}/${interval}`;
    return new Promise((resolve, reject) => {
      $.ajax({
        url: apiUrl,
        method: "GET",
        dataType: "json",
        success: function (e) {
          console.log("yfinance:", e);
          resolve(e);
        },
        error: function (error) {
          console.error("Error:", error);
          reject(error);
        },
      });
    });
  }
}
