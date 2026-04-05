import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import plotly.graph_objects as go

# 1. 初始化環境
st.set_page_config(page_title="AI 算力中心-動態版", layout="wide")

# 初始化自選股清單 (Session State)
if 'watchlist' not in st.session_state:
    st.session_state.watchlist = {
        '02513': {'name': '智譜 AI', 'base': 760, 'top': 850},
        '00100': {'name': 'MiniMax-W', 'base': 920, 'top': 980}
    }

# 2. 抓取引擎 (對接 aastock)
def fetch_realtime_price(ticker):
    try:
        url = f"http://www.aastocks.com/tc/stocks/analysis/stock-quote-details.aspx?stock={ticker}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(r.text, 'html.parser')
        price = float(soup.find('div', {'class': 'lastPrice'}).text.strip().replace(',', ''))
        name = soup.find('span', {'id': 'ctl00_mainContent_ucStockQuote_ucStockQuoteDetails_lblStockName'}).text.strip()
        return price, name
    except:
        return None, "未知股票"

# 3. 側邊欄：動態管理
st.sidebar.title("🔍 算力控制台")
new_ticker = st.sidebar.text_input("輸入港股代碼 (例如 00700):", "")

if st.sidebar.button("➕ 加入觀察清單"):
    if new_ticker and new_ticker not in st.session_state.watchlist:
        p, n = fetch_realtime_price(new_ticker)
        if p:
            # 自動設定初始 LEGO 方塊 (以現價為中心 ±5%)
            st.session_state.watchlist[new_ticker] = {
                'name': n, 'base': p * 0.95, 'top': p * 1.05
            }
            st.sidebar.success(f"已加入 {n}")
        else:
            st.sidebar.error("代碼錯誤或抓取失敗")

# 4. 主畫面佈局
st.title("📈 勢位態全板塊監控")
selected_ticker = st.selectbox("切換觀察對象", list(st.session_state.watchlist.keys()))

# 允許手動調整 LEGO 位
conf = st.session_state.watchlist[selected_ticker]
col_cfg1, col_cfg2 = st.columns(2)
with col_cfg1:
    new_base = st.number_input(f"調整 {conf['name']} 方塊底", value=float(conf['base']))
with col_cfg2:
    new_top = st.number_input(f"調整 {conf['name']} 方塊頂", value=float(conf['top']))
st.session_state.watchlist[selected_ticker]['base'] = new_base
st.session_state.watchlist[selected_ticker]['top'] = new_top

# 5. 數據呈現與圖表
price, _ = fetch_realtime_price(selected_ticker)
if price:
    col1, col2 = st.columns([1, 2])
    with col1:
        st.metric("實時現價", f"${price}", delta=f"LEGO 區間: {new_base}-{new_top}")
        status = "突破" if price > new_top else ("破位" if price < new_base else "疊磚")
        st.subheader(f"判定：{status}")
        
    with col2:
        # 繪製圖表
        fig = go.Figure()
        fig.add_shape(type="rect", x0=0, y0=new_base, x1=10, y1=new_top, fillcolor="Yellow", opacity=0.2)
        fig.add_trace(go.Scatter(x=list(range(11)), y=[price]*11, name="現價線", line=dict(color="Cyan", width=4)))
        fig.update_layout(title=f"{conf['name']} LEGO 態勢圖", template="plotly_dark", yaxis=dict(range=[new_base*0.9, new_top*1.1]))
        st.plotly_chart(fig, use_container_width=True)

st.info("☀️ **陽光操作：** 隨意加入股票後，系統會自動幫你畫出初始方塊。你可以根據 Sky Sir 的建議，手動微調方塊的底和頂。")
