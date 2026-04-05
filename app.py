import streamlit as st
import pandas as pd
import yfinance as yf
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import plotly.graph_objects as go

# 1. 頁面初始化
st.set_page_config(page_title="AI 勢位態終端 - 強韌版", layout="wide")
st.title("🛡️ 港股 AI 監控：突破封鎖部署站")

# 初始化自選清單
if 'watchlist' not in st.session_state:
    st.session_state.watchlist = {
        '02513': {'name': '智譜 AI', 'base': 760.0, 'top': 850.0, 'last_p': 779.0},
        '00100': {'name': 'MiniMax-W', 'base': 920.0, 'top': 980.0, 'last_p': 949.5}
    }

# 2. 深度抓取引擎 (加入更強的偽裝)
def fetch_data_aggressive(ticker):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    }
    try:
        # 嘗試從 AASTOCKS 另一個路徑抓取
        url = f"http://www.aastocks.com/tc/stocks/quote/detail-quote.aspx?symbol={ticker}"
        r = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(r.text, 'html.parser')
        # 尋找報價
        price_tag = soup.find('span', {'class': 'last-price'}) or soup.find('div', {'class': 'lastPrice'})
        if price_tag:
            return float(price_tag.text.strip().replace(',', '')), "AASTOCKS 實時"
        return None, "自動抓取被阻斷"
    except:
        return None, "連線超時"

# 3. 側邊欄：控制中心
st.sidebar.title("🛠️ 算力指揮部")
mode = st.sidebar.radio("數據模式", ["自動抓取", "手動輸入 (部署專用)"])
lookback = st.sidebar.slider("LEGO 觀察天數", 5, 20, 10)

# 4. 主面板邏輯
selected = st.selectbox("選擇監控個股", list(st.session_state.watchlist.keys()))
conf = st.session_state.watchlist[selected]

# 取得數據
if mode == "自動抓取":
    live_p, source = fetch_data_aggressive(selected)
else:
    live_p = None
    source = "手動部署模式"

# 5. 數據處理與判定
st.subheader(f"📊 {conf['name']} ({selected}) - {source}")

# 如果自動抓取失敗或切換到手動
final_p = live_p
if final_p is None:
    st.warning("⚠️ 自動數據流被封鎖。請根據手機 AASTOCKS 價格進行手動對齊：")
    final_p = st.number_input(f"請輸入 {conf['name']} 現價", value=float(conf['last_p']), step=0.1)

# 調整 LEGO 方塊
col1, col2 = st.columns(2)
with col1: new_base = st.number_input("LEGO 方塊底", value=float(conf['base']))
with col2: new_top = st.number_input("LEGO 方塊頂", value=float(conf['top']))

# 更新緩存
st.session_state.watchlist[selected].update({'base': new_base, 'top': new_top, 'last_p': final_p})

# 6. 視覺化圖表 (即使沒數據也能畫出 LEGO)
fig = go.Figure()
# 繪製 LEGO 方塊陰影
fig.add_shape(type="rect", x0=0, y0=new_base, x1=10, y1=new_top, fillcolor="Yellow", opacity=0.15, line=dict(color="Gold", width=2))
# 繪製現價水平線
fig.add_trace(go.Scatter(x=[0, 10], y=[final_p, final_p], mode='lines+text', name='當前位置', 
                         line=dict(color='#00ffcc', width=4), text=["", f"${final_p}"], textposition="top right"))

fig.update_layout(title=f"{conf['name']} LEGO 態勢分析", template="plotly_dark", yaxis=dict(range=[new_base*0.9, new_top*1.1], title="價格 (HKD)"))
st.plotly_chart(fig, use_container_width=True)

# 7. 判定
status = "🚀 突破中" if final_p > new_top else ("📉 破位" if final_p < new_base else "🧱 疊磚中")
st.success(f"戰略判定：{status} (數據參考日期: {datetime.now().strftime('%Y-%m-%d')})")
