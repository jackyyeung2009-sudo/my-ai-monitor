import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime
import plotly.graph_objects as go

# 1. 頁面初始化
st.set_page_config(page_title="AI 勢位態終端", layout="wide")
st.title("🕯️ 港股 AI 雙雄：陰陽燭與 LEGO 部署")

if 'watchlist' not in st.session_state:
    st.session_state.watchlist = {
        '02513': {'name': '智譜 AI', 'base': 760.0, 'top': 850.0},
        '00100': {'name': 'MiniMax-W', 'base': 920.0, 'top': 980.0}
    }

# 2. 強韌數據抓取函數
def get_clean_data(ticker):
    try:
        # 轉換格式: 02513 -> 2513.HK
        yf_code = f"{ticker.lstrip('0')}.HK"
        # 抓取一個月的數據
        df = yf.download(yf_code, period="1mo", interval="1d", progress=False)
        
        if df.empty: return None
        
        # 【核心修正】解決 MultiIndex 導致的 TypeError
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            
        return df
    except:
        return None

# 3. 側邊欄控制
st.sidebar.title("🛠️ 算力指揮部")
lookback = st.sidebar.slider("LEGO 觀察天數", 5, 25, 10)
new_stock = st.sidebar.text_input("新增港股代碼 (如 00700):")

if st.sidebar.button("➕ 加入監控"):
    d = get_clean_data(new_stock)
    if d is not None:
        last_p = float(d['Close'].iloc[-1])
        st.session_state.watchlist[new_stock] = {
            'name': f"個股 {new_stock}", 'base': last_p*0.95, 'top': last_p*1.05
        }
        st.sidebar.success(f"代碼 {new_stock} 已同步")
    else: st.sidebar.error("抓取失敗，請確認代碼")

# 4. 主面板邏輯
selected = st.selectbox("選擇監控個股", list(st.session_state.watchlist.keys()))
conf = st.session_state.watchlist[selected]
df = get_clean_data(selected)

if df is not None:
    # 調整 LEGO 方塊
    c1, c2 = st.columns(2)
    with c1: new_base = st.number_input("LEGO 方塊底", value=float(conf['base']))
    with c2: new_top = st.number_input("LEGO 方塊頂", value=float(conf['top']))
    st.session_state.watchlist[selected].update({'base': new_base, 'top': new_top})

    # 5. 繪製專業圖表
    fig = go.Figure(data=[go.Candlestick(
        x=df.index,
        open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
        name="日綫陰陽燭",
        increasing_line_color='#ff4d4d', decreasing_line_color='#2ecc71'
    )])

    # 注入 LEGO 方塊陰影 (態)
    fig.add_shape(type="rect",
        x0=df.index[-lookback], y0=new_base, x1=df.index[-1], y1=new_top,
        fillcolor="Yellow", opacity=0.15, line=dict(color="Gold", width=2)
    )

    fig.update_layout(
        title=f"{conf['name']} ({selected}) - LEGO 格局分析",
        template="plotly_dark",
        xaxis_rangeslider_visible=False,
        yaxis=dict(title="價格 (HKD)", range=[new_base*0.8, new_top*1.2])
    )
    st.plotly_chart(fig, use_container_width=True)

    # 6. 部署判定
    current_p = float(df['Close'].iloc[-1])
    status = "🚀 突破" if current_p > new_top else ("📉 破位" if current_p < new_base else "🧱 疊磚中")
    st.subheader(f"戰略判定：{status} (當前收報: ${current_p:.2f})")
else:
    st.error("數據連接中，請稍後或檢查代碼是否正確。")

st.info("☀️ **陽光建議：** 紅色代表陽燭（升），綠色代表陰燭（跌）。觀察陰陽燭的『影線』是否多次觸碰方塊頂部而回落。")
