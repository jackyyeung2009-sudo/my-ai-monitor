import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import plotly.graph_objects as go

# 1. 頁面設定
st.set_page_config(page_title="AI 勢位態監控中心", layout="wide")
st.title("🕯️ 智譜 & MiniMax：日綫陰陽燭 + LEGO 部署")

# 初始化自選清單
if 'watchlist' not in st.session_state:
    st.session_state.watchlist = {
        '02513': {'name': '智譜 AI', 'base': 760.0, 'top': 850.0},
        '00100': {'name': 'MiniMax-W', 'base': 920.0, 'top': 980.0}
    }

# 2. 獲取真實日綫數據 (yfinance 算力支援)
def get_historical_data(ticker):
    try:
        # 將港股代碼轉換為 yfinance 格式 (例如 02513 -> 2513.HK)
        yf_ticker = f"{ticker[1:]}.HK" if ticker.startswith('0') else f"{ticker}.HK"
        data = yf.download(yf_ticker, period="1mo", interval="1d")
        return data
    except:
        return None

# 3. 側邊欄控制
st.sidebar.title("🛠️ 算力指揮部")
lookback = st.sidebar.slider("顯示天數", 10, 30, 20)
new_ticker = st.sidebar.text_input("新增港股代碼:")
if st.sidebar.button("➕ 加入清單"):
    df = get_historical_data(new_ticker)
    if not df.empty:
        last_p = float(df['Close'].iloc[-1])
        st.session_state.watchlist[new_ticker] = {
            'name': f"個股 {new_ticker}", 'base': last_p*0.95, 'top': last_p*1.05
        }
    else: st.sidebar.error("代碼有誤")

# 4. 主看板
selected = st.selectbox("選擇監控個股", list(st.session_state.watchlist.keys()))
conf = st.session_state.watchlist[selected]

# 獲取數據
df = get_historical_data(selected)
if df is not None and not df.empty:
    # 調整 LEGO 參數
    col_a, col_b = st.columns(2)
    with col_a:
        new_base = st.number_input("LEGO 方塊底", value=float(conf['base']))
    with col_b:
        new_top = st.number_input("LEGO 方塊頂", value=float(conf['top']))
    st.session_state.watchlist[selected].update({'base': new_base, 'top': new_top})

    # 5. 繪製【陰陽燭 + LEGO 方塊】
    fig = go.Figure(data=[go.Candlestick(
        x=df.index,
        open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
        name="日綫陰陽燭",
        increasing_line_color='#ff4d4d', decreasing_line_color='#2ecc71' # 紅升綠跌
    )])

    # 注入 LEGO 方塊 (態)
    fig.add_shape(type="rect",
        x0=df.index[-lookback], y0=new_base, x1=df.index[-1], y1=new_top,
        fillcolor="Yellow", opacity=0.15, line=dict(color="Gold", width=2)
    )

    fig.update_layout(
        title=f"{conf['name']} - 勢位態視覺化分析",
        template="plotly_dark",
        xaxis_rangeslider_visible=False,
        yaxis=dict(title="價格 (HKD)", range=[new_base*0.85, new_top*1.15])
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # 6. 判定
    current_p = float(df['Close'].iloc[-1])
    status = "🚀 突破" if current_p > new_top else ("📉 破位" if current_p < new_base else "🧱 疊磚")
    st.subheader(f"當前判定：{status} (現價: ${current_p:.2f})")
else:
    st.error("暫時無法獲取該股歷史數據，請確認代碼。")
