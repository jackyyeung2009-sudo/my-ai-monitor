import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime
import plotly.graph_objects as go

# 1. 頁面初始化與時空握手
st.set_page_config(page_title="AI 勢位態終端", layout="wide")
st.title("🕯️ 港股 AI 雙雄：陰陽燭與 LEGO 部署 (雲端強化版)")

# 初始化自選清單
if 'watchlist' not in st.session_state:
    st.session_state.watchlist = {
        '02513': {'name': '智譜 AI', 'base': 760.0, 'top': 850.0},
        '00100': {'name': 'MiniMax-W', 'base': 920.0, 'top': 980.0}
    }

# 2. 強韌數據抓取函數 (解決 TypeError 的核心)
def get_clean_data(ticker):
    try:
        # yfinance 格式轉換 (確保 02513 變 2513.HK)
        clean_ticker = ticker.lstrip('0')
        yf_code = f"{clean_ticker}.HK"
        
        # 抓取數據
        df = yf.download(yf_code, period="1mo", interval="1d", progress=False)
        
        if df.empty:
            return None
            
        # 【關鍵修復】強力扁平化 MultiIndex 
        # 如果列是多層的 (例如 ('Close', '2513.HK')), 只保留第一層 ('Close')
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            
        return df
    except Exception as e:
        st.sidebar.error(f"數據引擎異常: {e}")
        return None

# 3. 側邊欄控制
st.sidebar.title("🛠️ 算力指揮部")
lookback = st.sidebar.slider("LEGO 觀察天數", 5, 25, 10)
new_stock = st.sidebar.text_input("新增港股代碼 (如 00700):")

if st.sidebar.button("➕ 加入監控"):
    d = get_clean_data(new_stock)
    if d is not None:
        # 確保取到的是單個 float
        last_p = float(d['Close'].iloc[-1])
        st.session_state.watchlist[new_stock] = {
            'name': f"個股 {new_stock}", 'base': last_p*0.95, 'top': last_p*1.05
        }
        st.sidebar.success(f"代碼 {new_stock} 已同步")
    else:
        st.sidebar.error("抓取失敗，可能是 Yahoo 暫時封鎖雲端 IP")

# 4. 主面板邏輯
selected = st.selectbox("選擇監控個股", list(st.session_state.watchlist.keys()))
conf = st.session_state.watchlist[selected]
df = get_clean_data(selected)

if df is not None:
    # 調整 LEGO 方塊
    c1, c2 = st.columns(2)
    with c1: new_base = st.number_input("LEGO 方塊底", value=float(conf['base']), key="base_input")
    with c2: new_top = st.number_input("LEGO 方塊頂", value=float(conf['top']), key="top_input")
    st.session_state.watchlist[selected].update({'base': new_base, 'top': new_top})

    # 5. 繪製專業陰陽燭
    fig = go.Figure(data=[go.Candlestick(
        x=df.index,
        open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
        name="日綫陰陽燭",
        increasing_line_color='#ff4d4d', decreasing_line_color='#2ecc71'
    )])

    # 注入 LEGO 方塊 (態)
    # 使用最後 N 天作為方塊範圍
    fig.add_shape(type="rect",
        x0=df.index[-min(len(df), lookback)], y0=new_base, x1=df.index[-1], y1=new_top,
        fillcolor="Yellow", opacity=0.15, line=dict(color="Gold", width=2)
    )

    fig.update_layout(
        title=f"{conf['name']} ({selected}) - LEGO 格局趨勢",
        template="plotly_dark",
        xaxis_rangeslider_visible=False,
        yaxis=dict(title="價格 (HKD)", fixedrange=False)
    )
    st.plotly_chart(fig, use_container_width=True)

    # 6. 戰略判定
    current_p = float(df['Close'].iloc[-1])
    status = "🚀 突破" if current_p > new_top else ("📉 破位" if current_p < new_base else "🧱 疊磚中")
    st.subheader(f"判定：{status} (最新價: ${current_p:.2f})")
else:
    st.error("⚠️ 雲端數據抓取失敗：這通常是 Yahoo Finance 暫時封鎖了 Streamlit 的公用 IP。請嘗試重新整理頁面，或檢查代碼是否正確。")

# 7. Debug 資訊 (僅供開發查看，正常運作後可刪除)
with st.expander("🛠️ 數據調試資訊"):
    if df is not None:
        st.write("Columns:", df.columns.tolist())
        st.write(df.tail(3))
