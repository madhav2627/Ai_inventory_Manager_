"""
Autonomous AI Inventory Intelligence Engine
--------------------------------------------
Runs 100% offline. No cloud APIs. Uses scikit-learn, pandas, numpy,
and SQLite to power 9 intelligent inventory management modules:

1. Demand Forecasting
2. Predictive Stock Detection
3. Restocking Recommendations
4. Anomaly & Fraud Detection
5. Natural Language Inventory Actions
6. Multi-Warehouse Optimization
7. Purchase Order Generation
8. Dead Stock & Slow-Moving Detection
9. Unified Intelligence Report
"""
import json
import re
from datetime import datetime, timedelta
from collections import defaultdict

import numpy as np
import pandas as pd

from ml.predict import get_intelligence


# ── 1. Demand Forecasting ─────────────────────────────────────────────────

def get_demand_forecast(conn, intel=None):
    """
    Returns per-product demand predictions for next day, week, and month.
    Uses the existing ML model / heuristic pipeline from predict.py.
    """
    if intel is None:
        intel = get_intelligence(conn)
    forecasts = []
    for pid, info in intel.items():
        daily = info["predicted_daily_demand"]
        forecasts.append({
            "product_id": pid,
            "name": info["name"],
            "stock_qty": info["stock_qty"],
            "daily_demand": daily,
            "weekly_demand": round(daily * 7, 1),
            "monthly_demand": round(daily * 30, 1),
            "method": info["method"],
        })
    # Sort by daily demand descending
    forecasts.sort(key=lambda x: x["daily_demand"], reverse=True)
    return forecasts


# ── 2. Predictive Stock Detection ─────────────────────────────────────────

def get_stockout_predictions(conn, intel=None):
    """
    Classifies each product into urgency tiers:
      - critical: ≤3 days to stockout
      - warning:  ≤7 days to stockout
      - caution:  ≤14 days to stockout
      - safe:     >14 days or no demand
    """
    if intel is None:
        intel = get_intelligence(conn)
    predictions = []
    for pid, info in intel.items():
        days = info["days_to_stockout"]
        if days is None:
            urgency = "safe"
        elif days <= 3:
            urgency = "critical"
        elif days <= 7:
            urgency = "warning"
        elif days <= 14:
            urgency = "caution"
        else:
            urgency = "safe"

        predictions.append({
            "product_id": pid,
            "name": info["name"],
            "stock_qty": info["stock_qty"],
            "reorder_level": info["reorder_level"],
            "days_to_stockout": days,
            "daily_demand": info["predicted_daily_demand"],
            "urgency": urgency,
        })
    # Sort critical first
    order = {"critical": 0, "warning": 1, "caution": 2, "safe": 3}
    predictions.sort(key=lambda x: (order.get(x["urgency"], 4), x["days_to_stockout"] or 9999))
    return predictions


# ── 3. Restocking Recommendations ─────────────────────────────────────────

def get_restock_recommendations(conn, settings, intel=None, user_id=None):
    """
    Calculates optimal reorder quantities using:
      reorder_qty = max(0, (daily_demand × lead_time × safety_multiplier) + reorder_level − current_stock)
    Only recommends restocking for products below or near reorder level.
    """
    lead_time = float(settings.get("lead_time_days", "3"))
    safety_mult = float(settings.get("safety_stock_multiplier", "1.5"))
    if intel is None:
        intel = get_intelligence(conn, user_id=user_id)
    recommendations = []

    for pid, info in intel.items():
        daily = info["predicted_daily_demand"]
        stock = info["stock_qty"]
        reorder_lvl = info["reorder_level"]

        # Calculate safety stock
        safety_stock = daily * lead_time * safety_mult
        target_stock = safety_stock + reorder_lvl
        reorder_qty = max(0, round(target_stock - stock, 1))

        if reorder_qty > 0 or stock <= reorder_lvl:
            # Fetch cost price for total calculation
            if user_id is None:
                row = conn.execute(
                    "SELECT cost_price, category FROM products WHERE id = ?", (pid,)
                ).fetchone()
            else:
                row = conn.execute(
                    "SELECT cost_price, category FROM products WHERE id = ? AND user_id = ?",
                    (pid, user_id),
                ).fetchone()
            cost = row["cost_price"] if row else 0
            category = row["category"] if row else "General"

            if reorder_qty == 0:
                reorder_qty = max(1, reorder_lvl)

            recommendations.append({
                "product_id": pid,
                "name": info["name"],
                "category": category,
                "current_stock": stock,
                "reorder_level": reorder_lvl,
                "daily_demand": daily,
                "recommended_qty": reorder_qty,
                "estimated_cost": round(reorder_qty * cost, 2),
                "unit_cost": cost,
                "days_to_stockout": info["days_to_stockout"],
            })

    recommendations.sort(key=lambda x: x["days_to_stockout"] or 9999)
    return recommendations


