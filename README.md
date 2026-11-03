# Stock Correlation Pipeline & Explorer

Practice implementation for the stock-correlation take-home.

## What it does

1. Reads daily stock-price CSVs from a directory or ZIP archive.
2. Builds a date Ã— ticker price matrix.
3. Computes daily returns.
4. Computes trailing 20-trading-day Pearson correlations between stock returns.
5. Stores only the upper triangle of each symmetric correlation matrix as compressed `float32` NumPy arrays.
6. Provides a Streamlit + Plotly UI.

## Input

The assignment screenshot suggests files like:

```text
stock_data/
â”œâ”€â”€ 20200101.csv
â”œâ”€â”€ 20200102.csv
â””â”€â”€ ...
```

Each CSV should contain a ticker/security identifier and a closing price.

The loader accepts common names such as `ticker`/`symbol` and `close`/`price`/`adjusted_close`. The date is inferred from an 8-digit `YYYYMMDD` value in the filename.

If your real files use different names, edit the aliases in `src/loader.py`.

## Correlation definition

For date `t`, the correlation between stock A and stock B is the Pearson correlation of their daily returns over the previous 20 trading observations ending at `t`.

This is the rolling-window interpretation of "trailing 20-day return correlations".

## Quick start

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pytest -q
python -m src.pipeline --input sample_data/stock_data --output output
streamlit run app/streamlit_app.py
```

Against the assignment ZIP:

```powershell
python -m src.pipeline --input C:\path\to\stock_data.zip --output output
```

## Storage choice

A 5,000 Ã— 5,000 correlation matrix has 25 million values per date. It is symmetric, so only the strict upper triangle is stored:

`5,000 Ã— 4,999 / 2 = 12,497,500` values.

The values are `float32`. This avoids repeating ticker strings millions of times in a long-form table and makes the dense matrix representation compact.

Ticker metadata is stored separately in `tickers.parquet`.

## Performance

For complete windows, the correlation matrix is calculated with vectorized NumPy matrix multiplication after column standardization:

`Z.T @ Z / (n - 1)`

This avoids a Python loop over every stock pair.

### Missing Data

The supplied dataset contains one row with a missing ticker in each daily CSV. These rows are excluded during ingestion because they cannot be associated with a valid instrument.

Missing prices are preserved as missing values; they are not imputed. When calculating a rolling correlation matrix, an instrument must have a complete return window to participate. Instruments with missing returns in the window receive undefined (`NaN`) correlations for that date.

This approach avoids introducing artificial prices or returns into the correlation calculations.

## GUI

The Streamlit app provides:

- date selection;
- stock selection;
- top positive correlations;
- top negative correlations;
- interactive heatmap.

Only the selected date's correlation file is loaded.

## Project structure

```text
stock-correlation-explorer/
â”œâ”€â”€ src/
â”œâ”€â”€ app/
â”œâ”€â”€ tests/
â”œâ”€â”€ sample_data/
â”œâ”€â”€ requirements.txt
â”œâ”€â”€ README.md
â”œâ”€â”€ AI_USAGE.md
â””â”€â”€ AGENTS.md
```

For an actual assessment, update `AI_USAGE.md` to accurately describe how AI was used.


