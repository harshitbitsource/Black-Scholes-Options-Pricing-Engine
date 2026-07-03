async function postJson(path, payload) {
  const response = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error("API request failed");
  }

  return response.json();
}

function formatValue(value) {
  return value === null || value === undefined ? "-" : Number(value).toLocaleString(undefined, { maximumFractionDigits: 6 });
}

async function updateResults(formData) {
  const result = await postJson("/api/price", formData);
  document.getElementById("result-price").textContent = formatValue(result.price);
  document.getElementById("result-delta").textContent = formatValue(result.delta);
  document.getElementById("result-gamma").textContent = formatValue(result.gamma);
  document.getElementById("result-vega").textContent = formatValue(result.vega);
  document.getElementById("result-theta").textContent = formatValue(result.theta);
  document.getElementById("result-rho").textContent = formatValue(result.rho);
}

async function updateImpliedVol(formData) {
  const marketPrice = Number(formData.market_price);
  if (marketPrice > 0) {
    const result = await postJson("/api/implied-vol", formData);
    document.getElementById("result-implied-vol").textContent = `${Number(result.implied_vol).toFixed(4)}%`;
  } else {
    document.getElementById("result-implied-vol").textContent = "Enter a market price";
  }
}

async function updateChart(formData) {
  const chartData = await postJson("/api/greeks-chart", formData);
  const figure = JSON.parse(chartData.graphJSON);
  Plotly.react("chart", figure.data, figure.layout, { responsive: true });
}

async function handleFormSubmit(event) {
  event.preventDefault();
  const form = event.target;
  const formData = {
    option_type: form.option_type.value,
    spot: form.spot.value,
    strike: form.strike.value,
    years: form.years.value,
    volatility: Number(form.volatility.value) / 100,
    rate: Number(form.rate.value) / 100,
    dividend_yield: Number(form.dividend_yield.value) / 100,
    market_price: form.market_price.value,
  };

  try {
    await updateResults(formData);
    await updateImpliedVol(formData);
    await updateChart(formData);
  } catch (error) {
    console.error(error);
    alert("Unable to calculate option values. Please check your input.");
  }
}

const pricingForm = document.getElementById("pricing-form");
pricingForm.addEventListener("submit", handleFormSubmit);
window.addEventListener("load", () => pricingForm.requestSubmit());