# ── 4. Anomaly & Fraud Detection ──────────────────────────────────────────

def detect_anomalies(conn, user_id=None):
    """
    Uses z-score analysis on:
      - Daily sales volume per product (sudden spikes)
      - Transaction discount amounts (unusually high discounts)
      - Stock adjustments (unexplained shrinkage)
    Returns a list of anomaly alerts with severity.
    """
    anomalies = []

    # ---- Sales volume anomalies ----
    sales_query = """
        SELECT ti.product_id, p.name, date(t.created_at) AS sale_date,
               SUM(ti.quantity) AS daily_qty
        FROM transaction_items ti
        JOIN transactions t ON t.id = ti.transaction_id
        JOIN products p ON p.id = ti.product_id
        WHERE ti.product_id IS NOT NULL
          AND date(t.created_at) >= date('now', 'localtime', '-60 days')
    """
    sales_params = []
    if user_id is not None:
        sales_query += " AND t.user_id = ?"
        sales_params.append(user_id)
    sales_query += " GROUP BY ti.product_id, p.name, date(t.created_at)"
    sales_df = pd.read_sql_query(sales_query, conn, params=sales_params)

    if not sales_df.empty:
        for pid, group in sales_df.groupby("product_id"):
            if len(group) < 3:
                continue
            mean_qty = group["daily_qty"].mean()
            std_qty = group["daily_qty"].std()
            if std_qty == 0:
                continue
            name = group["name"].iloc[0]
            for _, row in group.iterrows():
                z = (row["daily_qty"] - mean_qty) / std_qty
                if z > 2.5:
                    anomalies.append({
                        "type": "sales_spike",
                        "severity": "high" if z > 3.5 else "medium",
                        "product_id": int(pid),
                        "product_name": name,
                        "date": row["sale_date"],
                        "detail": f"Sold {row['daily_qty']:.0f} units (avg: {mean_qty:.1f}, z-score: {z:.1f})",
                        "z_score": round(z, 2),
                    })

    # ---- Discount anomalies ----
    discount_query = """
        SELECT id, invoice_no, date(created_at) AS txn_date,
               subtotal, discount, total
        FROM transactions
        WHERE discount > 0
          AND date(created_at) >= date('now', 'localtime', '-60 days')
    """
    discount_params = []
    if user_id is not None:
        discount_query += " AND user_id = ?"
        discount_params.append(user_id)
    disc_df = pd.read_sql_query(discount_query, conn, params=discount_params)

    if not disc_df.empty and len(disc_df) >= 3:
        disc_df["disc_pct"] = (disc_df["discount"] / disc_df["subtotal"].replace(0, 1)) * 100
        mean_disc = disc_df["disc_pct"].mean()
        std_disc = disc_df["disc_pct"].std()
        if std_disc > 0:
            for _, row in disc_df.iterrows():
                z = (row["disc_pct"] - mean_disc) / std_disc
                if z > 2.0:
                    anomalies.append({
                        "type": "high_discount",
                        "severity": "high" if z > 3.0 else "medium",
                        "product_id": None,
                        "product_name": f"Invoice {row['invoice_no']}",
                        "date": row["txn_date"],
                        "detail": f"Discount {row['disc_pct']:.1f}% (avg: {mean_disc:.1f}%, z-score: {z:.1f})",
                        "z_score": round(z, 2),
                    })

    # ---- Stock shrinkage anomalies ----
    adjustment_query = """
        SELECT sa.product_id, p.name, sa.change_qty, sa.reason,
               date(sa.created_at) AS adj_date
        FROM stock_adjustments sa
        JOIN products p ON p.id = sa.product_id
        WHERE sa.change_qty < 0
          AND date(sa.created_at) >= date('now', 'localtime', '-60 days')
    """
    adjustment_params = []
    if user_id is not None:
        adjustment_query += " AND sa.user_id = ?"
        adjustment_params.append(user_id)
    adj_df = pd.read_sql_query(adjustment_query, conn, params=adjustment_params)

    if not adj_df.empty and len(adj_df) >= 2:
        mean_adj = adj_df["change_qty"].mean()
        std_adj = adj_df["change_qty"].std()
        if std_adj > 0:
            for _, row in adj_df.iterrows():
                z = (row["change_qty"] - mean_adj) / std_adj
                if z < -2.0:  # Unusually large negative adjustment
                    anomalies.append({
                        "type": "stock_shrinkage",
                        "severity": "high" if z < -3.0 else "medium",
                        "product_id": int(row["product_id"]),
                        "product_name": row["name"],
                        "date": row["adj_date"],
                        "detail": f"Removed {abs(row['change_qty']):.0f} units — {row['reason'] or 'no reason given'}",
                        "z_score": round(abs(z), 2),
                    })

    # Sort by date descending, then severity
    sev_order = {"high": 0, "medium": 1, "low": 2}
    anomalies.sort(key=lambda x: (sev_order.get(x["severity"], 3), x["date"] or ""), reverse=False)
    return anomalies


