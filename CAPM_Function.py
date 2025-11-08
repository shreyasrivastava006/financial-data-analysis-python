import plotly.graph_objects as go
import pandas as pd

# ✅ Interactive Plot Function
def interactive_plot(df):
    fig = go.Figure()

    for col in df.columns[1:]:  # skip 'Date'
        fig.add_trace(
            go.Scatter(
                x=df["Date"],
                y=df[col],
                mode="lines",
                name=col
            )
        )

    fig.update_layout(
        width=450,
        margin=dict(l=20, r=20, t=50, b=20),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        xaxis_title="Date",
        yaxis_title="Price"
    )

    return fig


# ✅ Daily return function
def daily_return(stocks_df):
    df = stocks_df.copy()
    df["Date"] = pd.to_datetime(df["Date"])
    df.set_index("Date", inplace=True)

    # 🔥 Convert only number columns to numeric (fixes "unsupported operand type(s) for /: 'str'")
    df = df.apply(pd.to_numeric, errors="coerce")

    return df.pct_change().dropna()


# ✅ Beta & Alpha calculation function
def calculate_beta(df, stock_name):
    df = df.copy()
    df = df.apply(pd.to_numeric, errors="coerce")   # ensure numeric

    market_var = df["sp500"].var()
    cov = df[[stock_name, "sp500"]].cov().iloc[0, 1]

    beta = cov / market_var
    alpha = df[stock_name].mean() - beta * df["sp500"].mean()

    return beta, alpha


    market_var = df["sp500"].var()
    cov = df[[stock_name, "sp500"]].cov().iloc[0, 1]

    beta = cov / market_var
    alpha = df[stock_name].mean() - beta * df["sp500"].mean()

    return beta, alpha
