# \# Stock Correlation Pipeline \& Explorer

# 

# A Python application for calculating and exploring rolling correlations between stock returns.

# 

# The project takes daily stock price data, calculates daily returns, and generates trailing 20-trading-day Pearson correlation matrices. A Streamlit application provides an interactive way to explore the results.

# 

# \## Features

# 

# \- Load daily stock price data from CSV files in a directory or ZIP archive.

# \- Build a date-by-ticker price matrix.

# \- Calculate daily percentage returns.

# \- Calculate rolling 20-trading-day Pearson correlations.

# \- Use vectorised NumPy operations for correlation calculations.

# \- Store correlation matrices efficiently using compressed NumPy arrays.

# \- Explore correlations through an interactive Streamlit application.

# \- Identify the strongest positive and negative correlations for a selected stock.

# 

# \## Project Structure

# 

# ```text

# stock-correlation-pipeline-explorer/

# |

# |-- app/

# |   \\-- streamlit\_app.py

# |

# |-- sample\_data/

# |   \\-- stock\_data/

# |

# |-- src/

# |   |-- loader.py

# |   |-- returns.py

# |   |-- correlation.py

# |   |-- storage.py

# |   \\-- pipeline.py

# |

# |-- tests/

# |   |-- test\_loader.py

# |   |-- test\_returns.py

# |   |-- test\_correlation.py

# |   \\-- test\_storage.py

# |

# |-- requirements.txt

# |-- pytest.ini

# |-- README.md

# \\-- AI\_USAGE.md

# ```

# 

# \## Input Data

# 

# The pipeline accepts either a directory containing daily CSV files or a ZIP archive containing the same files.

# 

# Each CSV is expected to contain the following columns:

# 

# | Column | Description |

# |---|---|

# | Ticker | Stock or instrument identifier |

# | Date | Trading date |

# | Price | Closing price |

# 

# Example:

# 

# ```text

# Ticker,Date,Price

# AAPL,2020-01-01,75.09

# MSFT,2020-01-01,160.62

# GOOG,2020-01-01,71.71

# ```

# 

# The supplied sample data is included in `sample\_data/stock\_data/`.

# 

# \## Correlation Methodology

# 

# Daily simple returns are calculated from consecutive closing prices using percentage changes.

# 

# For each eligible date, the pipeline calculates Pearson correlations using the previous 20 trading-day return observations.

# 

# A 20-observation return window requires 21 price observations.

# 

# The correlation calculation uses NumPy matrix operations rather than iterating through every stock pair individually. This makes the calculation more efficient when working with thousands of instruments.

# 

# \## Missing Data

# 

# Rows without a ticker are excluded because they cannot be associated with an instrument.

# 

# Missing prices are preserved as missing values rather than being filled with estimated prices.

# 

# For a given rolling window, an instrument must have a complete set of return observations to participate in the correlation calculation. Incomplete or constant return series produce undefined correlations where appropriate.

# 

# This avoids introducing artificial values into the results.

# 

# \## Storage

# 

# Correlation matrices are symmetric, meaning the upper and lower triangles contain the same information.

# 

# To avoid storing duplicate values, the pipeline stores only the strict upper triangle of each matrix.

# 

# The correlation values are stored as compressed `float32` NumPy arrays, with ticker metadata stored separately in Parquet format.

# 

# The matrix can be reconstructed when needed by the application.

# 

# \## Getting Started

# 

# \### Requirements

# 

# \- Python 3.10 or later

# \- pip

# 

# \### Installation

# 

# Clone the repository:

# 

# ```bash

# git clone https://github.com/mbarak-beep/stock-correlation-pipeline-explorer.git

# cd stock-correlation-pipeline-explorer

# ```

# 

# Create a virtual environment:

# 

# \*\*Windows PowerShell:\*\*

# 

# ```powershell

# python -m venv .venv

# .venv\\Scripts\\Activate.ps1

# ```

# 

# \*\*macOS / Linux:\*\*

# 

# ```bash

# python -m venv .venv

# source .venv/bin/activate

# ```

# 

# Install the required packages:

# 

# ```bash

# python -m pip install -r requirements.txt

# ```

# 

# \## Running the Pipeline

# 

# To run the pipeline against the included sample data:

# 

# ```bash

# python -m src.pipeline --input sample\_data/stock\_data --output correlation\_output

# ```

# 

# To run it against the full dataset supplied as a ZIP archive:

# 

# ```bash

# python -m src.pipeline --input path/to/stock\_data.zip --output correlation\_output

# ```

# 

# The pipeline loads the data, calculates daily returns, generates the rolling correlation matrices and saves the results to the specified output directory.

# 

# \## Launching the Explorer

# 

# Once the pipeline has generated the correlation files, start the Streamlit application:

# 

# ```bash

# streamlit run app/streamlit\_app.py

# ```

# 

# Open the local URL printed in the terminal. By default, this is:

# 

# ```text

# http://localhost:8501

# ```

# 

# The application allows you to:

# 

# \- Select a trading date.

# \- Choose an individual stock.

# \- View its strongest positive correlations.

# \- View its strongest negative correlations.

# \- Explore relationships through an interactive correlation heatmap.

# 

# Only the selected date's correlation data is loaded by the explorer.

# 

# \## Running the Tests

# 

# Run the automated test suite from the project root:

# 

# ```bash

# pytest -q

# ```

# 

# The tests cover:

# 

# \- CSV data loading and validation.

# \- Daily return calculations.

# \- Rolling correlation calculations.

# \- Correlation matrix storage and reconstruction.

# 

# \## Dependencies

# 

# The project dependencies and required Python packages are listed in `requirements.txt`.

