# 🧠 Parking Predictor – Dev Notes

_Last updated: 2025-06-18_

---

## 🔧 API Architecture

- FastAPI backend hosted at: `https://parking-predictor.onrender.com`
- Connected to MongoDB Atlas via `MONGO_URI`
- Three endpoints:
  - `/lots` – returns static metadata from `lots_static`
  - `/prediction` – returns prediction for one lot at a specific weekday+hour
  - `/availability` – returns predictions for **all lots** at a specific weekday+hour, selects the most likely icon

---

## 🧠 Design Decisions

- **No separate logic for holidays.**
  - Weekdays like `"ערב פסח"` or `"חול המועד"` are treated like any other string.
  - All data (holiday + regular) is stored in the same MongoDB collection: `hourly_predictions`.

- Originally considered using a second collection (`hourly_predictions_holiday`) but did not implement this in the API.

---

## 📦 Mongo Collections

| Collection              | Purpose                     |
|-------------------------|-----------------------------|
| `lots_static`           | Static lot metadata         |
| `hourly_predictions`    | Full prediction data (used in production) |
| `hourly_predictions_holiday` | (Was tested, not used in production) |

---

## 📥 Upload Flow

1. **Generate data:**
   - Replace CSV path in `merge_datasets.py`
   - Run `merge_datasets.py`
   - Run `group_data_by_lot.py` → creates `hourly_predictions.json`

2. **Preview:**
   - Run tests - still to write better `tests.py`
   - Uncomment and use `preview_availability(populated_lots)` to visually inspect structure

3. **Upload:**
   - For regular: `upload_dynamic_to_mongo.py` → uploads with `wipe=True`
   - For holiday: `upload_holidays_to_mongo.py` → also uploads to `hourly_predictions`

4. **Verify API:**
   - Use `/availability?weekday=ערב פסח&hour=15` to test any data point

---

## ✅ Tests Overview

- `tests.py` → manual preview + prediction logic checks
- `/tests/test_api.py` → verifies `/lots` endpoint returns a list
- `test_utils.py` → placeholder
- No automated tests for `/availability` or `/prediction` yet

---

## 💡 Future TODOs
- Add `/health` endpoint to API for easier monitoring
