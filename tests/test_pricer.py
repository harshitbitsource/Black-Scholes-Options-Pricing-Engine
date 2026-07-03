import pytest

from black_scholes_engine.pricer import black_scholes_price, implied_volatility


def test_black_scholes_call_price():
    result = black_scholes_price(100, 100, 1, 0.2, 0.05, 0.0, option_type="call")
    assert pytest.approx(result.price, rel=1e-3) == 10.4506
    assert pytest.approx(result.delta, rel=1e-3) == 0.6368


def test_black_scholes_put_price():
    result = black_scholes_price(100, 100, 1, 0.2, 0.05, 0.0, option_type="put")
    assert pytest.approx(result.price, rel=1e-3) == 5.5735
    assert pytest.approx(result.delta, rel=1e-3) == -0.3632


def test_implied_volatility_converges():
    implied = implied_volatility(10.4506, 100, 100, 1, 0.05, 0.0, option_type="call")
    assert pytest.approx(implied, rel=1e-3) == 0.2
