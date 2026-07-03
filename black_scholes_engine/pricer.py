import math
import numpy as np

from dataclasses import dataclass

@dataclass
class OptionResult:
    price: float
    delta: float
    gamma: float
    vega: float
    theta: float
    rho: float
    implied_vol: float | None = None


def _std_normal_pdf(x: float) -> float:
    return math.exp(-0.5 * x * x) / math.sqrt(2 * math.pi)


def _std_normal_cdf(x: float) -> float:
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def black_scholes_price(
    spot: float,
    strike: float,
    time_to_expiry: float,
    volatility: float,
    rate: float,
    dividend_yield: float = 0.0,
    option_type: str = "call",
) -> OptionResult:
    if spot <= 0 or strike <= 0 or time_to_expiry <= 0 or volatility <= 0:
        raise ValueError("Spot, strike, time to expiry, and volatility must be positive.")

    sigma = volatility
    sqrt_t = math.sqrt(time_to_expiry)
    d1 = (math.log(spot / strike) + (rate - dividend_yield + 0.5 * sigma**2) * time_to_expiry) / (sigma * sqrt_t)
    d2 = d1 - sigma * sqrt_t
    discount_factor = math.exp(-rate * time_to_expiry)
    dividend_factor = math.exp(-dividend_yield * time_to_expiry)

    if option_type.lower() == "call":
        price = spot * dividend_factor * _std_normal_cdf(d1) - strike * discount_factor * _std_normal_cdf(d2)
        delta = dividend_factor * _std_normal_cdf(d1)
        rho = strike * time_to_expiry * discount_factor * _std_normal_cdf(d2)
    elif option_type.lower() == "put":
        price = strike * discount_factor * _std_normal_cdf(-d2) - spot * dividend_factor * _std_normal_cdf(-d1)
        delta = dividend_factor * (_std_normal_cdf(d1) - 1)
        rho = -strike * time_to_expiry * discount_factor * _std_normal_cdf(-d2)
    else:
        raise ValueError("option_type must be 'call' or 'put'.")

    gamma = dividend_factor * _std_normal_pdf(d1) / (spot * sigma * sqrt_t)
    vega = spot * dividend_factor * _std_normal_pdf(d1) * sqrt_t
    theta = -(
        spot * dividend_factor * _std_normal_pdf(d1) * sigma / (2 * sqrt_t)
        + rate * strike * discount_factor * _std_normal_cdf(d2 if option_type.lower() == "call" else -d2)
        - dividend_yield * spot * dividend_factor * _std_normal_cdf(d1 if option_type.lower() == "call" else -d1)
    )

    return OptionResult(
        price=price,
        delta=delta,
        gamma=gamma,
        vega=vega / 100,
        theta=theta / 365,
        rho=rho / 100,
        implied_vol=None,
    )


def implied_volatility(
    market_price: float,
    spot: float,
    strike: float,
    time_to_expiry: float,
    rate: float,
    dividend_yield: float = 0.0,
    option_type: str = "call",
    initial_guess: float = 0.2,
    tolerance: float = 1e-8,
    max_iterations: int = 100,
) -> float:
    if market_price <= 0:
        raise ValueError("Market price must be positive.")

    sigma = initial_guess
    for _ in range(max_iterations):
        result = black_scholes_price(spot, strike, time_to_expiry, sigma, rate, dividend_yield, option_type)
        price = result.price
        vega = result.vega * 100
        if vega == 0:
            break
        price_diff = price - market_price
        if abs(price_diff) < tolerance:
            return sigma
        sigma -= price_diff / vega
        sigma = max(sigma, 1e-12)
    raise RuntimeError("Implied volatility did not converge.")


def greek_series(
    spot: float,
    strike: float,
    time_to_expiry: float,
    volatility: float,
    rate: float,
    dividend_yield: float = 0.0,
    option_type: str = "call",
    points: int = 50,
    span: float = 0.5,
) -> dict[str, list[float]]:
    strikes = np.linspace(strike * (1 - span), strike * (1 + span), points)
    call_prices = []
    deltas = []
    gammas = []
    vegas = []
    thetas = []

    for s in strikes:
        result = black_scholes_price(s, strike, time_to_expiry, volatility, rate, dividend_yield, option_type)
        call_prices.append(result.price)
        deltas.append(result.delta)
        gammas.append(result.gamma)
        vegas.append(result.vega)
        thetas.append(result.theta)

    return {
        "underlying": strikes.tolist(),
        "price": call_prices,
        "delta": deltas,
        "gamma": gammas,
        "vega": vegas,
        "theta": thetas,
    }
