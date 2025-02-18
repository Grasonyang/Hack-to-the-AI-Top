let data = [];
const margin = { top: 20, right: 20, bottom: 70, left: 60 }; // 增加 bottom margin
const width = 960 - margin.left - margin.right;
const height = 500 - margin.top - margin.bottom;

const svg = d3
  .select("#chart")
  .append("svg")
  .attr("width", width + margin.left + margin.right)
  .attr("height", height + margin.top + margin.bottom)
  .append("g")
  .attr("transform", `translate(${margin.left}, ${margin.top})`);

// --- 使用 d3.scaleBand() ---
const x = d3.scaleBand().range([0, width]).padding(0.2); // 添加 padding
const y = d3.scaleLinear().range([height, 0]);

const xAxis = d3.axisBottom(x);
const yAxis = d3.axisLeft(y);

svg
  .append("g")
  .attr("class", "x-axis")
  .attr("transform", `translate(0, ${height})`)
  .call(xAxis);

svg.append("g").attr("class", "y-axis").call(yAxis);

let startIndex = 0;
const dataSlice = 30;

d3.select("#leftButton").on("click", () => {
  if (data.length > 0 && startIndex > 0) {
    startIndex -= 1;
    updateChart();
  }
});

d3.select("#rightButton").on("click", () => {
  if (data.length > 0 && startIndex + dataSlice < data.length) {
    startIndex += 1;
    updateChart();
  }
});

function updateChart() {
  if (data.length === 0) return;

  const newData = data.slice(startIndex, startIndex + dataSlice);
  // x 軸的 domain 是日期字串的陣列
  x.domain(newData.map((d) => d.date));
  y.domain([d3.min(newData, (d) => d.low), d3.max(newData, (d) => d.high)]);

  // 更新 x 軸
  svg
    .select(".x-axis")
    .transition()
    .duration(500)
    .call(xAxis)
    .selectAll("text") // 旋轉 x 軸的 labels
    .style("text-anchor", "end")
    .attr("dx", "-.8em")
    .attr("dy", ".15em")
    .attr("transform", "rotate(-65)");

  svg.select(".y-axis").transition().duration(500).call(yAxis);

  // --- 繪製 K 線圖 ---
  const candles = svg.selectAll(".candle").data(newData, (d) => d.date);

  const candlesEnter = candles.enter().append("g").attr("class", "candle");

  // K 線的垂直線
  candlesEnter
    .append("line")
    .attr("class", "stem")
    .attr("x1", (d) => x(d.date) + x.bandwidth() / 2) // 使用 band 的中心
    .attr("x2", (d) => x(d.date) + x.bandwidth() / 2)
    .attr("y1", (d) => y(d.high))
    .attr("y2", (d) => y(d.low))
    .attr("stroke", "black");

  // K 線的矩形
  candlesEnter
    .append("rect")
    .attr("class", (d) => (d.open > d.close ? "down" : "up"))
    .attr("x", (d) => x(d.date)) // x 座標是 band 的起始位置
    .attr("y", (d) => y(Math.max(d.open, d.close)))
    .attr("width", x.bandwidth()) // 寬度是 band 的寬度
    .attr("height", (d) => Math.abs(y(d.open) - y(d.close)) || 1); // 避免高度為 0

  const candlesUpdate = candlesEnter.merge(candles);

  candlesUpdate
    .select(".stem")
    .transition()
    .duration(500)
    .attr("x1", (d) => x(d.date) + x.bandwidth() / 2)
    .attr("x2", (d) => x(d.date) + x.bandwidth() / 2)
    .attr("y1", (d) => y(d.high))
    .attr("y2", (d) => y(d.low));

  candlesUpdate
    .select("rect")
    .transition()
    .duration(500)
    .attr("class", (d) => (d.open > d.close ? "down" : "up"))
    .attr("x", (d) => x(d.date))
    .attr("y", (d) => y(Math.max(d.open, d.close)))
    .attr("width", x.bandwidth())
    .attr("height", (d) => Math.abs(y(d.open) - y(d.close)) || 1);

  candles.exit().remove();
}

