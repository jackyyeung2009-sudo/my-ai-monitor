import streamlit as st
import pandas as pd
import yfinance as yf
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import plotly.graph_objects as go

# 1. 頁面配置
st.set_page_config(page_title="AI 勢位態終端 - 終極版", layout="wide")
st.title("🛡️ 港股 AI 雙雄：突破封鎖全功能站")

# 2. 緩存清單管理
if 'watchlist' not in st.session_state:
    st.session_state.watchlist = {
        '02513': {'name': '智譜 AI', 'base': 760.0, 'top': 850.0},
        '00100': {'name': 'MiniMax-W', 'base': 920.0, 'top': 980.0}
    }

# 3. 抓取引擎 (PLAN B 隱身模式)
def fetch_stealth_price(ticker):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    try:
        url = f"http://www.aastocks.com/tc/stocks/quote/detail-quote.aspx?symbol={ticker}"
        r = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(r.text, 'html.parser')
        price_tag = soup.find('span', {'class': 'last-price'}) or soup.find('div', {'class': 'lastPrice'})
        if price_tag:
            return float(price_tag.text.strip().replace(',', '')), "AASTOCKS 實時"
        return None, "自動抓取被阻斷"
    except:
        return None, "連線超時"

# 4. 側邊欄控制：【新增股票功能回歸】
st.sidebar.title("🛠️ 算力指揮部")
lookback = st.sidebar.slider("LEGO 觀察天數", 5, 20, 10)

new_ticker = st.sidebar.text_input("輸入港股代碼新增 (如 00700):")
if st.sidebar.button("➕ 加入監控清單"):
    p, n = fetch_stealth_price(new_ticker)
    init_p = p if p else 100.0
    st.session_state.watchlist[new_ticker] = {
        'name': f"個股 {new_ticker}", 
        'base': init_p * 0.95, 'top': init_p * 1.05
    }
    st.sidebar.success(f"{new_ticker} 已就位")

# 5. 主面板邏輯
selected = st.selectbox("選擇監控個股", list(st.session_state.watchlist.keys()))
conf = st.session_state.watchlist[selected]

# 抓取數據
live_p, source = fetch_stealth_price(selected)
final_p = st.number_input(f"【{source}】現價確認 (失敗可手動修正)", value=float(live_p if live_p else 0.0))

# 調整 LEGO 方塊
c1, c2 = st.columns(2)
with c1: new_base = st.number_input("LEGO 方塊底", value=float(conf['base']))
with c2: new_top = st.number_input("LEGO 方塊頂", value=float(conf['top']))
st.session_state.watchlist[selected].update({'base': new_base, 'top': new_top})

# 6. 視覺化圖表：【確保圖表不消失】
fig = go.Figure()

# 嘗試抓取日綫，失敗則顯示基礎方塊
try:
    yf_code = f"{selected.lstrip('0')}.HK"
    hist_df = yf.download(yf_code, period="1mo", interval="1d", progress=False)
    if not hist_df.empty:
        if isinstance(hist_df.columns, pd.MultiIndex):
            hist_df.columns = hist_df.columns.get_level_values(0)
        
        # 加入陰陽燭
        fig.add_trace(go.Candlestick(
            x=hist_df.index, open=hist_df['Open'], high=hist_df['High'], low=hist_df['Low'], close=hist_df['Close'],
            name="日綫", increasing_line_color='#ff4d4d', decreasing_line_color='#2ecc71'
        ))
        box_start = hist_df.index[-min(len(hist_df), lookback)]
        box_end = hist_df.index[-1]
    else:
        raise Exception("YF 數據空")
except:
    # 備援圖表：只畫方塊與現價線
    st.warning("🕯️ 陰陽燭抓取失敗，目前僅顯示 LEGO 格局判定圖。")
    box_start, box_end = 0, 10
    fig.add_trace(go.Scatter(x=[0, 10], y=[final_p, final_p], name="現價位置", line=dict(color="#00ffcc", width=4)))

# 統一注入 LEGO 方塊 (態)
fig.add_shape(type="rect", x0=box_start, y0=new_base, x1=box_end, y1=new_top,
              fillcolor="Yellow", opacity=0.15, line=dict(color="Gold", width=2))

fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=500, title=f"{conf['name']} - 勢位態分析")
st.plotly_chart(fig, use_container_width=True)

# 7. 判定
status = "🚀 突破" if final_p > new_top else ("📉 破位" if final_p < new_base else "🧱 疊磚中")
st.subheader(f"戰略判定：{status}")
