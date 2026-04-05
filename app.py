import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime

# 1. 初始化與數據定義 (對齊 HTML 數據)
st.set_page_config(page_title="Sky Sir 核心監控", layout="wide")

# 模擬從 HTML 提取的數據庫
SECTOR_DATA = {
    'ATMXJ (科網)': {'flow': -12.50, 'meta': '資金撤離', 'stocks': [
        {'id': '01810', 'name': '小米', 'flow': 11.15, 'meta': '木旺帶火', 'base': 18.2, 'top': 21.5},
        {'id': '03690', 'name': '美團', 'flow': 2.45, 'meta': '震盪守位', 'base': 95.0, 'top': 112.0},
        {'id': '09988', 'name': '阿里', 'flow': -2.49, 'meta': '資金緩流', 'base': 68.0, 'top': 75.0},
        {'id': '00700', 'name': '騰訊', 'flow': -1.80, 'meta': '回調修正', 'base': 300.0, 'top': 335.0}
    ]},
    '中特估 (高息)': {'flow': 18.22, 'meta': '土生金能量', 'stocks': [
        {'id': '00939', 'name': '建行', 'flow': 8.40, 'meta': '穩健護盤', 'base': 4.8, 'top': 5.4},
        {'id': '01398', 'name': '工行', 'flow': 3.20, 'meta': '穩定防守', 'base': 4.0, 'top': 4.6},
        {'id': '00883', 'name': '中海油', 'flow': -7.34, 'meta': '火旺制金', 'base': 17.5, 'top': 19.8}
    ]},
    '新能源 (汽車)': {'flow': 21.75, 'meta': '庚金利刃', 'stocks': [
        {'id': '00175', 'name': '吉利', 'flow': 21.75, 'meta': '氣場爆發', 'base': 8.5, 'top': 10.2},
        {'id': '01211', 'name': '比亞迪', 'flow': 4.12, 'meta': '趨勢向上', 'base': 195.0, 'top': 225.0}
    ]},
    '資源/黃金': {'flow': 4.90, 'meta': '金氣衝天', 'stocks': [
        {'id': '02899', 'name': '紫金', 'flow': 2.10, 'meta': '對沖首選', 'base': 14.5, 'top': 17.2},
        {'id': '01787', 'name': '山東黃金', 'flow': 1.25, 'meta': '避險資金', 'base': 15.8, 'top': 18.5}
    ]}
}

# 管理導航狀態
if 'view_level' not in st.session_state: st.session_state.view_level = 'sector'
if 'selected_sector' not in st.session_state: st.session_state.selected_sector = None
if 'selected_stock' not in st.session_state: st.session_state.selected_stock = None

# --- 介面邏輯 ---

# 返回按鈕
if st.session_state.view_level != 'sector':
    if st.button("⬅️ 返回上級"):
        if st.session_state.view_level == 'stock_detail':
            st.session_state.view_level = 'stock_list'
        else:
            st.session_state.view_level = 'sector'
        st.rerun()

# 第一層：板塊總覽 (Level 1)
if st.session_state.view_level == 'sector':
    st.subheader("📊 核心板塊資金流向 (億港元)")
    cols = st.columns(len(SECTOR_DATA))
    for i, (name, info) in enumerate(SECTOR_DATA.items()):
        with cols[i]:
            color = "inverse" if info['flow'] < 0 else "normal"
            if st.button(f"{name}\n{info['flow']}B"):
                st.session_state.selected_sector = name
                st.session_state.view_level = 'stock_list'
                st.rerun()
            st.caption(f"氣場：{info['meta']}")

# 第二層：個股排行 (Level 2)
elif st.session_state.view_level == 'stock_list':
    sector_name = st.session_state.selected_sector
    st.subheader(f"🔍 {sector_name} - 個股資金流向排行 (Top 5)")
    
    stocks = SECTOR_DATA[sector_name]['stocks']
    # 按資金流降序排
    sorted_stocks = sorted(stocks, key=lambda x: x['flow'], reverse=True)
    
    for s in sorted_stocks:
        col_s1, col_s2, col_s3 = st.columns([2, 1, 1])
        with col_s1:
            st.write(f"**{s['name']} ({s['id']})**")
            st.caption(f"玄學標籤：{s['meta']}")
        with col_s2:
            flow_color = "red" if s['flow'] > 0 else "green"
            st.markdown(f":{flow_color}[{s['flow']:+.2f} 億]")
        with col_s3:
            if st.button("查看圖表分析", key=s['id']):
                st.session_state.selected_stock = s
                st.session_state.view_level = 'stock_detail'
                st.rerun()

# 第三層：LEGO 圖表分析 (Level 3)
elif st.session_state.view_level == 'stock_detail':
    s = st.session_state.selected_stock
    st.subheader(f"🧱 {s['name']} ({s['id']}) - 勢位態視覺化")
    
    # 抓取日綫數據 (備援模式)
    try:
        yf_code = f"{s['id'].lstrip('0')}.HK"
        df = yf.download(yf_code, period="1mo", interval="1d", progress=False)
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        
        fig = go.Figure(data=[go.Candlestick(
            x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
            increasing_line_color='#ff4d4d', decreasing_line_color='#2ecc71', name="日綫"
        )])
        
        # 注入 LEGO 方塊 (態)
        fig.add_shape(type="rect",
            x0=df.index[-10], y0=s['base'], x1=df.index[-1], y1=s['top'],
            fillcolor="Yellow", opacity=0.15, line=dict(color="Gold", width=2)
        )
        
        fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=500)
        st.plotly_chart(fig, use_container_width=True)
        
        current_p = float(df['Close'].iloc[-1])
        status = "🚀 突破" if current_p > s['top'] else ("📉 破位" if current_p < s['base'] else "🧱 疊磚中")
        st.metric("當前判定", status, delta=f"現價 ${current_p:.2f}")
    except:
        st.error("⚠️ 雲端數據暫時封鎖，請參考 aastock 手動對齊 LEGO 位。")
        st.write(f"🧱 建議 LEGO 方塊：${s['base']} - ${s['top']}")
