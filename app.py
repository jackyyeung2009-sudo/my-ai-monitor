import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import plotly.graph_objects as go

# 1. 基礎設定與時空握手
st.set_page_config(page_title="AI 勢位態監控中心", layout="wide")

# 初始化自選清單 (若不存在則建立)
if 'watchlist' not in st.session_state:
    st.session_state.watchlist = {
        '02513': {'name': '智譜 AI', 'base': 760.0, 'top': 850.0},
        '00100': {'name': 'MiniMax-W', 'base': 920.0, 'top': 980.0}
    }

# 2. 數據抓取引擎 (強韌版)
def fetch_safe_data(ticker):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    url = f"http://www.aastocks.com/tc/stocks/analysis/stock-quote-details.aspx?stock={ticker}"
    try:
        r = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(r.text, 'html.parser')
        # 掃描多個可能標籤
        price_tag = soup.find('div', {'class': 'lastPrice'}) or soup.find('div', {'class': 'neg-price'}) or soup.find('div', {'class': 'pos-price'})
        price = float(price_tag.text.strip().replace(',', '')) if price_tag else None
        
        name_tag = soup.find('span', {'id': 'ctl00_mainContent_ucStockQuote_ucStockQuoteDetails_lblStockName'})
        name = name_tag.text.strip() if name_tag else f"個股 {ticker}"
        return price, name
    except:
        return None, f"代碼 {ticker}"

# 3. 側邊欄控制區
st.sidebar.title("🛠️ 算力指揮部")

# 設定 LEGO 計算週期 (解決 NameError 的核心)
lookback_days = st.sidebar.slider("LEGO 計算週期 (天)", min_value=5, max_value=20, value=10)

# 新增自選股
new_ticker = st.sidebar.text_input("新增港股 (如 00700):")
if st.sidebar.button("➕ 加入監控"):
    p, n = fetch_safe_data(new_ticker)
    # 以現價為基準，根據計算天數自動生成初始方塊 (模擬歷史波动)
    init_p = p if p else 100.0
    st.session_state.watchlist[new_ticker] = {
        'name': n,
        'base': init_p * (1 - 0.005 * lookback_days), # 天數越多，方塊越寬
        'top': init_p * (1 + 0.005 * lookback_days)
    }
    st.sidebar.success(f"{n} 已就位")

# 4. 主看板邏輯
st.title("📈 港股 AI 板塊 - 勢位態動態分析")
selected = st.selectbox("切換觀察對象", list(st.session_state.watchlist.keys()))
conf = st.session_state.watchlist[selected]

# 抓取實時數據
live_p, _ = fetch_safe_data(selected)
final_p = st.number_input("現價確認 (可手動修正)", value=float(live_p if live_p else 0.0))

# 調整 LEGO 方塊 (位)
col1, col2 = st.columns(2)
with col1:
    new_base = st.number_input(f"【{lookback_days}日】方塊底", value=float(conf['base']))
with col2:
    new_top = st.number_input(f"【{lookback_days}日】方塊頂", value=float(conf['top']))

# 更新緩存
st.session_state.watchlist[selected].update({'base': new_base, 'top': new_top})

# 5. 視覺化分析
fig = go.Figure()
# 繪製方塊
fig.add_shape(type="rect", x0=0, y0=new_base, x1=lookback_days, y1=new_top, fillcolor="Yellow", opacity=0.15, line=dict(color="Gold"))
# 繪製現價
fig.add_trace(go.Scatter(x=list(range(lookback_days + 1)), y=[final_p]*(lookback_days + 1), name="現價線", line=dict(color="#00ffcc", width=4)))

fig.update_layout(
    title=f"{conf['name']} ({selected}) - 基於 {lookback_days} 日之 LEGO 形態",
    template="plotly_dark",
    yaxis=dict(range=[new_base*0.8, new_top*1.2]),
    xaxis=dict(title="計算週期內時間軸")
)
st.plotly_chart(fig, use_container_width=True)

# 6. 狀態判定
status = "🚀 突破中" if final_p > new_top else ("📉 破位" if final_p < new_base else "🧱 疊磚中")
st.subheader(f"判定結果：{status}")
st.info(f"☀️ 部署建議：目前週期為 {lookback_days} 日。智譜 (2513) 的能量區間正隨天數擴大，請注意 {new_base} 的支撐強度。")
