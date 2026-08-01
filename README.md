# PriceWatchID
> Buying intelligence platform focused on skincare products in the Indonesian marketplace.

---

## Overview
PriceWatchID helps consumers make more confident buying decisions through:
* price history tracking
* store trust signals
* buying timing insights

starting with skincare products listed on Tokopedia.

The core premise:
> Consumers don't need the cheapest option.
> They need the most confident buying decision.

---

## My Role

This is a solo project. My role centers on **product direction and decision-making**, not raw code output:

* Defined the problem, target users, and product philosophy (data-first, calm intelligence — see Design Principles)
* Designed the phased roadmap (Phase 0 validation before any application features) and decided what to build vs. defer
* Directed AI-assisted development — I brief the approach, review generated code, and iterate based on what fits the product's direction
* Made the calls on structure, trade-offs, and quality — what's good enough to ship vs. what needs rework
* Validated outputs against the actual goal (e.g., data reliability before UI work), not just "does it run"

Code implementation is AI-assisted; the product thinking, requirements, and judgment calls are mine.

---

## Current Status
**Phase 0 — Data Layer Validation**

| Milestone                                      | Status         |
| ---------------------------------------------- | -------------- |
| Tokopedia scraper (Playwright)                 | ✅ Completed    |
| Extract product metadata (price, rating, sold) | 🔄 In progress |
| Persist historical data to SQLite              | ⏳ Pending      |
| Scheduled collection pipeline (6h interval)    | ⏳ Pending      |
| Price history validation chart                 | ⏳ Pending      |

> Application development is intentionally blocked until data reliability is proven.

---

## Repository Structure
```txt
pricewatch-id/
├── scraper/            # Scraping & data collection pipeline
├── backend/            # FastAPI application layer
├── frontend/           # React + Vite frontend
├── data/               # Database, migrations, seeds
├── docs/               # Project analysis & reliability docs
└── README.md
```

---

## Tech Stack

### Phase 0 — Validation Layer
| Layer      | Technology         |
| ---------- | ------------------ |
| Scraping   | Python, Playwright |
| Parsing    | BeautifulSoup4     |
| Storage    | SQLite             |
| Scheduling | APScheduler        |

### Phase 1 — Application Layer
| Layer      | Technology                |
| ---------- | ------------------------- |
| Frontend   | React, Vite, Tailwind CSS |
| Backend    | FastAPI                   |
| Database   | PostgreSQL                |
| Deployment | TBD                       |

---

## Core Data Model
```sql
products
  id
  name
  url
  marketplace
  created_at

price_history
  id
  product_id
  price
  rating
  sold
  store
  timestamp
```

---

## Development Roadmap

### Phase 0 — Validate Data Acquisition
Prove marketplace price data can be reliably collected,
parsed, and stored before building application features.

### Phase 1 — Minimal Product Experience
Single product page with:
* price history chart
* store comparison
* buying signals

### Phase 2 — Watchlist & Alerts
* tracked products
* price threshold alerts
* account system

---

## Design Principles
* **Data first** — infrastructure before interface
* **Calm intelligence** — analytical, not promotional
* **Restraint** — fewer features, higher trust
* **Utility over hype** — avoid unnecessary AI claims or growth mechanics

---

## License
MIT
