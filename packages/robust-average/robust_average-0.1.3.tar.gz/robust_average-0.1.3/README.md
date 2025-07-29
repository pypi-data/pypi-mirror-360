# Global-Sourcing-Intelligence

**An Intelligent Sourcing & Profitability Platform for Global SME Traders**

---

## 📌 Overview

**Smart Sourcing Hub** is a modular software solution designed for import/export businesses, global traders, and SME resellers who need better control over supplier deals, shipping costs, market pricing, and profit margins.

The goal is simple: **Buy smart, sell smart, and protect your margins**.

---

## ✅ Key Features

- **Supplier Comparison**
  - Compare offers from auctions, manufacturers, and distributors.
  - Rank deals by price, reliability score, and delivery time.

- **Real-Time Market Data**
  - Pull retail prices in the destination market using local marketplaces, price comparison APIs, or Google Shopping SERP data.
  - Fetch live shipping rates (air, sea, courier) via integrations with Freightos, SeaRates, DHL, and others.
  - Convert foreign currencies using real-time exchange rates.

- **Profitability Protection**
  - Calculate total landed cost per unit.
  - Automatically check profit margins against your target threshold.
  - Generate a “walk-away price” so you never overpay.

- **Deal Decision & Alerts**
  - Approve or reject deals automatically based on profit margin.
  - Generate negotiation templates for suppliers.
  - Send instant alerts to the procurement team.

- **Logistics & Contracting**
  - Calculate shipping weight/volume x quantity.
  - Add local delivery and warehousing costs.
  - Auto-generate purchase orders (POs) with clear terms.

- **Reporting & Dashboard**
  - Real-time dashboard to track profit vs. costs.
  - Export deal reports for management review.
  - Keep a historical log of all suppliers and deals.

- **Future-Ready Add-ons**
  - Traceability tools for supplier compliance.
  - Forecasting with historical data + ML.
  - Fraud detection and risk scoring for trusted partners.

---

## 📊 Robust Average for Price Analysis

### What is Robust Average?
The `robust_average` function is a reusable Python module that intelligently selects the most meaningful average (mean, median, or mode) for a list/Series of prices. It analyzes the data for outliers and skewness, then chooses the best statistical measure to represent the "typical" price, ensuring results are not distorted by extreme values or unusual distributions.

### Why Integrate Robust Average?
- **Real-world price data is often messy:** Scraped prices from APIs or the web can include outliers, errors, or highly skewed distributions.
- **Standard mean can be misleading:** A few very high or low prices can distort the mean, making it unrepresentative of what most buyers actually pay.
- **Business and legal accuracy:** In contracts, reporting, or compliance, using a misleading average can have legal or financial consequences. The robust average ensures you report the most defensible and meaningful value.

### Benefits
- **Automatic selection:** No need to manually inspect data for outliers or skewness—the function does it for you.
- **Transparency:** Returns the method used (mean, median, or mode) and supporting statistics, so you can justify your results.
- **Reusability:** Can be used in any project or analysis where robust, reliable price statistics are needed.
- **Better decision-making:** Ensures that pricing, negotiation, and reporting are based on the most representative data, not distorted by anomalies.

### Decision Logic
The function uses a systematic approach to select the most appropriate average:

1. **Outlier Detection (IQR Method):**
   - Calculates Q1 (25th percentile) and Q3 (75th percentile)
   - Defines outliers as values outside [Q1 - 1.5×IQR, Q3 + 1.5×IQR]
   - IQR = Q3 - Q1

2. **Skewness Analysis:**
   - Calculates the skewness coefficient using scipy.stats.skew()
   - Skewness measures the asymmetry of the data distribution
   - Values close to 0 indicate symmetric distribution

3. **Decision Criteria:**
   - **Use MEAN if:** No outliers AND |skewness| < 0.5 (symmetric, clean data)
   - **Use MEDIAN if:** Outliers present OR |skewness| ≥ 0.5 (skewed or contaminated data)
   - **Use MODE if:** A single value appears in >50% of the dataset (dominant price point)

4. **Mathematical Foundation:**
   - **Mean:** Best for normally distributed data without outliers
   - **Median:** Robust to outliers and skewed distributions
   - **Mode:** Most frequent value, useful for discrete price points

### Example Usage
```python
from robust_average import robust_average
prices = [97.87, 109.99, 129.99, 89.99, 119.99, 500.00]
result = robust_average(prices)
print(result)
# Output: {'value': 109.99, 'method': 'median', ...}
```

---

## ⚙️ Tech Stack

This is a **Python-based project blueprint** — simple to expand with:
- **APIs**: `requests` for HTTP calls to shipping & price services.
- **Data**: `pandas` for logging, exporting reports, and trends.
- **Optional Dashboard**: `Streamlit`, `Dash` or `Flask` for real-time monitoring.
- **Database**: SQLite, PostgreSQL, or any relational DB for storing deals.

---

## 🚀 How It Works (Flow)

1. **STEP 1**: User inputs product details (name, SKU, year, weight, memory, size, quantity, destination, shipping method).
2. **STEP 2**: System fetches market retail prices, shipping costs, and FX rates.
3. **STEP 3**: Calculates total landed costs, profit margin, and walk-away price.
4. **STEP 4**: Compares multiple supplier offers and ranks them.
5. **STEP 5**: Approves or rejects the deal; sends alerts and negotiation suggestions.
6. **STEP 6**: Calculates final logistics costs, generates contract/PO.
7. **STEP 7**: (If agri-export) Matches local suppliers/farmers to international buyers.
8. **STEP 8**: Real-time dashboard and exportable reports.
9. **STEP 9**: Future enhancements like traceability, forecasting, fraud detection.

---

## 🔗 APIs & Integrations

- **Shipping**: Freightos, SeaRates, DHL, UPS, Aramex.
- **Price Comparison**: Local marketplaces (Jumia, Noon, Takealot, Konga), Google Shopping via SerpAPI.
- **FX Rates**: Free services like exchangerate.host or premium FX APIs.
- **Notifications**: Can integrate with email, Slack, or WhatsApp for team alerts.

---

## 🚦 Project Progress

### ✅ Completed
- Environment variable management for API keys (.env, python-dotenv)
- Integration with SerpAPI for product price scraping
- Country/domain lookup using Wikidata and DuckDB
- Flexible, case-insensitive country matching
- Product filtering based on user-specified criteria (name, memory, color)
- Robust average function for meaningful price analysis (mean/median/mode selection)
- Demo and playground scripts for data analysis and testing
- requirements.txt updated for all dependencies

### 🔜 To Do
- Generate and format analysis reports (Step 3 in demo_env.py)
- Save reports to files (Step 4)
- Implement user notification or report delivery (Step 5)
- Add more comprehensive error handling and logging
- Expand data validation and integrity checks
- Build a user interface or dashboard (optional/future)
- Add more unit and integration tests
- Improve documentation and usage examples

---

## 📁 File Structure (Example)

