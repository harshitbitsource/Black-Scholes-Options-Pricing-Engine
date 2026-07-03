import json
from pathlib import Path

import pandas as pd
import plotly.graph_objs as go
from flask import Flask, jsonify, render_template, request

from .pricer import black_scholes_price, greek_series, implied_volatility

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

app = Flask(
    __name__,
    template_folder=str(TEMPLATES_DIR),
    static_folder=str(STATIC_DIR),
)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/price", methods=["POST"])
def price_api():
    payload = request.get_json(force=True)
    option_type = payload.get("option_type", "call")
    spot = float(payload["spot"])
    strike = float(payload["strike"])
    years = float(payload["years"])
    volatility = float(payload["volatility"])
    rate = float(payload["rate"])
    dividend_yield = float(payload.get("dividend_yield", 0.0))

    result = black_scholes_price(
        spot,
        strike,
        years,
        volatility,
        rate,
        dividend_yield,
        option_type=option_type,
    )

    return jsonify(
        price=round(result.price, 4),
        delta=round(result.delta, 4),
        gamma=round(result.gamma, 6),
        vega=round(result.vega, 4),
        theta=round(result.theta, 6),
        rho=round(result.rho, 4),
    )


@app.route("/api/implied-vol", methods=["POST"])
def implied_vol_api():
    payload = request.get_json(force=True)
    option_type = payload.get("option_type", "call")
    spot = float(payload["spot"])
    strike = float(payload["strike"])
    years = float(payload["years"])
    market_price = float(payload["market_price"])
    rate = float(payload["rate"])
    dividend_yield = float(payload.get("dividend_yield", 0.0))

    implied_vol = implied_volatility(
        market_price,
        spot,
        strike,
        years,
        rate,
        dividend_yield,
        option_type=option_type,
    )

    return jsonify(implied_vol=round(implied_vol, 6))


@app.route("/api/greeks-chart", methods=["POST"])
def greeks_chart_api():
    payload = request.get_json(force=True)
    option_type = payload.get("option_type", "call")
    spot = float(payload["spot"])
    strike = float(payload["strike"])
    years = float(payload["years"])
    volatility = float(payload["volatility"])
    rate = float(payload["rate"])
    dividend_yield = float(payload.get("dividend_yield", 0.0))

    series_data = greek_series(
        spot,
        strike,
        years,
        volatility,
        rate,
        dividend_yield=dividend_yield,
        option_type=option_type,
    )

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=series_data["underlying"], y=series_data["price"], name="Price"))
    fig.add_trace(go.Scatter(x=series_data["underlying"], y=series_data["delta"], name="Delta"))
    fig.add_trace(go.Scatter(x=series_data["underlying"], y=series_data["gamma"], name="Gamma"))
    fig.add_trace(go.Scatter(x=series_data["underlying"], y=series_data["vega"], name="Vega"))
    fig.add_trace(go.Scatter(x=series_data["underlying"], y=series_data["theta"], name="Theta"))

    fig.update_layout(
        title="Option Greeks and Price vs Underlying",
        xaxis_title="Underlying Price",
        yaxis_title="Value",
        legend_title="Series",
        template="plotly_white",
    )

    return jsonify(graphJSON=fig.to_json())


def main():
    app.run(host="0.0.0.0", port=8080, debug=False)
