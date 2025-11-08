# ────────────────────────────────────────────────────────────────
# IMPORT LIBRARIES
# ────────────────────────────────────────────────────────────────
import streamlit as st
import pandas as pd
import pandas_datareader.data as web
import yfinance as yf
import datetime
import CAPM_Function

# ────────────────────────────────────────────────────────────────
# STREAMLIT PAGE SETUP
# ────────────────────────────────────────────────────────────────
st.set_page_config(page_title="CAPM", page_icon="📈", layout="wide")
st.title("📊 Capital Asset Pricing Model (CAPM)")

# ────────────────────────────────────────────────────────────────
# USER INPUT
# ────────────────────────────────────────────────────────────────
col1, col2 = st.columns([1, 1])

with col1:
    selected_stocks = st.multiselect(
        "Choose Stocks",
        ('TSLA', 'AAPL', 'NFLX', 'MSFT', 'MGM', 'AMZN', 'NVDA', 'GOOGL'),
        ['TSLA', 'AAPL', 'AMZN', 'GOOGL']
    )
with col2:
    years = st.number_input("Number Of Years", 1, 10)

# ────────────────────────────────────────────────────────────────
# DATE RANGE SETUP
# ────────────────────────────────────────────────────────────────
end = datetime.date.today()
start = datetime.date(end.year - years, end.month, end.day)

# ────────────────────────────────────────────────────────────────
# DOWNLOAD S&P500 DATA
# ────────────────────────────────────────────────────────────────
SP500 = web.DataReader("SP500", "fred", start, end)
SP500 = SP500.reset_index()             # ensure simple index
SP500.columns = ["Date", "sp500"]       # rename for merge

# ────────────────────────────────────────────────────────────────
# DOWNLOAD STOCK DATA
# ────────────────────────────────────────────────────────────────
stocks_df = pd.DataFrame()

for stock in selected_stocks:
    data = yf.download(stock, start=start, end=end)

    # ✅ flatten MultiIndex column names returned by yfinance
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = ['_'.join(col).strip() for col in data.columns]
    else:
        data.columns = [str(col) for col in data.columns]

    data["Stock"] = stock
    stocks_df = pd.concat([stocks_df, data])

# ────────────────────────────────────────────────────────────────
# CLEAN INDEX & DATE FOR MERGE
# ────────────────────────────────────────────────────────────────
stocks_df = stocks_df.reset_index()                # Date becomes column
stocks_df["Date"] = pd.to_datetime(stocks_df["Date"])

# ✅ force remove any MultiIndex on index if still remains
if isinstance(stocks_df.index, pd.MultiIndex):
    stocks_df.index = stocks_df.index.droplevel(list(range(stocks_df.index.nlevels)))

if isinstance(SP500.index, pd.MultiIndex):
    SP500.index = SP500.index.droplevel(list(range(SP500.index.nlevels)))

# ────────────────────────────────────────────────────────────────
# FINAL MERGE (WILL NOT FAIL NOW)
# ────────────────────────────────────────────────────────────────
stocks_df = pd.merge(stocks_df, SP500, on="Date", how="inner")

# ────────────────────────────────────────────────────────────────
# DISPLAY DATA
# ────────────────────────────────────────────────────────────────
# ────────────────────────────────────────────────────────────────
# DISPLAY DATA (HEAD + TAIL)
# ────────────────────────────────────────────────────────────────

col1, col2 = st.columns(2)

with col1:
    st.subheader("🔼 First 5 rows (HEAD)")
    st.dataframe(stocks_df.head(), use_container_width=True)

with col2:
    st.subheader("🔽 Last 5 rows (TAIL)")
    st.dataframe(stocks_df.tail(), use_container_width=True)

col1, col2 = st.columns([1, 1])
with col1:
    st.markdown("### Price of all the Stocks")
    st.plotly_chart(CAPM_Function.interactive_plot(stocks_df))

try:
    stocks_daily_return = CAPM_Function.daily_return(stocks_df)
    print(stocks_daily_return.head())

    beta = {}
    alpha = {}

    for i in stocks_daily_return.columns:
        if i != 'Date' and i != 'sp500':
            b, a = CAPM_Function.calculate_beta(stocks_daily_return, i)
            beta[i] = b
            alpha[i] = a

    print(beta, alpha)

    # Create Beta dataframe
    beta_df = pd.DataFrame(columns=['Stock', 'Beta Value'])
    beta_df['Stock'] = beta.keys()
    beta_df['Beta Value'] = [round(i, 2) for i in beta.values()]

    with col1:
        st.markdown('### Calculated Beta Value')
        st.dataframe(beta_df, use_container_width=True)

    # CAPM Return value
    rf = 0
    rn = stocks_daily_return['sp500'].mean() * 252

    return_df = pd.DataFrame()
    return_value = []

    for stock, value in beta.items():
        return_value.append(round(rf + (value * (rn - rf)), 2))

    return_df['Stock'] = list(beta.keys())
    return_df['Return Value'] = return_value

    with col2:
        st.markdown('### Calculated Return using CAPM')
        st.dataframe(return_df, use_container_width=True)

except Exception as e:
    st.write("Please select valid inputs!")
    st.error(e)


