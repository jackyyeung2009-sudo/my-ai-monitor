import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# 1. 設置 UI 與風格
st.set_page_config(page_title="AI 算力中心", layout="wide")
st.title("🛡️ 智譜 & MiniMax：部署與實時雙模系統")

# 2. 定義核心 LEGO 區間 (根據你對過去的觀察)
# 這裡儲存的是「態」的格局，不受休市影響
STOCK_DB = {
    '02513': {'name': '智譜 AI', 'base': 760, 'top': 850, 'last_close': 779.0},
    '00100': {'name': 'MiniMax-W', 'base': 920, 'top': 980, 'last_close': 949.5}
}

def fetch_data(ticker):
    """嘗試抓取，失敗則返回最後收市價"""
    try:
        url = f"http://www.aastocks.com/tc/stocks/analysis/stock-quote-details.aspx?stock={ticker}"
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'}
        r = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # 嘗試尋找現價標籤
        price_tag = soup.find('div', {'class': 'lastPrice'})
        if price_tag:
            return float(price_tag.text.strip().replace(',', '')), "實時更新"
        else:
            return STOCK_DB[ticker]['last_close'], "休市數據"
    except:
        # 如果被封鎖或出錯，返回最後紀錄的數據
        return STOCK_DB[ticker]['last_close'], "離線/部署模式"

# 3. 畫面呈現
st.subheader(f"📅 部署看板 (時間: {datetime.now().strftime('%H:%M:%S')})")
cols = st.columns(2)

for i, ticker in enumerate(STOCK_DB.keys()):
    with cols[i]:
        price, source = fetch_data(ticker)
        config = STOCK_DB[ticker]
        
        # 計算 LEGO 位置
        position = "方塊底部" if price <= config['base'] + 10 else ("方塊頂部" if price >= config['top'] - 10 else "區間中游")
        
        # 顯示指標
        st.metric(label=f"{config['name']} ({ticker})", value=f"${price}", delta=source)
        
        st.write(f"🧱 **LEGO 格局：** ${config['base']} - ${config['top']}")
        st.write(f"📍 **當前狀態：** {position}")
        
        # 方塊進度條 (看過去的位)
        progress = (price - config['base']) / (config['top'] - config['base'])
        st.progress(min(max(progress, 0.0), 1.0), text="方塊內位置")

st.markdown("---")
st.info("💡 **收市分析部署：** 智譜 (2513) 的 LEGO 方塊底在 $760，這是『勢』的防線。明日若低開但不破 760，即為疊磚成功。")