# ── 5. Dead Stock & Slow-Moving Detection ─────────────────────────────────

def detect_dead_slow_stock(conn, settings, user_id=None):
    """
    Dead stock:    Products with ZERO sales in the last `dead_stock_days` days.
    Slow-moving:   Products sold less than their average daily demand × 0.3 threshold
                   over the last `slow_moving_days` days.
    """
    dead_days = int(settings.get("dead_stock_days", "60"))
    slow_days = int(settings.get("slow_moving_days", "30"))

    # All products
    if user_id is None:
        products = conn.execute("SELECT id, name, stock_qty, cost_price, category FROM products").fetchall()
    else:
        products = conn.execute(
            "SELECT id, name, stock_qty, cost_price, category FROM products WHERE user_id = ?", (user_id,)
        ).fetchall()

    # Sales in dead_stock window
    sales_query = f"""
        SELECT ti.product_id, SUM(ti.quantity) AS total_sold
        FROM transaction_items ti
        JOIN transactions t ON t.id = ti.transaction_id
        WHERE date(t.created_at) >= date('now', 'localtime', '-{dead_days} days')
    """
    sales_params = []
    if user_id is not None:
        sales_query += " AND t.user_id = ?"
        sales_params.append(user_id)
    sales_query += " GROUP BY ti.product_id"
    sales = pd.read_sql_query(sales_query, conn, params=sales_params)
    sold_map = dict(zip(sales["product_id"], sales["total_sold"])) if not sales.empty else {}

    # Sales in slow_moving window
    slow_query = f"""
        SELECT ti.product_id, SUM(ti.quantity) AS total_sold
        FROM transaction_items ti
        JOIN transactions t ON t.id = ti.transaction_id
        WHERE date(t.created_at) >= date('now', 'localtime', '-{slow_days} days')
    """
    slow_params = []
    if user_id is not None:
        slow_query += " AND t.user_id = ?"
        slow_params.append(user_id)
    slow_query += " GROUP BY ti.product_id"
    slow_sales = pd.read_sql_query(slow_query, conn, params=slow_params)
    slow_map = dict(zip(slow_sales["product_id"], slow_sales["total_sold"])) if not slow_sales.empty else {}

    dead_stock = []
    slow_moving = []

    for p in products:
        pid = p["id"]
        total_sold_dead = sold_map.get(pid, 0)
        total_sold_slow = slow_map.get(pid, 0)
        stock_val = p["stock_qty"] * p["cost_price"]

        if total_sold_dead == 0 and p["stock_qty"] > 0:
            dead_stock.append({
                "product_id": pid,
                "name": p["name"],
                "category": p["category"],
                "stock_qty": p["stock_qty"],
                "stock_value": round(stock_val, 2),
                "days_checked": dead_days,
                "units_sold": 0,
            })
        elif total_sold_slow > 0 and p["stock_qty"] > 0:
            avg_daily = total_sold_slow / slow_days
            # Slow-moving: selling less than 0.3 units per day on average
            if avg_daily < 0.3:
                slow_moving.append({
                    "product_id": pid,
                    "name": p["name"],
                    "category": p["category"],
                    "stock_qty": p["stock_qty"],
                    "stock_value": round(stock_val, 2),
                    "days_checked": slow_days,
                    "units_sold": total_sold_slow,
                    "avg_daily": round(avg_daily, 3),
                })

    dead_stock.sort(key=lambda x: x["stock_value"], reverse=True)
    slow_moving.sort(key=lambda x: x["avg_daily"])
    return {"dead_stock": dead_stock, "slow_moving": slow_moving}


