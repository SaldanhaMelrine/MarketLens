# Stockfolio

Stockfolio is a portfolio analytics dashboard built using Streamlit and Python that enables users to analyze multiple stocks and evaluate portfolio performance through interactive visualizations and risk metrics.

The application emphasizes clean architecture, efficient data storage, and practical financial analytics.

---

## Overview

Stockfolio allows users to compare multiple stocks, simulate an equal-weight portfolio, and analyze performance using commonly used financial metrics such as volatility and drawdown.

Historical market data is stored locally using SQLite to reduce redundant data fetching and improve application performance through caching.

---

## Features

* Multi-stock performance comparison
* Equal-weight portfolio simulation
* Portfolio equity curve visualization
* Volatility analysis
* Maximum drawdown calculation
* Normalized price comparison
* Interactive dashboard using Streamlit
* Cached data loading for faster execution

---

## Tech Stack

**Frontend**

* Streamlit

**Backend**

* Python
* Pandas

**Database**

* SQLite with composite primary key (`ticker`, `date`)

**Deployment**

* Streamlit Cloud

---

## Project Structure

```
stockfolio/
│
├── app.py
├── data/
│   └── ingestion.py
├── db/
│   └── database.py
├── analytics/
│   ├── returns.py
│   ├── risk.py
│   └── portfolio.py
└── ui/
    └── dashboard.py
```

---

## Architecture

The project follows a modular architecture separating responsibilities across independent components:

* Data ingestion layer for market data collection
* Database layer for persistent storage
* Analytics layer for financial computations
* UI layer for visualization and interaction

### Design Decisions

* Modular backend improves scalability and maintainability
* SQLite provides lightweight persistent storage
* Composite primary key prevents duplicate records
* `st.cache_data` minimizes repeated computations
* Analytics logic separated from UI components

---

## Analytics Implemented

* Daily returns
* Cumulative returns
* Portfolio aggregation
* Annualized volatility
* Maximum drawdown
* Equity curve analysis

---

## Data Workflow

1. User selects stock tickers
2. Historical data is fetched or loaded from SQLite
3. Cached datasets are processed
4. Portfolio analytics are computed
5. Results are visualized interactively

---

## Installation

Clone the repository:

```bash
git clone https://github.com/your-username/stockfolio.git
cd stockfolio
```

Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
streamlit run app.py
```

---

## Deployment

The application is deployed using Streamlit Cloud with GitHub integration for continuous deployment.

---

## Future Improvements

* Custom portfolio weighting
* Risk-adjusted performance metrics (Sharpe Ratio, Sortino Ratio)
* Benchmark comparison
* Portfolio rebalancing simulation
* Exportable analytics reports

---

## Motivation

This project was developed to apply software engineering principles such as modular design, database normalization, and performance optimization within a financial analytics application.

---

## License

This project is licensed under the MIT License.
