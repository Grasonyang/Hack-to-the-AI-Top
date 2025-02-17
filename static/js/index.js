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
  // data format
  // 從第31筆開始抓取，設定移動窗口35，每次移動一筆，取得並製作輸入資料
  // 輸入資料input1、input2
  input_data = {
    input1: [],
    input2: [],
    input_raw: [],
  };
  data_window = 35;
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
    input_data.input_raw.push(data[i + data_window]);
    input_data.input1.push(input1);
    input_data.input2.push(input2);
  }
  console.log(input_data);
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
        // drawData(data); // draw
      },
      error: function (error) {
        console.error("Error:", error);
      },
    });
  }
}
