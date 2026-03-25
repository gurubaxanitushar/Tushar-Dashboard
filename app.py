import streamlit as st
import requests
import pandas as pd
import yfinance as yf
import time

st.set_page_config(page_title="Global Market Dashboard", layout="wide")

# ================= STYLE =================
st.markdown("""
<style>
.big-title {
    font-size:45px;
    font-weight:bold;
    background: linear-gradient(90deg,#7c3aed,#3b82f6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.green {color:#22c55e; font-weight:bold;}
.red {color:#ef4444; font-weight:bold;}
.card {
    padding:15px;
    border-radius:15px;
    background: linear-gradient(135deg,#1e1b4b,#1e3a8a);
    color:white;
    text-align:center;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='big-title'>🌐 Global Market Dashboard</div>", unsafe_allow_html=True)

# ================= LOADER =================
if "loaded" not in st.session_state:
    st.session_state.loaded = False

if not st.session_state.loaded:
    st.markdown("## 🚀 Welcome Legend")
    p = st.progress(0)
    for i in range(100):
        time.sleep(0.01)
        p.progress(i+1)
    st.session_state.loaded = True
    st.rerun()

# ================= SAFE =================
def safe(url):
    try:
        return requests.get(url, timeout=5).json()
    except:
        return {}

# ================= RSI =================
def rsi(data):
    delta = data.diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = -delta.clip(upper=0).rolling(14).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# ================= DATA =================
@st.cache_data(ttl=60)
def get_crypto():
    return safe("https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&per_page=50&page=1")

crypto = get_crypto()

# ================= NAV (WITH ICONS) =================
page = st.radio(
    "",
    [
        "🏠 Home",
        "💰 Crypto",
        "🛢 Commodity",
        "🌍 Global Index",
        "📡 Signals",
        "📰 Macro News"
    ],
    horizontal=True
)

# ================= HOME =================
if page == "🏠 Home":

    st.markdown("## 🚀 Welcome Legend")

    def card(title, symbol):
        df = yf.download(symbol, period="2d", progress=False)
        if len(df) >= 2:
            close = float(df["Close"].iloc[-1])
            prev = float(df["Close"].iloc[-2])
            pct = ((close - prev) / prev) * 100 if prev != 0 else 0
            color = "green" if pct > 0 else "red"
            return f"<div class='card'><h4>{title}</h4><h2>{round(close,2)}</h2><p class='{color}'>{round(pct,2)}%</p></div>"
        return ""

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(card("Bitcoin","BTC-USD"), unsafe_allow_html=True)
    c2.markdown(card("Ethereum","ETH-USD"), unsafe_allow_html=True)
    c3.markdown(card("Gold","GC=F"), unsafe_allow_html=True)
    c4.markdown(card("Silver","SI=F"), unsafe_allow_html=True)

    if crypto:
        clean = [x for x in crypto if isinstance(x.get("price_change_percentage_24h"), (int,float))]
        gainers = sorted(clean, key=lambda x: x["price_change_percentage_24h"], reverse=True)[:5]
        losers = sorted(clean, key=lambda x: x["price_change_percentage_24h"])[:5]

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Top Gainers")
            for x in gainers:
                st.markdown(f"{x['name']} <span class='green'>{x['price_change_percentage_24h']:.2f}%</span>", unsafe_allow_html=True)

        with col2:
            st.subheader("Top Losers")
            for x in losers:
                st.markdown(f"{x['name']} <span class='red'>{x['price_change_percentage_24h']:.2f}%</span>", unsafe_allow_html=True)

    fg = safe("https://api.alternative.me/fng/")
    try:
        st.markdown(f"### 😨 Fear & Greed: {fg['data'][0]['value']} ({fg['data'][0]['value_classification']})")
    except:
        pass

# ================= CRYPTO =================
elif page == "💰 Crypto":

    rows = []
    for i, x in enumerate(crypto, 1):
        ch = x.get("price_change_percentage_24h", 0) or 0
        color = "green" if ch > 0 else "red"

        rows.append({
            "No": i,
            "Name": x["name"],
            "Price": x["current_price"],
            "High": x["high_24h"],
            "Low": x["low_24h"],
            "Volume": x["total_volume"],
            "24h %": f"<span class='{color}'>{round(ch,2)}%</span>"
        })

    df = pd.DataFrame(rows)
    st.write(df.to_html(index=False, escape=False), unsafe_allow_html=True)

# ================= COMMODITY =================
elif page == "🛢 Commodity":

    assets = {
        "Gold":"GC=F","Silver":"SI=F","Crude Oil (WTI)":"CL=F",
        "Brent Oil":"BZ=F","Natural Gas":"NG=F",
        "Platinum":"PL=F","Palladium":"PA=F"
    }

    rows = []

    for i,(name,symbol) in enumerate(assets.items(),1):
        df = yf.download(symbol, period="2d", progress=False)

        if len(df) >= 2:
            close = float(df["Close"].iloc[-1])
            prev = float(df["Close"].iloc[-2])
            pct = ((close - prev) / prev) * 100 if prev != 0 else 0
            color = "green" if pct > 0 else "red"

            rows.append({
                "No": i,
                "Name": name,
                "Price": round(close,2),
                "High": round(float(df["High"].iloc[-1]),2),
                "Low": round(float(df["Low"].iloc[-1]),2),
                "Volume": "-",
                "24h %": f"<span class='{color}'>{round(pct,2)}%</span>"
            })

    df = pd.DataFrame(rows)
    st.write(df.to_html(index=False, escape=False), unsafe_allow_html=True)

# ================= GLOBAL INDEX =================
elif page == "🌍 Global Index":

    indices = {
        "S&P 500":"^GSPC","NASDAQ":"^IXIC","Dow Jones":"^DJI",
        "NIFTY 50":"^NSEI","SENSEX":"^BSESN","DAX":"^GDAXI",
        "FTSE 100":"^FTSE","CAC 40":"^FCHI","Nikkei":"^N225",
        "Hang Seng":"^HSI","Shanghai":"000001.SS","KOSPI":"^KS11",
        "ASX 200":"^AXJO","TSX":"^GSPTSE","IBEX":"^IBEX",
        "SMI":"^SSMI","AEX":"^AEX","OMX":"^OMX","TAIEX":"^TWII","SET":"^SET.BK"
    }

    rows = []

    for i,(name,symbol) in enumerate(indices.items(),1):
        df = yf.download(symbol, period="2d", progress=False)

        if len(df) >= 2:
            close = float(df["Close"].iloc[-1])
            prev = float(df["Close"].iloc[-2])
            pct = ((close - prev) / prev) * 100 if prev != 0 else 0
            color = "green" if pct > 0 else "red"

            rows.append({
                "No": i,
                "Name": name,
                "Price": round(close,2),
                "High": round(float(df["High"].iloc[-1]),2),
                "Low": round(float(df["Low"].iloc[-1]),2),
                "Volume": "-",
                "24h %": f"<span class='{color}'>{round(pct,2)}%</span>"
            })

    df = pd.DataFrame(rows)
    st.write(df.to_html(index=False, escape=False), unsafe_allow_html=True)

# ================= SIGNAL =================
elif page == "📡 Signals":

    for x in crypto[:15]:
        try:
            df = yf.download(x["symbol"].upper()+"-USD", period="1mo", progress=False)
            if len(df) < 20:
                continue

            r = rsi(df["Close"]).iloc[-1]
            vol = df["Volume"].iloc[-1]

            if r < 30:
                s = "STRONG BUY"; c = "#22c55e"
            elif r < 45:
                s = "BUY"; c = "#4ade80"
            elif r > 70:
                s = "STRONG SELL"; c = "#ef4444"
            elif r > 55:
                s = "SELL"; c = "#f87171"
            else:
                s = "HOLD"; c = "#94a3b8"

            st.markdown(f"<div class='card'><h4>{x['name']}</h4><p style='color:{c}'>{s}</p><p>RSI:{round(r,2)} | Vol:{int(vol)}</p></div>", unsafe_allow_html=True)

        except:
            pass

# ================= MACRO NEWS =================
elif page == "📰 Macro News":

    news = safe("https://cryptopanic.com/api/v1/posts/?public=true")

    for n in news.get("results", [])[:10]:
        st.markdown(f"### {n['title']}")
        st.markdown(f"[Read more]({n['url']})")