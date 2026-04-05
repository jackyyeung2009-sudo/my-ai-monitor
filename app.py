import streamlit as st
import pandas as pd
import yfinance as yf
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import plotly.graph_objects as go

# 1. 頁面初始化
st.set_page_config(page_title="AI 勢位態終端", layout="wide")
st.title("🛡️ 港股 AI 監控：強韌化數據終端")

if 'watchlist' not in st.session_state:
    st.session_state.watchlist = {
        '02513': {'name': '智譜 AI', 'base': 760.0, 'top': 850.0},
        '00100': {'name': 'MiniMax-W', 'base': 920.0, 'top': 980.0}
    }

# 2. 備援抓取引擎 (優先 AASTOCKS 現價)
def fetch_last_resort(ticker):
    try:
        url = f"http://www.aastocks.com/tc/stocks/analysis/stock-quote-details.aspx?stock={ticker}"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        r = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(r.text, 'html.parser')
        price_tag = soup.find('div', {'class': 'lastPrice'})
        if price_tag:
            return float(price_tag.text.strip().replace(',', '')), "AASTOCKS 實時"
        return None, "所有來源皆被封鎖"
    except:
        return None, "網絡異常"

def get_historical_safe(ticker):
    try:
        yf_code = f"{ticker.lstrip('0')}.HK"
        # 加入更強的 Session 管理
        df = yf.download(yf_code, period="1mo", interval="1d", progress=False, timeout=10)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df
    except:
        return None

# 3. 側邊欄控制
st.sidebar.title("🛠️ 算力指揮部")
lookback = st.sidebar.slider("LEGO 觀察天數", 5, 25, 15)

# 4. 主面板
selected = st.selectbox("選擇監控個股", list(st.session_state.watchlist.keys()))
conf = st.session_state.watchlist[selected]

# 嘗試獲取數據
df = get_historical_safe(selected)
live_p, source_name = fetch_last_resort(selected)

# 5. 數據呈現邏輯
st.subheader(f"📊 {conf['name']} ({selected}) - {source_name}")

if df is not None:
    # 正常顯示陰陽燭
    current_p = live_p if live_p else float(df['Close'].iloc[-1])
    
    col1, col2 = st.columns(2)
    with col1: new_base = st.number_input("LEGO 方塊底", value=float(conf['base']))
    with col2: new_top = st.number_input("LEGO 方塊頂", value=float(conf['top']))
    st.session_state.watchlist[selected].update({'base': new_base, 'top': new_top})

    fig = go.Figure(data=[go.Candlestick(
        x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
        increasing_line_color='#ff4d4d', decreasing_line_color='#2ecc71', name="日綫"
    )])
    
    fig.add_shape(type="rect",
        x0=df.index[-min(len(df), lookback)], y0=new_base, x1=df.index[-1], y1=new_top,
        fillcolor="Yellow", opacity=0.15, line=dict(color="Gold", width=2)
    )
    
    fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=500)
    st.plotly_chart(fig, use_container_width=True)
    
    status = "🚀 突破" if current_p > new_top else ("📉 破位" if current_p < new_base else "🧱 疊磚中")
    st.info(f"🔮 算力判定：{status} (參考價: ${current_p})")
else:
    # 進入【手動部署模式】
    st.error("⚠️ 雲端 IP 被 Yahoo 封鎖，已切換至「手動部署模式」")
    manual_p = st.number_input("請輸入當前看見的股價 (參考 AASTOCKS)", value=float(live_p if live_p else 0.0))
    m_base = st.number_input("手動設定 LEGO 底", value=float(conf['base']))
    m_top = st.number_input("手動設定 LEGO 頂", value=float(conf['top']))
    
    # 畫出簡單的 LEGO 判定圖
    fig = go.Figure()
    fig.add_shape(type="rect", x0=0, y0=m_base, x1=10, y1=m_top, fillcolor="Yellow", opacity=0.2)
    fig.add_trace(go.Scatter(x=[0,10], y=[manual_p, manual_p], name="手動價格", line=dict(color="Cyan", width=3)))
    fig.update_layout(template="plotly_dark", title="手動部署形態圖")
    st.plotly_chart(fig, use_container_width=True)
