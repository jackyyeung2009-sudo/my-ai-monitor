import streamlit as st
import pandas as pd
import yfinance as yf
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import plotly.graph_objects as go

# 1. 頁面初始化
st.set_page_config(page_title="AI 勢位態終端-PLAN B", layout="wide")
st.title("🚀 港股 AI 雙雄：雲端突圍監控屏")

# 2. 緩存自選股與 LEGO 數據
if 'watchlist' not in st.session_state:
    st.session_state.watchlist = {
        '02513': {'name': '智譜 AI', 'base': 760.0, 'top': 850.0, 'last_p': 779.0},
        '00100': {'name': 'MiniMax-W', 'base': 920.0, 'top': 980.0, 'last_p': 949.5}
    }

# 3. 隱身抓取引擎 (PLAN B 核心)
def stealth_fetch_price(ticker):
    # 隨機偽裝 Header
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'zh-HK,zh;q=0.9,en;q=0.8',
        'Referer': 'https://www.google.com/'
    }
    # 嘗試 AASTOCKS
    try:
        url = f"http://www.aastocks.com/tc/stocks/quote/detail-quote.aspx?symbol={ticker}"
        r = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(r.text, 'html.parser')
        price_tag = soup.find('span', {'class': 'last-price'}) or soup.find('div', {'class': 'lastPrice'})
        if price_tag:
            return float(price_tag.text.strip().replace(',', '')), "AASTOCKS 實時"
    except:
        pass
    
    # 嘗試 Yahoo Finance 備援
    try:
        yf_code = f"{ticker.lstrip('0')}.HK"
        data = yf.download(yf_code, period="1d", progress=False)
        if not data.empty:
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(0)
            return float(data['Close'].iloc[-1]), "Yahoo 備援"
    except:
        pass
        
    return None, "數據源暫時封鎖"

# 4. 側邊欄控制
st.sidebar.title("🛠️ 算力指揮部")
lookback = st.sidebar.slider("LEGO 觀察天數", 5, 20, 10)
selected = st.selectbox("選擇監控個股", list(st.session_state.watchlist.keys()))
conf = st.session_state.watchlist[selected]

# 5. 執行抓取與顯示
live_p, source = stealth_fetch_price(selected)
final_p = live_p if live_p else st.number_input(f"【{source}】手動輸入現價:", value=float(conf['last_p']))

# 更新 LEGO 區間
col1, col2 = st.columns(2)
with col1: new_base = st.number_input("LEGO 方塊底", value=float(conf['base']))
with col2: new_top = st.number_input("LEGO 方塊頂", value=float(conf['top']))
st.session_state.watchlist[selected].update({'base': new_base, 'top': new_top, 'last_p': final_p})

# 6. 陰陽燭與 LEGO 圖表
st.subheader(f"📊 {conf['name']} ({selected}) - 勢位態分析")

# 嘗試抓取歷史日綫作背景
try:
    hist_df = yf.download(f"{selected.lstrip('0')}.HK", period="1mo", interval="1d", progress=False)
    if not hist_df.empty:
        if isinstance(hist_df.columns, pd.MultiIndex):
            hist_df.columns = hist_df.columns.get_level_values(0)
        
        fig = go.Figure(data=[go.Candlestick(
            x=hist_df.index, open=hist_df['Open'], high=hist_df['High'], low=hist_df['Low'], close=hist_df['Close'],
            increasing_line_color='#ff4d4d', decreasing_line_color='#2ecc71', name="日綫"
        )])
        # 加入 LEGO 方塊
        fig.add_shape(type="rect", x0=hist_df.index[-lookback], y0=new_base, x1=hist_df.index[-1], y1=new_top,
                      fillcolor="Yellow", opacity=0.15, line=dict(color="Gold", width=2))
        
        fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=500)
        st.plotly_chart(fig, use_container_width=True)
except:
    st.warning("日綫陰陽燭抓取失敗，顯示基礎 LEGO 判定圖。")
    # 基礎圖表略 (同上個版本)

# 7. 判定
status = "🚀 突破中" if final_p > new_top else ("📉 破位" if final_p < new_base else "🧱 疊磚中")
st.success(f"判定結果：{status} (現價: ${final_p})")
