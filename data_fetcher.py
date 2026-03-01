# ================================================
# CODING MARKET — GitHub Actions Auto Fetcher
# by MR. RISHU RAJ
# ================================================
# Yeh script roz GitHub Actions pe chalti hai:
#   1. NSE CSV fetch karta hai
#   2. CodingMarket_New.html ke IDs update karta hai
#   3. GitHub auto commit karta hai → Website live!
# ================================================

import requests
import pandas as pd
import re
from io import BytesIO
from datetime import datetime, timedelta

HTML_FILE = "CodingMarket_New.html"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept":     "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Referer":    "https://www.nseindia.com",
}

# ── Trading Date ──────────────────────────────
def last_trading_day():
    d = datetime.utcnow() + timedelta(hours=5, minutes=30)  # IST
    # Agar 10 PM se pehle — pichla din
    if d.hour < 22:
        d -= timedelta(days=1)
    while d.weekday() >= 5:   # Skip Sat/Sun
        d -= timedelta(days=1)
    return d

# ── NSE Fetch with Session ────────────────────
def fetch_csv(date):
    dd  = date.strftime("%d%m%Y")
    url = f"https://www.nseindia.com/content/nsccl/fao_participant_oi_{dd}.csv"
    print(f"  📡 URL: {url}")

    session = requests.Session()
    try:
        session.get("https://www.nseindia.com", headers=HEADERS, timeout=15)
        r = session.get(url, headers=HEADERS, timeout=20)
        r.raise_for_status()
        df = pd.read_csv(BytesIO(r.content))
        print(f"  ✅ Rows: {len(df)}  Columns: {list(df.columns)}")
        return df
    except Exception as e:
        print(f"  ❌ Failed: {e}")
        return None

# ── Parse ─────────────────────────────────────
def safe_n(val):
    try:    return float(str(val).replace(",","").strip() or 0)
    except: return 0.0

def parse(df, client_type):
    try:
        df.columns = [c.strip() for c in df.columns]
        row = df[df.iloc[:,0].str.strip().str.upper() == client_type.upper()]
        if row.empty:
            print(f"  ⚠️  '{client_type}' not found")
            return 0, 0
        call = safe_n(row["Index Call Long"].values[0]) - safe_n(row["Index Call Short"].values[0])
        put  = safe_n(row["Index Put Long"].values[0])  - safe_n(row["Index Put Short"].values[0])
        return int(call), int(put)
    except Exception as e:
        print(f"  ⚠️  Parse error ({client_type}): {e}")
        return 0, 0

def sentiment(call, put):
    n = call + put
    return "bullish" if n > 10000 else "bearish" if n < -10000 else "neutral"

# ── Format ────────────────────────────────────
def fmt(n):  return ("+" if n >= 0 else "") + f"{int(n):,}"
def mood(v): return "Heavily Bullish" if v=="bullish" else "Heavily Bearish" if v=="bearish" else "Neutral"
def badge(v):return "BULLISH ↑" if v=="bullish" else "BEARISH ↓" if v=="bearish" else "NEUTRAL ↔"

# ── HTML ID Update ─────────────────────────────
def upd(html, eid, value):
    pat = r'(id="{}"[^>]*>)[^<]*(</[^>]+>)'.format(re.escape(eid))
    out = re.sub(pat, r'\g<1>' + str(value) + r'\2', html)
    print(f"  {'✅' if out!=html else '⚠️ MISS'} #{eid} → {value}")
    return out

# ── Main Update ───────────────────────────────
def update_html(participants, date_str):
    with open(HTML_FILE, "r", encoding="utf-8") as f:
        html = f.read()

    print("\n📝 Updating HTML...\n")

    # CLIENT
    c = participants["client"]
    html = upd(html, "call-net",     fmt(c["call"]))
    html = upd(html, "put-net",      fmt(c["put"]))
    html = upd(html, "client-mood",  mood(c["v"]))
    html = upd(html, "client-badge", badge(c["v"]))

    # FII
    f = participants["fii"]
    html = upd(html, "fii-call",  fmt(f["call"]))
    html = upd(html, "fii-put",   fmt(f["put"]))
    html = upd(html, "fii-mood",  mood(f["v"]))
    html = upd(html, "fii-badge", badge(f["v"]))

    # PRO
    p = participants["pro"]
    html = upd(html, "pro-call",  fmt(p["call"]))
    html = upd(html, "pro-put",   fmt(p["put"]))
    html = upd(html, "pro-mood",  mood(p["v"]))
    html = upd(html, "pro-badge", badge(p["v"]))

    # DII
    d = participants["dii"]
    html = upd(html, "dii-call",  fmt(d["call"]))
    html = upd(html, "dii-put",   fmt(d["put"]))
    html = upd(html, "dii-mood",  mood(d["v"]))
    html = upd(html, "dii-badge", badge(d["v"]))

    # DATE
    html = upd(html, "h-date", date_str)

    # PREDICTION
    vals  = [c["v"], f["v"], p["v"], d["v"]]
    bears = vals.count("bearish")
    bulls = vals.count("bullish")
    pred  = "bearish" if (bears>=2 and f["v"]=="bearish") else "bullish" if bulls>=3 else "neutral"
    ptxt  = "Market Goes Up" if pred=="bullish" else "Market Goes Down" if pred=="bearish" else "Market Sideways"
    emoji = "⬆️" if pred=="bullish" else "⬇️" if pred=="bearish" else "↔️"
    html  = upd(html, "h-pred",  ptxt)
    html  = upd(html, "h-emoji", emoji)

    with open(HTML_FILE, "w", encoding="utf-8") as f_out:
        f_out.write(html)

    return pred

# ── Entry Point ───────────────────────────────
if __name__ == "__main__":
    print("=" * 55)
    print("  CODING MARKET — GitHub Actions Auto Fetcher")
    print(f"  Run time: {datetime.utcnow()+timedelta(hours=5,minutes=30):%d-%b-%Y %H:%M IST}")
    print("=" * 55)

    # Pichle trading day ka date nikalo
    date = last_trading_day()
    print(f"\n📅 Trading date: {date:%d-%b-%Y (%A)}")

    # CSV fetch karo
    print("\n📡 Fetching NSE data...")
    df = fetch_csv(date)

    # Agar fail — ek din aur peeche jao
    if df is None:
        date -= timedelta(days=1)
        while date.weekday() >= 5:
            date -= timedelta(days=1)
        print(f"\n🔄 Retry: {date:%d-%b-%Y}")
        df = fetch_csv(date)

    if df is None:
        print("\n❌ NSE data fetch nahi hua — Action fail!")
        exit(1)

    # Sab participants parse karo
    parts = {}
    for key, nse_name in [("client","Client"),("fii","FII"),("pro","Pro"),("dii","DII")]:
        call, put = parse(df, nse_name)
        v = sentiment(call, put)
        parts[key] = {"call": call, "put": put, "v": v}
        print(f"  {key.upper():8}: Call {fmt(call):>12}  Put {fmt(put):>12}  [{v.upper()}]")

    # HTML update karo
    pred = update_html(parts, date.strftime("%d-%b-%Y"))

    print("\n" + "=" * 55)
    print("  ✅ HTML UPDATED!")
    print(f"  Prediction: {pred.upper()}")
    print("  GitHub will auto-commit and push...")
    print("=" * 55)
