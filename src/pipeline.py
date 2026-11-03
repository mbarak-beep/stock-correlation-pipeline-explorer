from __future__ import annotations

import argparse
from pathlib import Path

from .loader import load_prices, build_price_matrix
from .returns import daily_returns, trailing_return_window
from .correlation import correlation_matrix
from .storage import save_correlation, save_metadata


def run(input_path: str, output_dir: str, window: int = 20) -> None:
    print(f"Loading data from {input_path}...")
    data = load_prices(input_path)
    prices = build_price_matrix(data)

    print(
        f"Loaded {len(prices):,} trading dates and "
        f"{prices.shape[1]:,} tickers."
    )

    returns = daily_returns(prices)
    tickers = list(prices.columns)
    save_metadata(output_dir, tickers)

    first_position = window
    total = len(returns) - first_position

    if total <= 0:
        raise ValueError("Not enough trading dates for the requested window.")

    for count, position in enumerate(
        range(first_position, len(returns)), start=1
    ):
        date = returns.index[position]
        window_df = trailing_return_window(returns, position, window)
        corr = correlation_matrix(window_df)
        save_correlation(output_dir, date, corr)

        if count == 1 or count % 10 == 0 or count == total:
            print(f"[{count:>5}/{total}] {date:%Y-%m-%d}")

    print(f"Finished. Output written to {Path(output_dir).resolve()}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Stock correlation pipeline")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--window", type=int, default=20)
    args = parser.parse_args()

    run(args.input, args.output, args.window)


if __name__ == "__main__":
    main()
