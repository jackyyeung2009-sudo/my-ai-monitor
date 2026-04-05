import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime

# 1. 頁面初始化與樣式注入
st.set_page_config(page_title="Sky Sir 核心終端", layout="wide")

st.markdown("""
    <style>
    .sector-card {
        background-color: #1a1a1a;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
        border: 1px solid #ffd70033;
        transition: 0.3s;
    }
    .sector-card:hover { border-color: #ffd700; background-color: #222; }
    .inflow { color: #ff4d4d !important; font-weight: bold; }
    .outflow { color: #2ecc71 !important; font-weight: bold; }
    .meta-tag {
        font-size: 0.75em;
        background: #ffd70022;
        padding: 3px 8px;
        border-radius: 4px;
        color: #ffd700;
        border: 0.5px solid #ffd700;
        margin-right: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. 核心數據初始化 (Session State)
if 'watchlist' not in st.session_state:
    st.session_state.watchlist = {
        '02513': {'name': '智譜 AI', 'flow': 8.5, 'meta': '算力新星', 'base': 760.0, 'top': 850.0},
        '00100': {'name': 'MiniMax-W', 'flow': 12.2, 'meta': '金氣匯聚', 'base': 920.0, 'top': 980.0}
    }

if 'step' not in st.session_state: st.session_state.step = 'L1'
if 'focus_sector' not in st.session_state: st.session_state.focus_sector = None
if 'focus_stock' not in st.session_state: st.session_state.focus_stock = None

# 3. 側邊欄：【功能回歸 - 新增股票】
st.sidebar.title("🛠️ 算力控制台")
st.sidebar.markdown("---")
new_id = st.sidebar.text_input("輸入港股代碼 (如 00700):", key="new_stock_input")

if st.sidebar.button("➕ 加入觀察名單"):
    if new_id:
        clean_id = new_id.zfill(5)
        st.session_state.watchlist[clean_id] = {
            'name': f"自選 {clean_id}", 'flow': 0.0, 'meta': '手動偵察', 
            'base': 100.0, 'top': 110.0 # 預設方塊，進入 Level 3 可調整
        }
        st.sidebar.success(f"{clean_id} 已加入自選板塊")

# 重置導航
if st.sidebar.button("🏠 回到總覽"):
    st.session_state.step = 'L1'
    st.rerun()

# 4. 數據定義 (對齊 HTML 板塊)
SECTOR_DB = {
    '自選觀察 (主力)': st.session_state.watchlist,
    '新能源 (趨勢題材)': {
        '00175': {'name': '吉利汽車', 'flow': 21.75, 'meta': '氣場爆發', 'base': 8.5, 'top': 10.2},
        '01211': {'name': '比亞迪', 'flow': 4.12, 'meta': '趨勢向上', 'base': 195.0, 'top': 225.0}
    },
    'ATMXJ (科網龍頭)': {
        '01810': {'name': '小米集團', 'flow': 11.15, 'meta': '木旺帶火', 'base': 18.2, 'top': 21.5},
        '00700': {'name': '騰訊控股', 'flow': -1.80, 'meta': '回調修正', 'base': 300.0, 'top': 335.0}
    }
}

# --- 第一層：板塊總覽 (L1) ---
if st.session_state.step == 'L1':
    st.markdown("### 📊 天人合一：板塊穿透看板")
    cols = st.columns(len(SECTOR_DB))
    for i, (name, stocks) in enumerate(SECTOR_DB.items()):
        with cols[i]:
            total_flow = sum(s['flow'] for s in stocks.values())
            f_class = "inflow" if total_flow >= 0 else "outflow"
            
            st.markdown(f"""
                <div class="sector-card">
                    <h4 style="margin:0;">{name}</h4>
                    <p class="{f_class}" style="font-size:1.4em; margin:10px 0;">{total_flow:+.1f} 億</p>
                </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"查看明細", key=f"go_{name}"):
                st.session_state.focus_sector = name
                st.session_state.step = 'L2'
                st.rerun()

# --- 第二層：個股清單 (L2) ---
elif st.session_state.step == 'L2':
    sec = st.session_state.focus_sector
    st.markdown(f"### 🔍 {sec} - 資金排行")
    
    stocks = SECTOR_DB[sec]
    for sid, sinfo in stocks.items():
        f_c = "inflow" if sinfo['flow'] >= 0 else "outflow"
        col1, col2, col3 = st.columns([3, 2, 1])
        with col1:
            st.markdown(f"<span class='meta-tag'>{sinfo['meta']}</span> **{sinfo['name']} ({sid})**", unsafe_allow_html=True)
        with col2:
            st.markdown(f"<span class='{f_c}'>{sinfo['flow']:+.2f} 億</span>", unsafe_allow_html=True)
        with col3:
            if st.button("LEGO 分析", key=f"lego_{sid}"):
                # 將個股數據傳入 L3
                sinfo['id'] = sid
                st.session_state.focus_stock = sinfo
                st.session_state.step = 'L3'
                st.rerun()

# --- 第三層：LEGO 陰陽燭分析 (L3) ---
elif st.session_state.step == 'L3':
    s = st.session_state.focus_stock
    st.markdown(f"### 🧱 {s['name']} ({s['id']}) - LEGO 視覺部署")
    
    # 允許調整方塊
    c1, c2 = st.columns(2)
    with c1: s['base'] = st.number_input("LEGO 方塊底", value=float(s['base']))
    with c2: s['top'] = st.number_input("LEGO 方塊頂", value=float(s['top']))

    try:
        yf_code = f"{s['id'].lstrip('0')}.HK"
        df = yf.download(yf_code, period="1mo", interval="1d", progress=False)
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        
        fig = go.Figure(data=[go.Candlestick(
            x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
            increasing_line_color='#ff4d4d', decreasing_line_color='#2ecc71', name="日綫"
        )])
        fig.add_shape(type="rect", x0=df.index[-10], y0=s['base'], x1=df.index[-1], y1=s['top'],
                      fillcolor="Yellow", opacity=0.15, line=dict(color="Gold", width=2))
        fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=600)
        st.plotly_chart(fig, use_container_width=True)
        
        curr = float(df['Close'].iloc[-1])
        st.subheader(f"判定：{'🚀 突破' if curr > s['top'] else ('📉 破位' if curr < s['base'] else '🧱 疊磚')}")
    except:
        st.error("⚠️ 雲端數據受限，請參考 AASTOCKS 手動核對。")
