let barCount = 100;

var ctx = document.getElementById("chart").getContext("2d");

var barData = new Array(barCount);
var lineData = new Array(barCount);

getData();

var chart = new Chart(ctx, {
  type: "candlestick",
  data: {
    datasets: [
      {
        label: "CHRT - Chart.js Corporation",
        data: barData,
      },
      {
        label: "Close price",
        type: "line",
        data: lineData,
        hidden: true,
      },
    ],
  },
});

function processData(data) {
  barData = data.slice(0, barCount).map((item) => ({
    x: new Date(item.date).valueOf(),
    o: item.open,
    h: item.high,
    l: item.low,
    c: item.close,
  }));

  lineData = barData.map((item) => ({
    x: item.x,
    y: item.c,
  }));

  chart.update();
}

function getData() {
  let ticker = $("#ticker").val();
  let start_date = $("#start_date").val();
  let end_date = $("#end_date").val();
  let interval = $("#interval").val();
  console.log(ticker, start_date, end_date, interval);

  if (ticker && start_date && end_date && interval) {
    let apiUrl = `/api/yfinance/${ticker}/${start_date}/${end_date}/${interval}`;
    // Use $.ajax for better jQuery integration
    $.ajax({
      url: apiUrl,
      method: "GET",
      dataType: "json",
      success: function (data) {
        console.log(data);
        processData(data.data);
      },
      error: function (error) {
        console.error("Error:", error);
      },
    });
  }
}

var update = function () {
  var dataset = chart.config.data.datasets[0];

  // candlestick vs ohlc
  var type = document.getElementById("type").value;
  chart.config.type = type;

  // linear vs log
  var scaleType = document.getElementById("scale-type").value;
  chart.config.options.scales.y.type = scaleType;

  // color
  var colorScheme = document.getElementById("color-scheme").value;
  if (colorScheme === "neon") {
    chart.config.data.datasets[0].backgroundColors = {
      up: "#01ff01",
      down: "#fe0000",
      unchanged: "#999",
    };
  } else {
    delete chart.config.data.datasets[0].backgroundColors;
  }

  // border
  var border = document.getElementById("border").value;
  if (border === "false") {
    dataset.borderColors = "rgba(0, 0, 0, 0)";
  } else {
    delete dataset.borderColors;
  }

  // mixed charts
  var mixed = document.getElementById("mixed").value;
  if (mixed === "true") {
    chart.config.data.datasets[1].hidden = false;
  } else {
    chart.config.data.datasets[1].hidden = true;
  }

  chart.update();
};

[...document.getElementsByTagName("select")].forEach((element) =>
  element.addEventListener("change", update)
);

document.getElementById("update").addEventListener("click", update);

document.getElementById("randomizeData").addEventListener("click", function () {
  getRandomData(initialDateStr, barData);
  update();
});
