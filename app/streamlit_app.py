from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.storage import available_dates, load_correlation, load_tickers


st.set_page_config(page_title="Stock Correlation Explorer", page_icon="ðŸ“ˆ", layout="wide")
st.title("Stock Correlation Explorer")
st.caption("Trailing 20-trading-day return correlations")

output_dir = st.sidebar.text_input("Output directory", "correlation_output")
output_path = Path(output_dir)

if not (output_path / "tickers.parquet").exists():
    st.info(
        "Run the pipeline first: "
        "`python -m src.pipeline --input path/to/stock_data.zip --output correlation_output`"
    )
    st.stop()

dates = available_dates(output_path)
tickers_df = load_tickers(output_path)
tickers = tickers_df["ticker"].tolist()

if not dates:
    st.error("No correlation dates found.")
    st.stop()

selected_date = st.sidebar.selectbox(
    "Date", dates, format_func=lambda x: x.strftime("%Y-%m-%d")
)
selected_ticker = st.sidebar.selectbox("Stock", tickers)
top_n = st.sidebar.slider("Number of peers", 5, 50, 15)

ticker_to_id = dict(zip(tickers_df["ticker"], tickers_df["index"]))
ticker_id = int(ticker_to_id[selected_ticker])

matrix = load_correlation(output_path, selected_date)
row = matrix[ticker_id].copy()
row[ticker_id] = np.nan

ranking = pd.DataFrame({"ticker": tickers, "correlation": row}).dropna()
positive = ranking.sort_values("correlation", ascending=False).head(top_n)
negative = ranking.sort_values("correlation", ascending=True).head(top_n)

col1, col2 = st.columns(2)

with col1:
    st.subheader(f"Top positive correlations for {selected_ticker}")
    st.dataframe(
        positive.style.format({"correlation": "{:.3f}"}),
        use_container_width=True,
        hide_index=True,
    )

with col2:
    st.subheader(f"Top negative correlations for {selected_ticker}")
    st.dataframe(
        negative.style.format({"correlation": "{:.3f}"}),
        use_container_width=True,
        hide_index=True,
    )

heatmap_tickers = [selected_ticker] + positive["ticker"].head(9).tolist()
heatmap_ids = [ticker_to_id[t] for t in heatmap_tickers]
heatmap = matrix[np.ix_(heatmap_ids, heatmap_ids)]

fig = px.imshow(
    heatmap,
    x=heatmap_tickers,
    y=heatmap_tickers,
    zmin=-1,
    zmax=1,
    text_auto=".2f",
    aspect="auto",
    title=f"Correlation heatmap â€” {selected_date:%Y-%m-%d}",
)

st.plotly_chart(fig, use_container_width=True)

