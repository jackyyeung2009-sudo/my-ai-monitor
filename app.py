import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime

# 1. 頁面初始化與樣式注入
st.set_page_config(page_title="Sky Sir 終極指揮部", layout="wide")

st.markdown("""
    <style>
    .sector-card {
        background-color: #1a1a1a;
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 15px;
        border: 1px solid #ffd70044;
        transition: 0.3s;
    }
    .sector-card:hover { border-color: #ffd700; transform: translateY(-3px); }
    .inflow { color: #ff4d4d !important; font-weight: bold; }
    .outflow { color: #2ecc71 !important; font-weight: bold; }
    .meta-tag {
        font-size: 0.75em;
        background: #ffd70022;
        padding: 4px 8px;
        border-radius: 5px;
        color: #ffd700;
        border: 1px solid #ffd700;
        margin-right: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. 數據庫持久化與防禦性初始化
if 'full_db' not in st.session_state:
    st.session_state.full_db = {
        'AI 核心 (主力)': {
            '02513': {'name': '智譜 AI', 'flow': 8.5, 'meta': '算力新星', 'base': 760.0, 'top': 850.0},
            '00100': {'name': 'MiniMax-W', 'flow': 12.2, 'meta': '金氣匯聚', 'base': 920.0, 'top': 980.0}
        },
        '新能源 (趨勢)': {
            '00175': {'name': '吉利汽車', 'flow': 21.75, 'meta': '氣場爆發', 'base': 8.5, 'top': 10.2},
            '01211': {'name': '比亞迪', 'flow': 4.12, 'meta': '趨勢向上', 'base': 195.0, 'top': 225.0}
        }
    }

if 'step' not in st.session_state: st.session_state.step = 'L1'
if 'focus_sector' not in st.session_state: st.session_state.focus_sector = None
if 'focus_stock_id' not in st.session_state: st.session_state.focus_stock_id = None

# 3. 側邊欄控制台
st.sidebar.title("🛠️ 指揮部控制台")

# --- 板塊管理 (帶安全檢查) ---
with st.sidebar.expander("📁 板塊管理", expanded=True):
    new_sec_name = st.text_input("新增板塊名稱:")
    if st.button("➕ 建立新板塊"):
        if new_sec_name and new_sec_name not in st.session_state.full_db:
            st.session_state.full_db[new_sec_name] = {}
            st.success(f"板塊 {new_sec_name} 已建立")
    
    if st.session_state.full_db:
        del_sec_name = st.selectbox("刪除板塊:", ["-- 選擇 --"] + list(st.session_state.full_db.keys()))
        if st.button("🗑️ 刪除該板塊"):
            if del_sec_name != "-- 選擇 --":
                del st.session_state.full_db[del_sec_name]
                st.session_state.step = 'L1' # 強制回首頁防止 KeyError
                st.rerun()

# --- 股票管理 (帶安全檢查) ---
with st.sidebar.expander("📈 股票管理", expanded=True):
    if st.session_state.full_db:
        target_sec = st.selectbox("目標板塊:", list(st.session_state.full_db.keys()))
        add_id = st.text_input("新增股票代碼 (5位):")
        if st.button("➕ 加入該板塊"):
            if add_id and target_sec:
                clean_id = add_id.zfill(5)
                st.session_state.full_db[target_sec][clean_id] = {
                    'name': f"個股 {clean_id}", 'flow': 0.0, 'meta': '主動偵察', 'base': 100.0, 'top': 110.0
                }
                st.success(f"{clean_id} 已加入 {target_sec}")

        current_stocks = st.session_state.full_db.get(target_sec, {})
        if current_stocks:
            del_stk_id = st.selectbox("刪除股票:", ["-- 選擇 --"] + list(current_stocks.keys()))
            if st.button("🗑️ 移除該股票"):
                if del_stk_id != "-- 選擇 --":
                    del st.session_state.full_db[target_sec][del_stk_id]
                    st.session_state.step = 'L2' # 回到清單頁
                    st.rerun()

if st.sidebar.button("🏠 回到總覽首頁"):
    st.session_state.step = 'L1'
    st.rerun()

# 4. 主介面邏輯 (穿透式分析)

# --- 第一層：板塊總覽 (L1) ---
if st.session_state.step == 'L1':
    st.markdown("### 📊 勢位態：穿透式資金監控矩陣")
    if not st.session_state.full_db:
        st.info("目前無板塊數據，請從側邊欄新增。")
    else:
        cols = st.columns(3)
        for i, (name, stocks) in enumerate(st.session_state.full_db.items()):
            with cols[i % 3]:
                total_flow = sum(s['flow'] for s in stocks.values())
                f_class = "inflow" if total_flow >= 0 else "outflow"
                st.markdown(f"""
                    <div class="sector-card">
                        <h4 style="margin:0; color:#ffd700;">{name}</h4>
                        <p class="{f_class}" style="font-size:1.5em; margin:10px 0;">{total_flow:+.2f} 億</p>
                        <p style="font-size:0.8em; color:#888;">成員數: {len(stocks)}</p>
                    </div>
                """, unsafe_allow_html=True)
                if st.button(f"進入 {name} 分析", key=f"go_{name}"):
                    st.session_state.focus_sector = name
                    st.session_state.step = 'L2'
                    st.rerun()

# --- 第二層：個股清單 (L2) ---
elif st.session_state.step == 'L2':
    sec = st.session_state.focus_sector
    if sec not in st.session_state.full_db: # 安全檢查
        st.session_state.step = 'L1'
        st.rerun()
    
    st.markdown(f"### 🔍 {sec} - 資金分佈排行")
    stocks = st.session_state.full_db[sec]
    
    if not stocks:
        st.warning("此板塊暫無股票，請從側邊欄加入。")
    else:
        for sid, sinfo in stocks.items():
            col1, col2, col3 = st.columns([3, 2, 1])
            with col1:
                st.markdown(f"<span class='meta-tag'>{sinfo['meta']}</span> **{sinfo['name']} ({sid})**", unsafe_allow_html=True)
            with col2:
                f_c = "inflow" if sinfo['flow'] >= 0 else "outflow"
                st.markdown(f"<span class='{f_c}'>{sinfo['flow']:+.2f} 億</span>", unsafe_allow_html=True)
            with col3:
                if st.button("LEGO 分析", key=f"lego_{sid}"):
                    st.session_state.focus_stock_id = sid
                    st.session_state.step = 'L3'
                    st.rerun()

# --- 第三層：LEGO 分析 (L3) ---
elif st.session_state.step == 'L3':
    sec = st.session_state.focus_sector
    sid = st.session_state.focus_stock_id
    
    # 【關鍵安全檢查】防止 KeyError
    if sec not in st.session_state.full_db or sid not in st.session_state.full_db[sec]:
        st.session_state.step = 'L2'
        st.rerun()
        
    s = st.session_state.full_db[sec][sid]
    st.markdown(f"### 🧱 {s['name']} ({sid}) - LEGO 視覺部署")
    
    c1, c2 = st.columns(2)
    with c1: 
        new_base = st.number_input("LEGO 方塊底", value=float(s['base']))
    with c2: 
        new_top = st.number_input("LEGO 方塊頂", value=float(s['top']))
    
    # 實時保存調整後的 LEGO 位
    st.session_state.full_db[sec][sid].update({'base': new_base, 'top': new_top})

    try:
        yf_code = f"{sid.lstrip('0')}.HK"
        df = yf.download(yf_code, period="1mo", interval="1d", progress=False)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        
        fig = go.Figure(data=[go.Candlestick(
            x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
            increasing_line_color='#ff4d4d', decreasing_line_color='#2ecc71', name="日綫"
        )])
        
        # 繪製 LEGO 方塊 (看過去 10 天)
        fig.add_shape(type="rect",
            x0=df.index[-10], y0=new_base, x1=df.index[-1], y1=new_top,
            fillcolor="Yellow", opacity=0.15, line=dict(color="Gold", width=2)
        )
        
        fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=600)
        st.plotly_chart(fig, use_container_width=True)
        
        curr = float(df['Close'].iloc[-1])
        status = "🚀 突破" if curr > new_top else ("📉 破位" if curr < new_base else "🧱 疊磚")
        st.subheader(f"判定：{status} (現價: ${curr:.2f})")
    except:
        st.error("⚠️ 雲端數據抓取頻率受限，圖表暫時無法顯示。請根據 AASTOCKS 手動核對方塊位。")