function drawData(apiData) {
  if (!apiData || apiData.length === 0) {
    console.warn("No data received from API.");
    return;
  }

  data = apiData.map((item) => ({
    date: item.date, // 不再需要 new Date()
    open: +item.open,
    high: +item.high,
    low: +item.low,
    close: +item.close,
  }));

  updateChart();
}

async function dealData(data) {
  data_window = 35;
  // output1_count只有module1預測
  output1_count_no_model2 = {
    buy_signal_false: 0,
    buy_signal_true: 0,
    first_return_output: [],
  };
  for (let i = 27; i < data.length - data_window; i++) {
    let input1 = [];
    let input2 = [];
    for (let j = 0; j < data_window; j++) {
      if (j < 30) {
        input1.push(data[i + j]);
        input2.push(data[i + j]);
      } else {
        input2.push(data[i + j]);
      }
    }
    // 獲取input1、input2 json array
    // 組合輸入資料
    input1_prompt = {
      prompt:
        "你是一個專業的股票分析師，根據過去 30 天的股票數據，分析是否出現買入訊號。",
      data: input1,
    };
    output1 = await callAPI(input1_prompt, 1);
    if (output1.buy_signal) {
      output1_count_no_model2.buy_signal_true += 1;
    } else {
      output1_count_no_model2.buy_signal_false += 1;
    }
    draw_no_module2_object = JSON.parse(JSON.stringify(input2[30]));
    draw_no_module2_object.predict = output1;
    output1_count_no_model2.first_return_output.push(draw_no_module2_object);

    input2_prompt = {
      prompt:
        "你是一個專業的股票交易評估師，你的任務是根據 **額外 5 天的數據**，驗證 **過去 30 天的分析結果是否準確**。",
      data: input2,
      previous_prediction: output1,
    };
    output2 = await callAPI(input2_prompt, 2);
    // output2檢視預測結果
    // while (1) {
    //   input2_prompt = {
    //     prompt:
    //       "你是一個專業的股票交易評估師，你的任務是根據 **額外 5 天的數據**，驗證 **過去 30 天的分析結果是否準確**。",
    //     data: input2,
    //     previous_prediction: output1,
    //   };
    //   output2 = await callAPI(input2_prompt, 2);
    //   if (output2.pass) {
    //     break;
    //   } else {
    //     input1_prompt = {
    //       prompt: "這",
    //       data: input1,
    //     };
    //     output1 = await callAPI(input1_prompt, 1);
    //   }
    //   // 應該要output.pass為true才能跳出迴圈
    // }
    break;
    input_data.input2.push({
      prompt: "",
      data: input2,
      last_prompt_ouput: output1,
    });
  }
}

async function callAPI(data, model) {
  let apiUrl = `/api/gemini/${model}`;
  return new Promise((resolve, reject) => {
    $.ajax({
      url: apiUrl,
      method: "POST",
      contentType: "application/json",
      data: JSON.stringify({
        input: JSON.stringify(data),
      }),
      success: function (e) {
        resolve(e.data);
      },
      error: function (error) {
        console.error("Error:", error);
        reject(error);
      },
    });
  });
}

function getData() {
  let ticker = $("#ticker").val();
  let start_date = $("#start_date").val();
  let end_date = $("#end_date").val();
  let interval = $("#interval").val();

  if (ticker && start_date && end_date && interval) {
    let apiUrl = `/api/yfinance/${ticker}/${start_date}/${end_date}/${interval}`;

    $.ajax({
      url: apiUrl,
      method: "GET",
      dataType: "json",
      success: async function (apiData) {
        data = await dealData(apiData.data); // call llm
        // drawData(apiData.data); // draw
      },
      error: function (error) {
        console.error("Error:", error);
      },
    });
  }
}
