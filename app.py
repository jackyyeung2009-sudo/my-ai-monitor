import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime

# 1. 頁面初始化
st.set_page_config(page_title="Sky Sir 算力中心", layout="wide")

# 樣式注入：讓首頁卡片回歸 HTML 質魂
st.markdown("""
    <style>
    .sector-card {
        background-color: #1e1e1e;
        border-radius: 15px;
        padding: 25px;
        margin-bottom: 20px;
        border: 1px solid #ffd70033;
        transition: all 0.3s ease;
    }
    .sector-card:hover {
        border-color: #ffd700;
        background-color: #252525;
        transform: translateY(-5px);
    }
    .inflow { color: #ff4d4d !important; font-weight: bold; font-size: 1.6em; }
    .outflow { color: #2ecc71 !important; font-weight: bold; font-size: 1.6em; }
    .meta-tag {
        font-size: 0.8em;
        background: #ffd70022;
        padding: 4px 10px;
        border-radius: 6px;
        color: #ffd700;
        border: 1px solid #ffd700;
        margin-bottom: 10px;
        display: inline-block;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. 核心數據庫
SECTOR_DB = {
    'ATMXJ (科網龍頭)': {'flow': -12.5, 'meta': '資金撤離', 'icon': '🌐'},
    '中特估 (高息權重)': {'flow': 18.2, 'meta': '土生金能量', 'icon': '🏦'},
    '新能源 (趨勢題材)': {'flow': 21.8, 'meta': '庚金利刃', 'icon': '⚡'},
    '資源/黃金 (對沖)': {'flow': 4.9, 'meta': '金氣衝天', 'icon': '🏆'}
}

STOCK_DETAILS = {
    'ATMXJ (科網龍頭)': [
        {'id': '01810', 'name': '小米集團', 'flow': 11.15, 'meta': '木旺帶火', 'base': 18.2, 'top': 21.5},
        {'id': '03690', 'name': '美團', 'flow': 2.45, 'meta': '震盪守位', 'base': 95.0, 'top': 112.0},
        {'id': '00700', 'name': '騰訊控股', 'flow': -1.80, 'meta': '回調修正', 'base': 300.0, 'top': 335.0}
    ],
    '新能源 (趨勢題材)': [
        {'id': '00175', 'name': '吉利汽車', 'flow': 21.75, 'meta': '氣場爆發', 'base': 8.5, 'top': 10.2},
        {'id': '01211', 'name': '比亞迪', 'flow': 4.12, 'meta': '趨勢向上', 'base': 195.0, 'top': 225.0}
    ]
    # 其他板塊可按需補充...
}

# 3. 導航狀態管理
if 'step' not in st.session_state: st.session_state.step = 'L1'
if 'focus_sector' not in st.session_state: st.session_state.focus_sector = None
if 'focus_stock' not in st.session_state: st.session_state.focus_stock = None

# --- 第一層：板塊總覽 (L1) ---
if st.session_state.step == 'L1':
    st.markdown("## 📊 張士佳風格：板塊穿透分析盤")
    st.caption("資料日期：2026-04-03 Close | AEST 01:40 對齊")
    
    cols = st.columns(2)
    for i, (name, info) in enumerate(SECTOR_DB.items()):
        with cols[i % 2]:
            f_val = info['flow']
            f_class = "inflow" if f_val > 0 else "outflow"
            f_sign = "+" if f_val > 0 else ""
            
            # 渲染卡片
            st.markdown(f"""
                <div class="sector-card">
                    <div class="meta-tag">{info['meta']}</div>
                    <h3 style="margin:0; color:white;">{info['icon']} {name}</h3>
                    <p class="{f_class}">{f_sign}{f_val} 億</p>
                </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"進入 {name} 分佈", key=f"btn_{name}"):
                st.session_state.focus_sector = name
                st.session_state.step = 'L2'
                st.rerun()

# --- 第二層：個股清單 (L2) ---
elif st.session_state.step == 'L2':
    sec = st.session_state.focus_sector
    st.markdown(f"### 🔍 {sec} - 資金分佈明細")
    if st.button("⬅️ 返回首頁"):
        st.session_state.step = 'L1'
        st.rerun()

    stocks = STOCK_DETAILS.get(sec, [])
    if not stocks:
        st.info("該板塊暫無詳細個股數據。")
    else:
        for s in stocks:
            f_c = "inflow" if s['flow'] > 0 else "outflow"
            f_s = "+" if s['flow'] > 0 else ""
            col1, col2, col3 = st.columns([3, 2, 1])
            with col1:
                st.markdown(f"<span class='meta-tag'>{s['meta']}</span> **{s['name']} ({s['id']})**", unsafe_allow_html=True)
            with col2:
                st.markdown(f"<span class='{f_c}'>{f_s}{s['flow']} 億</span>", unsafe_allow_html=True)
            with col3:
                if st.button("LEGO 分析", key=f"lego_{s['id']}"):
                    st.session_state.focus_stock = s
                    st.session_state.step = 'L3'
                    st.rerun()

# --- 第三層：LEGO 分析 (L3) ---
elif st.session_state.step == 'L3':
    s = st.session_state.focus_stock
    st.markdown(f"### 🧱 {s['name']} ({s['id']}) - LEGO 視覺部署")
    if st.button("⬅️ 返回列表"):
        st.session_state.step = 'L2'
        st.rerun()

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
        status = "🚀 突破" if curr > s['top'] else ("📉 破位" if curr < s['base'] else "🧱 疊磚")
        st.subheader(f"判定：{status}")
        st.write(f"LEGO 區間：${s['base']} - ${s['top']} | 現價：${curr:.2f}")
    except:
        st.error("⚠️ 雲端數據連線受限，請參考 AASTOCKS 手動核對。")
