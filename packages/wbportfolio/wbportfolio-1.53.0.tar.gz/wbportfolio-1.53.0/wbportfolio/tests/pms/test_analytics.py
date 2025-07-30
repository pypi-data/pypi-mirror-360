import pandas as pd

from wbportfolio.pms.analytics.portfolio import Portfolio


def test_get_next_weights():
    w0 = 0.3
    w1 = 0.5
    w2 = 0.2
    r0 = 0.1
    r1 = 0.05
    r2 = -0.23
    weights = [w0, w1, w2]
    returns = [r0, r1, r2]
    portfolio = Portfolio(X=pd.DataFrame([returns]), weights=pd.Series(weights))
    next_weights = portfolio.get_next_weights()

    assert next_weights[0] == w0 * (r0 + 1) / (w0 * (r0 + 1) + w1 * (r1 + 1) + w2 * (r2 + 1))
    assert next_weights[1] == w1 * (r1 + 1) / (w0 * (r0 + 1) + w1 * (r1 + 1) + w2 * (r2 + 1))
    assert next_weights[2] == w2 * (r2 + 1) / (w0 * (r0 + 1) + w1 * (r1 + 1) + w2 * (r2 + 1))


def test_get_estimate_net_value():
    w0 = 0.3
    w1 = 0.5
    w2 = 0.2
    r0 = 0.1
    r1 = 0.05
    r2 = -0.23
    weights = [w0, w1, w2]
    returns = [r0, r1, r2]
    portfolio = Portfolio(X=pd.DataFrame([returns]), weights=pd.Series(weights))
    current_price = 100
    net_asset_value = portfolio.get_estimate_net_value(current_price)
    return net_asset_value == current_price * (1.0 + w0 * r0 + w1 * r1 + w2 * r2)
