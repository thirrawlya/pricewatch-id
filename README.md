# PriceWatchID

> Buying intelligence platform for e-commerce price tracking on Tokopedia.

**Live demo:** _localhost (self-hosted)_ &nbsp;·&nbsp; **Stack:** Python · FastAPI · SQLite · Playwright · React

---

## What it does

PriceWatchID helps users decide **when** to buy, not just where.

Instead of showing a single price snapshot, it tracks historical price data and surfaces buying signals:

- Is the current price above or below the 30-day average?
- Is this near the historical low?
- Should I buy now or wait?

---

## Features

- **Tokopedia scraper** — automated price collection via Playwright
- **REST API** — FastAPI backend with `/products` and `/analytics` endpoints
- **Analytics engine** — calculates current, average, lowest, highest price + % change
- **Buy score** — 0–100 score based on price position relative to historical range
- **Recommendation** — "Good time to buy", "Wait", or "Neutral" with reasoning
- **Dashboard** — React frontend with area chart, stat cards, and price history table

---

## Tech Stack

| Layer | Technology |
|---|---|
| Scraping | Python, Playwright |
| Backend | FastAPI, SQLite |
| Analytics | Custom Python logic |
| Frontend | React, Vite, Recharts, Tailwind CSS |

---

## API Endpoints

```
GET /products
GET /products/{id}/prices
GET /products/{id}/analytics?days=30
```

The `/analytics` endpoint returns:

```json
{
  "current": 4098000,
  "average": 4428000,
  "lowest": 3950000,
  "highest": 4800000,
  "change_pct": -7.4,
  "recommendation": "good_buy",
  "reason": "Price is 7.4% below 30-day average",
  "history": []
}
```

---

## Project Structure

```
pricewatch-id/
├── backend/        # FastAPI app + analytics logic
├── frontend/       # React + Vite dashboard
├── experiments/    # Scraper, parser, scheduler
├── data/           # SQLite database + backups
└── docs/           # Project analysis docs
```

---

## Data Model

```sql
products        -- id, name, url, marketplace, created_at
price_history   -- id, product_id, price, rating, sold, store, timestamp
```

---

## Running locally

```bash
# Backend
cd backend
source ../venv/bin/activate
uvicorn main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

---

## Status

| Component | Status |
|---|---|
| Scraper | ✅ Working |
| Database | ✅ 400+ products, price history collected |
| API | ✅ Endpoints live |
| Analytics | ✅ Buy score + recommendation |
| Dashboard | ✅ Chart + stats + history table |

---

## License

MIT
