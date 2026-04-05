import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import plotly.graph_objects as go

# 1. 初始化
st.set_page_config(page_title="AI 算力中心-強韌版", layout="wide")

if 'watchlist' not in st.session_state:
    st.session_state.watchlist = {
        '02513': {'name': '智譜 AI', 'base': 760, 'top': 850},
        '00100': {'name': 'MiniMax-W', 'base': 920, 'top': 980}
    }

# 2. 強大抓取引擎
def fetch_safe_data(ticker):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    url = f"http://www.aastocks.com/tc/stocks/analysis/stock-quote-details.aspx?stock={ticker}"
    try:
        r = requests.get(url, headers=headers, timeout=5)
        if r.status_code != 200: return None, "伺服器拒絕"
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # 嘗試多種標籤組合以應對休市變動
        price_tags = ['lastPrice', 'neg-price', 'pos-price']
        price = None
        for tag in price_tags:
            found = soup.find('div', {'class': tag})
            if found:
                price = float(found.text.strip().replace(',', ''))
                break
        
        name_tag = soup.find('span', {'id': 'ctl00_mainContent_ucStockQuote_ucStockQuoteDetails_lblStockName'})
        name = name_tag.text.strip() if name_tag else f"個股 {ticker}"
        return price, name
    except:
        return None, "抓取失敗"

# 3. 介面設計
st.sidebar.title("🛠️ 算力控制台")
new_ticker = st.sidebar.text_input("輸入港股代碼 (如 00700):")

if st.sidebar.button("➕ 加入/刷新觀察"):
    p, n = fetch_safe_data(new_ticker)
    # 即使抓不到，也允許加入
    st.session_state.watchlist[new_ticker] = {
        'name': n if n else f"個股 {new_ticker}",
        'base': (p * 0.95) if p else 0.0,
        'top': (p * 1.05) if p else 100.0,
        'manual_price': p if p else 0.0
    }
    st.sidebar.success(f"已記錄 {new_ticker}")

st.title("📈 勢位態部署工作站")
selected = st.selectbox("選擇股票進行 LEGO 分析", list(st.session_state.watchlist.keys()))
conf = st.session_state.watchlist[selected]

# 4. 核心功能：數據手動/自動修正區
col_a, col_b, col_c = st.columns(3)
with col_a:
    live_p, _ = fetch_safe_data(selected)
    final_p = st.number_input("現價確認 (自動抓取失敗可手動修正)", value=float(live_p if live_p else conf.get('manual_price', 0.0)))
with col_b:
    new_base = st.number_input("方塊底部 (LEGO Base)", value=float(conf['base']))
with col_c:
    new_top = st.number_input("方塊頂部 (LEGO Top)", value=float(conf['top']))

# 更新狀態
st.session_state.watchlist[selected].update({'base': new_base, 'top': new_top, 'manual_price': final_p})

# 5. 視覺化圖表
fig = go.Figure()
# 繪製 LEGO 方塊 (態)
fig.add_shape(type="rect", x0=0, y0=new_base, x1=10, y1=new_top, fillcolor="Yellow", opacity=0.15, line=dict(color="Gold"))
# 繪製現價線 (位)
fig.add_trace(go.Scatter(x=list(range(11)), y=[final_p]*11, name="當前位置", line=dict(color="#00ffcc", width=4, dash='dash')))

fig.update_layout(title=f"{conf['name']} - LEGO 格局趨勢", template="plotly_dark", yaxis=dict(range=[new_base*0.8, new_top*1.2]))
st.plotly_chart(fig, use_container_width=True)

st.warning(f"💡 判斷：{'🚀 向上突破' if final_p > new_top else ('📉 破位下行' if final_p < new_base else '🧱 疊磚整固')}")
