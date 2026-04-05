import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime

# 1. 樣式注入：復刻 HTML 視覺效果
st.set_page_config(page_title="Sky Sir 算力中心", layout="wide")

st.markdown("""
    <style>
    .sector-card {
        background-color: #1e1e1e;
        border-radius: 12px;
        padding: 20px;
        border: 1px solid #444;
        transition: 0.3s;
        cursor: pointer;
    }
    .sector-card:hover { border-color: #ffd700; background-color: #252525; }
    .inflow { color: #ff4d4d; font-weight: bold; }
    .outflow { color: #2ecc71; font-weight: bold; }
    .meta-tag {
        font-size: 0.75em;
        background: #333;
        padding: 3px 8px;
        border-radius: 4px;
        color: #ffd700;
        margin-right: 8px;
        border: 0.5px solid #ffd700;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. 核心數據庫 (對齊 2026-04-03 數據)
SECTOR_DB = {
    'ATMXJ (科網龍頭)': {'flow': -12.5, 'meta': '資金撤離', 'icon': '🌐', 'stocks': [
        {'id': '01810', 'name': '小米集團', 'flow': 11.15, 'meta': '木旺帶火', 'base': 18.2, 'top': 21.5},
        {'id': '03690', 'name': '美團', 'flow': 2.45, 'meta': '震盪守位', 'base': 95.0, 'top': 112.0},
        {'id': '09988', 'name': '阿里巴巴', 'flow': -2.49, 'meta': '資金緩流', 'base': 68.0, 'top': 75.0},
        {'id': '00700', 'name': '騰訊控股', 'flow': -1.80, 'meta': '回調修正', 'base': 300.0, 'top': 335.0}
    ]},
    '中特估 (高息權重)': {'flow': 18.2, 'meta': '土生金能量', 'icon': '🏦', 'stocks': [
        {'id': '00939', 'name': '建設銀行', 'flow': 8.40, 'meta': '穩定防守', 'base': 4.8, 'top': 5.4},
        {'id': '01398', 'name': '工商銀行', 'flow': 3.20, 'meta': '穩健護盤', 'base': 4.0, 'top': 4.6},
        {'id': '00883', 'name': '中海油', 'flow': -7.34, 'meta': '火旺制金', 'base': 17.5, 'top': 19.8}
    ]},
    '新能源 (趨勢題材)': {'flow': 21.8, 'meta': '庚金利刃', 'icon': '⚡', 'stocks': [
        {'id': '00175', 'name': '吉利汽車', 'flow': 21.75, 'meta': '氣場爆發', 'base': 8.5, 'top': 10.2},
        {'id': '01211', 'name': '比亞迪', 'flow': 4.12, 'meta': '趨勢向上', 'base': 195.0, 'top': 225.0}
    ]},
    '資源/黃金 (對沖)': {'flow': 4.9, 'meta': '金氣衝天', 'icon': '🏆', 'stocks': [
        {'id': '02899', 'name': '紫金礦業', 'flow': 2.10, 'meta': '避險首選', 'base': 14.5, 'top': 17.2},
        {'id': '01787', 'name': '山東黃金', 'flow': 1.25, 'meta': '金氣凝聚', 'base': 15.8, 'top': 18.5}
    ]}
}

# 3. 狀態導航
if 'step' not in st.session_state: st.session_state.step = 'L1'
if 'focus_sector' not in st.session_state: st.session_state.focus_sector = None
if 'focus_stock' not in st.session_state: st.session_state.focus_stock = None

# --- 第一層：板塊資金流向看板 (L1) ---
if st.session_state.step == 'L1':
    st.markdown("### 📊 張士佳風格：板塊穿透分析盤")
    st.caption("數據日期：2026-04-03 Close | 最高算力實時分析")
    
    cols = st.columns(2)
    for i, (name, info) in enumerate(SECTOR_DB.items()):
        with cols[i % 2]:
            flow_str = f"{info['flow']:+.1f} 億"
            flow_class = "inflow" if info['flow'] > 0 else "outflow"
            
            st.markdown(f"""
                <div class="sector-card">
                    <h3 style="margin:0;">{info['icon']} {name}</h3>
                    <p style="margin:10px 0;">玄學氣場：{info['meta']}</p>
                    <p class="{flow_class}" style="font-size:1.5em;">{flow_str}</p>
                </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"進入 {name} 明細", key=f"btn_{name}"):
                st.session_state.focus_sector = name
                st.session_state.step = 'L2'
                st.rerun()

# --- 第二層：個股資金流明細 (L2) ---
elif st.session_state.step == 'L2':
    sec = st.session_state.focus_sector
    st.markdown(f"### 🔍 {sec} - 資金分佈明細")
    if st.button("⬅️ 返回板塊看板"):
        st.session_state.step = 'L1