# ── 6. Natural Language Inventory Actions ─────────────────────────────────

COMMAND_SUGGESTIONS = [
    "show critical stock",
    "what needs restocking",
    "sales today",
    "top selling products",
    "demand forecast",
    "expiring soon",
]


def _normalize_command(query):
    """Normalise harmless language variations before classifying an intent."""
    normalized = query.strip().lower()
    normalized = normalized.replace("’", "'")
    normalized = re.sub(r"[?!.]+", " ", normalized)
    normalized = re.sub(r"[-_/]+", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized.strip()


def _classify_command(query):
    """Classify inventory questions by meaning, without requiring word order."""
    words = set(query.split())
    has = lambda *terms: any(term in query for term in terms)

    if has("help", "what can you", "what do you", "commands", "examples"):
        return "help"
    if has("critical", "urgent", "immediate risk", "stockout", "stock out"):
        return "critical_stock"
    if has("at risk", "needs attention", "warning", "warnings"):
        return "at_risk_stock"
    if has("low stock", "running low", "out of stock", "low inventory", "reorder level"):
        return "low_stock"
    if has("expiring", "expiry", "expire soon", "expired"):
        return "expiry_alerts"
    if has("dead stock", "dead inventory", "not selling"):
        return "dead_stock"
    if has("slow moving", "slow mover", "slow selling"):
        return "slow_moving"
    if has("anomal", "fraud", "suspicious", "unusual activity"):
        return "anomalies"
    if has("warehouse", "warehouses", "location", "transfer"):
        return "warehouse_info"
    if has("restock", "reorder", "re order", "purchase order", "what should i order", "what to order", "replenish", "recommendation"):
        return "restock"
    if has("forecast", "demand", "predict", "prediction", "next week", "next month"):
        return "demand_forecast"
    if has("best seller", "best selling", "top selling", "most sold", "popular product", "fast moving"):
        return "top_selling"
    if has("sales", "revenue", "earned", "income", "turnover"):
        if "yesterday" in words:
            return "sales_yesterday"
        if has("week", "weekly", "last 7"):
            return "sales_week"
        if has("month", "monthly", "last 30"):
            return "sales_month"
        return "sales_today"
    if has("health", "overall status", "inventory status", "inventory summary", "overview"):
        return "health_check"
    if has("stock of", "stock for", "quantity of", "quantity for", "do we have", "is there", "find", "search", "look up", "details of", "details for", "about"):
        return "product_search"
    return None


def _product_search_term(query):
    """Remove conversational scaffolding so product lookup uses only the item name."""
    term = query.strip(" '\"")
    term = re.sub(
        r"^(?:please\s+)?(?:can you\s+)?(?:tell me\s+)?(?:show|find|search(?: for)?|look up|check)\s+",
        "", term,
    )
    term = re.sub(
        r"^(?:how much|what is|what's)\s+(?:stock|quantity|inventory)\s+(?:do we have\s+)?(?:of|for)?\s*",
        "", term,
    )
    term = re.sub(
        r"^(?:stock|quantity|inventory|details|information|info)\s+(?:of|for|about)?\s*",
        "", term,
    )
    term = re.sub(r"^(?:do we have|is there)\s+(?:any\s+)?", "", term)
    term = re.sub(r"\s+(?:in stock|available|please)$", "", term)
    return term.strip(" '\"")


def _looks_like_product_name(query):
    """Keep a product-name lookup useful without mislabelling unrelated questions."""
    words = query.split()
    unsupported = {
        "hello", "hi", "hey", "why", "when", "where", "who", "how", "can", "could", "should",
        "explain", "make", "create", "weather", "news", "joke", "recipe", "code", "anything",
    }
    return bool(words) and len(words) <= 5 and not any(word in unsupported for word in words)


def _sales_summary(conn, user_id, date_condition, label, settings):
    row = conn.execute(
        f"SELECT COALESCE(SUM(total),0) AS total, COUNT(*) AS cnt FROM transactions WHERE {date_condition} AND user_id = ?",
        (user_id,),
    ).fetchone()
    currency = settings.get("currency_symbol", "₹")
    return {
        "total": row["total"],
        "count": row["cnt"],
        "response": f"{label}: {currency}{row['total']:,.2f} across {row['cnt']} transaction(s).",
    }


def parse_natural_language(query, conn, settings, user_id=None):
    """Answer supported inventory questions with a deliberate, user-scoped response."""
    query_normalized = _normalize_command(query)
    matched_action = _classify_command(query_normalized)
    product_term = _product_search_term(query_normalized)

    if not matched_action and _looks_like_product_name(product_term):
        matched_action = "product_search"

    result = {
        "action": matched_action or "unsupported",
        "query": query,
        "response": "",
        "data": [],
        "suggestions": COMMAND_SUGGESTIONS,
    }

    if matched_action == "low_stock":
        rows = conn.execute(
            """SELECT id, name, stock_qty, reorder_level, unit_label
               FROM products WHERE stock_qty <= reorder_level AND user_id = ?
               ORDER BY stock_qty ASC, name ASC""",
            (user_id,),
        ).fetchall()
        result["data"] = [dict(r) for r in rows]
        result["response"] = f"Found {len(rows)} product(s) at or below their reorder level." if rows else "All of your products are above their reorder levels. ✓"

    elif matched_action == "critical_stock":
        preds = get_stockout_predictions(conn, intel=get_intelligence(conn, user_id=user_id))
        critical = [p for p in preds if p["urgency"] == "critical"]
        result["data"] = critical
        result["response"] = f"{len(critical)} product(s) are critical and may stock out within 3 days." if critical else "No products are currently in critical stock status. ✓"

    elif matched_action == "at_risk_stock":
        preds = get_stockout_predictions(conn, intel=get_intelligence(conn, user_id=user_id))
        at_risk = [p for p in preds if p["urgency"] in ("critical", "warning", "caution")]
        result["data"] = at_risk
        result["response"] = f"{len(at_risk)} product(s) need attention based on predicted stockout timing." if at_risk else "No products currently need attention. ✓"

    elif matched_action == "expiry_alerts":
        rows = conn.execute(
            """SELECT id, name, stock_qty, unit_label, expiry_date
               FROM products
               WHERE user_id = ? AND expiry_date IS NOT NULL AND expiry_date != ''
                 AND date(expiry_date) <= date('now', 'localtime', '+30 days')
               ORDER BY date(expiry_date) ASC, name ASC""",
            (user_id,),
        ).fetchall()
        result["data"] = [dict(r) for r in rows]
        result["response"] = f"Found {len(rows)} product(s) expired or expiring within 30 days." if rows else "No products are expired or expiring within the next 30 days. ✓"

    elif matched_action == "dead_stock":
        ds = detect_dead_slow_stock(conn, settings, user_id=user_id)
        result["data"] = ds["dead_stock"]
        result["response"] = f"Found {len(ds['dead_stock'])} dead-stock item(s) with no sales in the configured period."

    elif matched_action == "slow_moving":
        ds = detect_dead_slow_stock(conn, settings, user_id=user_id)
        result["data"] = ds["slow_moving"]
        result["response"] = f"Found {len(ds['slow_moving'])} slow-moving product(s)."

    elif matched_action == "anomalies":
        anomalies = detect_anomalies(conn, user_id=user_id)
        result["data"] = anomalies
        result["response"] = f"Detected {len(anomalies)} unusual pattern(s) in recent activity." if anomalies else "No unusual sales, discounts, or stock adjustments were detected. ✓"

    elif matched_action == "sales_today":
        summary = _sales_summary(conn, user_id, "date(created_at) = date('now', 'localtime')", "Today's sales", settings)
        result["data"] = {"total": summary["total"], "count": summary["count"]}
        result["response"] = summary["response"]

    elif matched_action == "sales_yesterday":
        summary = _sales_summary(conn, user_id, "date(created_at) = date('now', 'localtime', '-1 day')", "Yesterday's sales", settings)
        result["data"] = {"total": summary["total"], "count": summary["count"]}
        result["response"] = summary["response"]

    elif matched_action == "sales_week":
        summary = _sales_summary(conn, user_id, "date(created_at) >= date('now', 'localtime', '-6 days')", "Sales in the last 7 days", settings)
        result["data"] = {"total": summary["total"], "count": summary["count"]}
        result["response"] = summary["response"]

    elif matched_action == "sales_month":
        summary = _sales_summary(conn, user_id, "date(created_at) >= date('now', 'localtime', '-29 days')", "Sales in the last 30 days", settings)
        result["data"] = {"total": summary["total"], "count": summary["count"]}
        result["response"] = summary["response"]

    elif matched_action == "top_selling":
        rows = conn.execute("""
            SELECT ti.product_name, SUM(ti.quantity) AS total_qty, SUM(ti.line_total) AS total_revenue
            FROM transaction_items ti
            JOIN transactions t ON t.id = ti.transaction_id
            WHERE date(t.created_at) >= date('now', 'localtime', '-29 days') AND t.user_id = ?
            GROUP BY ti.product_name ORDER BY total_revenue DESC LIMIT 10
        """, (user_id,)).fetchall()
        result["data"] = [dict(r) for r in rows]
        result["response"] = f"Top {len(rows)} selling product(s) in the last 30 days:" if rows else "No sales data is available yet."

    elif matched_action == "demand_forecast":
        intel = get_intelligence(conn, user_id=user_id)
        forecast = get_demand_forecast(conn, intel=intel)[:10]
        result["data"] = forecast
        result["response"] = f"Demand forecast for {len(forecast)} product(s):" if forecast else "There are no products to forecast yet."

    elif matched_action == "restock":
        intel = get_intelligence(conn, user_id=user_id)
        recs = get_restock_recommendations(conn, settings, intel=intel, user_id=user_id)
        result["data"] = recs
        result["response"] = f"{len(recs)} product(s) need replenishing." if recs else "All of your products are adequately stocked. ✓"

    elif matched_action == "health_check":
        preds = get_stockout_predictions(conn, intel=get_intelligence(conn, user_id=user_id))
        critical = sum(1 for p in preds if p["urgency"] == "critical")
        warning = sum(1 for p in preds if p["urgency"] == "warning")
        safe = sum(1 for p in preds if p["urgency"] == "safe")
        result["data"] = {"critical": critical, "warning": warning, "safe": safe, "total": len(preds)}
        result["response"] = f"Inventory health: {critical} critical, {warning} warning, and {safe} safe out of {len(preds)} product(s)."

    elif matched_action == "warehouse_info":
        warehouses = get_warehouse_optimization(conn, user_id=user_id)
        result["data"] = warehouses["warehouses"]
        result["response"] = warehouses["message"]

    elif matched_action == "product_search":
        search_term = product_term or query_normalized
        rows = conn.execute(
            """SELECT id, name, category, stock_qty, unit_label, unit_price, reorder_level
               FROM products WHERE user_id = ? AND name LIKE ?
               ORDER BY name ASC LIMIT 10""",
            (user_id, f"%{search_term}%"),
        ).fetchall()
        result["data"] = [dict(r) for r in rows]
        if rows:
            result["response"] = f"Found {len(rows)} product(s) matching “{search_term}”."
        else:
            result["response"] = f"I could not find a product matching “{search_term}”. Try a shorter name, brand, or barcode."

    elif matched_action == "help":
        result["response"] = (
            "I can answer inventory questions such as:\n"
            "• show critical stock / what needs attention\n"
            "• what needs restocking / create a purchase order\n"
            "• sales today, yesterday, this week, or this month\n"
            "• top selling products / demand forecast\n"
            "• show anomalies, dead stock, slow-moving items, or expiring soon\n"
            "• stock of [product name]"
        )

    else:
        result["response"] = "I can help with your store’s inventory, sales, forecasts, restocking, expiry, and product lookups. Choose a suggestion below or ask for help."

    return result


# ── 7. Multi-Warehouse Optimization ───────────────────────────────────────

def get_warehouse_optimization(conn, user_id=None):
    """
    Analyzes stock distribution across warehouses and suggests transfers
    to balance levels. If only one warehouse exists, returns basic info.
    """
    if user_id is None:
        warehouses = conn.execute("SELECT * FROM warehouses ORDER BY is_default DESC").fetchall()
    else:
        warehouses = conn.execute(
            "SELECT * FROM warehouses WHERE user_id = ? ORDER BY is_default DESC", (user_id,)
        ).fetchall()
    if len(warehouses) < 2:
        return {
            "warehouses": [dict(w) for w in warehouses] if warehouses else [],
            "suggestions": [],
            "message": "Add multiple warehouses to enable stock transfer optimization."
        }

    # Get stock per warehouse per product
    stock_query = """
        SELECT pw.warehouse_id, w.name AS warehouse_name,
               pw.product_id, p.name AS product_name,
               pw.stock_qty, p.reorder_level
        FROM product_warehouse pw
        JOIN warehouses w ON w.id = pw.warehouse_id
        JOIN products p ON p.id = pw.product_id
    """
    stock_params = []
    if user_id is not None:
        stock_query += " WHERE w.user_id = ? AND p.user_id = ?"
        stock_params = [user_id, user_id]
    stock_dist = pd.read_sql_query(stock_query, conn, params=stock_params)

    suggestions = []
    if not stock_dist.empty:
        for pid, group in stock_dist.groupby("product_id"):
            if len(group) < 2:
                continue
            mean_stock = group["stock_qty"].mean()
            reorder = group["reorder_level"].iloc[0]
            product_name = group["product_name"].iloc[0]

            overstocked = group[group["stock_qty"] > mean_stock * 1.5]
            understocked = group[group["stock_qty"] < reorder]

            for _, under in understocked.iterrows():
                for _, over in overstocked.iterrows():
                    transfer_qty = min(
                        over["stock_qty"] - mean_stock,
                        reorder - under["stock_qty"]
                    )
                    if transfer_qty > 0:
                        suggestions.append({
                            "product_id": int(pid),
                            "product_name": product_name,
                            "from_warehouse_id": int(over["warehouse_id"]),
                            "from_warehouse": over["warehouse_name"],
                            "to_warehouse_id": int(under["warehouse_id"]),
                            "to_warehouse": under["warehouse_name"],
                            "quantity": round(transfer_qty, 1),
                            "reason": f"Balance stock (from {over['stock_qty']:.0f} → {under['stock_qty']:.0f})"
                        })

    return {
        "warehouses": [dict(w) for w in warehouses],
        "suggestions": suggestions,
        "message": f"{len(suggestions)} transfer suggestion(s) to optimize stock distribution."
    }


# ── 8. Purchase Order Generation ──────────────────────────────────────────

def generate_purchase_orders(conn, settings, user_id=1):
    """
    Auto-generates purchase order drafts for products that need restocking,
    grouped by product category (acting as supplier proxy).
    Returns the created PO IDs.
    """
    from database import now_iso

    intel = get_intelligence(conn, user_id=user_id)
    recs = get_restock_recommendations(conn, settings, intel=intel, user_id=user_id)
    if not recs:
        return {"created": 0, "po_ids": [], "message": "No products need restocking."}

    # Group by category
    grouped = defaultdict(list)
    for r in recs:
        grouped[r["category"]].append(r)

    po_prefix = settings.get("po_prefix", "PO")
    po_counter = int(settings.get("po_counter", "1"))
    created_pos = []

    for category, items in grouped.items():
        po_number = f"{po_prefix}-{po_counter:04d}"
        total_cost = sum(i["estimated_cost"] for i in items)
        now = now_iso()

        cur = conn.execute(
            """INSERT INTO purchase_orders (user_id, po_number, status, supplier_name, total_cost, notes, created_at, updated_at)
               VALUES (?, ?, 'draft', ?, ?, ?, ?, ?)""",
            (user_id, po_number, f"{category} Supplier", round(total_cost, 2),
             f"Auto-generated by AI agent for {len(items)} product(s)", now, now)
        )
        po_id = cur.lastrowid

        for item in items:
            line_total = round(item["recommended_qty"] * item["unit_cost"], 2)
            conn.execute(
                """INSERT INTO purchase_order_items (po_id, product_id, product_name, quantity, unit_cost, line_total)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (po_id, item["product_id"], item["name"], item["recommended_qty"], item["unit_cost"], line_total)
            )

        created_pos.append({"po_id": po_id, "po_number": po_number, "category": category, "total_cost": round(total_cost, 2), "items": len(items)})
        po_counter += 1

    # Update counter
    conn.execute(
        """INSERT INTO settings (key, value, user_id) VALUES ('po_counter', ?, ?)
           ON CONFLICT(key, user_id) DO UPDATE SET value = excluded.value""",
        (str(po_counter), user_id)
    )

    # Log the action
    conn.execute(
        "INSERT INTO ai_agent_log (user_id, action_type, summary, details, created_at) VALUES (?, ?, ?, ?, ?)",
        (user_id, "po", f"Generated {len(created_pos)} purchase order(s)",
         json.dumps(created_pos), now_iso())
    )

    conn.commit()
    return {"created": len(created_pos), "po_ids": created_pos, "message": f"Created {len(created_pos)} purchase order draft(s)."}


# ── 9. Unified Intelligence Report ───────────────────────────────────────

def run_full_analysis(conn, settings, user_id=None):
    """
    Orchestrates all AI modules and returns a complete intelligence report.
    Reuses intelligence data across modules to maximize performance.
    """
    # Core intelligence computed ONCE
    try:
        intel = get_intelligence(conn, user_id=user_id)
    except Exception:
        intel = {}

    try:
        stockout = get_stockout_predictions(conn, intel=intel)
    except Exception:
        stockout = []

    try:
        demand = get_demand_forecast(conn, intel=intel)
    except Exception:
        demand = []

    try:
        restock = get_restock_recommendations(conn, settings, intel=intel, user_id=user_id)
    except Exception:
        restock = []

    try:
        anomalies = detect_anomalies(conn, user_id=user_id)
    except Exception:
        anomalies = []

    try:
        dead_slow = detect_dead_slow_stock(conn, settings, user_id=user_id)
    except Exception:
        dead_slow = {"dead_stock": [], "slow_moving": []}

    try:
        warehouses = get_warehouse_optimization(conn, user_id=user_id)
    except Exception:
        warehouses = {"warehouses": [], "suggestions": [], "message": ""}

    # Summary counts
    critical_count = sum(1 for s in stockout if s.get("urgency") == "critical")
    warning_count = sum(1 for s in stockout if s.get("urgency") == "warning")
    safe_count = sum(1 for s in stockout if s.get("urgency") == "safe")

    # Recent agent log
    try:
        if user_id is not None:
            log_rows = conn.execute(
                "SELECT * FROM ai_agent_log WHERE user_id = ? ORDER BY id DESC LIMIT 20", (user_id,)
            ).fetchall()
        else:
            log_rows = conn.execute(
                "SELECT * FROM ai_agent_log ORDER BY id DESC LIMIT 20"
            ).fetchall()
    except Exception:
        log_rows = []

    # Active POs
    try:
        if user_id is not None:
            po_rows = conn.execute(
                "SELECT * FROM purchase_orders WHERE user_id = ? AND status IN ('draft', 'sent') ORDER BY id DESC LIMIT 10", (user_id,)
            ).fetchall()
        else:
            po_rows = conn.execute(
                "SELECT * FROM purchase_orders WHERE status IN ('draft', 'sent') ORDER BY id DESC LIMIT 10"
            ).fetchall()
    except Exception:
        po_rows = []

    return {
        "summary": {
            "total_products": len(stockout),
            "critical": critical_count,
            "warning": warning_count,
            "safe": safe_count,
            "anomaly_count": len(anomalies),
            "dead_stock_count": len(dead_slow.get("dead_stock", [])),
            "slow_moving_count": len(dead_slow.get("slow_moving", [])),
            "restock_needed": len(restock),
            "analyzed_at": datetime.now().isoformat(timespec="seconds"),
        },
        "stockout_predictions": stockout[:20],
        "demand_forecast": demand[:15],
        "restock_recommendations": restock[:20],
        "anomalies": anomalies[:20],
        "dead_stock": dead_slow.get("dead_stock", [])[:15],
        "slow_moving": dead_slow.get("slow_moving", [])[:15],
        "warehouses": warehouses,
        "purchase_orders": [dict(po) for po in po_rows],
        "agent_log": [dict(l) for l in log_rows],
    }
