import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import plotly.graph_objects as go

# 1. 時空握手 & 頁面設定
st.set_page_config(page_title="AI 算力中心", layout="wide")
st.title("🚀 AI 新貴：勢位態實時監控系統")
st.write(f"系統時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (對齊 AEST/HKT)")

# 2. 實時抓取引擎
def get_stock_price(ticker):
    try:
        url = f"http://www.aastocks.com/tc/stocks/analysis/stock-quote-details.aspx?stock={ticker}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(r.text, 'html.parser')
        # 抓取現價 (對標 aastock 結構)
        price = soup.find('div', {'class': 'lastPrice'}).text.strip().replace(',', '')
        return float(price)
    except:
        return None

# 3. 數據處理邏輯 (智譜 2513 / MiniMax 100)
def load_dashboard():
    stocks = [
        {"id": "02513", "name": "智譜 AI", "lego_base": 760, "lego_top": 850},
        {"id": "00100", "name": "MiniMax-W", "lego_base": 920, "lego_top": 980}
    ]
    
    results = []
    for s in stocks:
        current = get_stock_price(s['id'])
        if current:
            # 判定形態 (態)
            status = "突破中" if current > s['lego_top'] else ("破位" if current < s['lego_base'] else "疊磚中")
            results.append({
                "代碼": s['id'], "名稱": s['name'], "實時價": current, 
                "方塊底部": s['lego_base'], "狀態": status, "更新": datetime.now().strftime('%H:%M:%S')
            })
    return pd.DataFrame(results)

# 4. 畫面呈現
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📊 實時勢位監控")
    df = load_dashboard()
    if not df.empty:
        # 使用 map 取代 applymap 避免報錯
        st.dataframe(df.style.map(lambda x: 'color: #2ecc71' if x == "突破中" else ('color: #ff4d4d' if x == "破位" else 'color: #f1c40f'), subset=['狀態']))
    else:
        st.warning("等待開市數據流入...")

with col2:
    st.subheader("🔮 玄學與算力提示")
    st.info("💡 提示：明早 09:30 HKT 智譜若守住 $764，火金磁場轉強，有利疊磚上行。")

# 自動刷新按鈕
if st.button('🔄 手動刷新數據'):
    st.rerun()
