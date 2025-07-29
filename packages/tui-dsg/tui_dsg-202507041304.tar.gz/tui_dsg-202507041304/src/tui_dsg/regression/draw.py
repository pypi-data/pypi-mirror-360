from math import fabs as abs

import numpy as np
import pandas as pd
import torch


def frange(start, stop, steps):
    step_size = (stop - start) / steps

    while start < stop:
        end = min(start + step_size, stop)
        yield start, end
        start = end


def polynomial(x, *coef):
    val = 0
    for n, c in enumerate(coef):
        val += c * (x ** n)

    return val


def R(x_series, y_series, *coef):
    return (
        (y - yr) for y, yr in zip(
        y_series,
        (
            polynomial(x, *coef) for x in x_series
        )
    )
    )


def R_abs(x_series, y_series, *coef):
    return sum(map(abs, R(x_series, y_series, *coef)))


def R_squared(x_series, y_series, *coef):
    return sum((r * r for r in R(x_series, y_series, *coef)))


def draw_regression(fig, *coef, regression_width=1, regression_opacity=1, residual_width=0.5, residual_opacity=0):
    steps = max(1, min(100, (len(coef) - 1) * 50))

    # regression
    min_x = np.inf
    max_x = -np.inf

    for data in fig['data']:
        min_x = min(min_x, data['x'].min())
        max_x = max(max_x, data['x'].max())

    for x0, x1 in frange(min_x, max_x, steps):
        fig.add_shape(
            type='line',
            x0=x0, y0=polynomial(x0, *coef),
            x1=x1, y1=polynomial(x1, *coef),
            line={
                'width': regression_width,
                'color': f'rgba(255, 0, 0, {regression_opacity})'
            }
        )

    # residuals
    if residual_width > 0 and residual_opacity > 0:
        for data in fig['data']:
            for x, y in zip(data['x'], data['y']):
                fig.add_shape(
                    type='line',
                    x0=x, y0=y,
                    x1=x, y1=polynomial(x, *coef),
                    line={
                        'width': residual_width,
                        'color': f'rgb(255, 0, 0, {residual_opacity})'
                    }
                )

    return fig


def draw_nn_regression(fun, df: pd.DataFrame, **kwargs):
    Xs = [i / 20 for i in range(-80, 121, 1)]
    Ys = []

    for model in fun(df, **kwargs):
        s = []
        for x in Xs:
            x_t = torch.tensor([x])
            y_pred = model(x_t)
            s.append(y_pred.item())
        Ys.append(s)

    xd = []
    yd = []
    framed = []
    typed = []

    for frame, s in enumerate(Ys):
        for x, y in zip(Xs, s):
            xd.append(x)
            yd.append(y)
            framed.append(frame)
            typed.append('pred')

        for _, (x, y) in df.iterrows():
            xd.append(x)
            yd.append(y)
            framed.append(frame)
            typed.append('object')

    return pd.DataFrame({
        'x': xd,
        'y': yd,
        'epoch': framed,
        'type': typed
    })
