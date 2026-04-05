import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# 1. 設置 UI
st.set_page_config(page_title="AI 算力中心-部署版", layout="wide")
st.title("🛡️ 智譜 & MiniMax：收市分析與明日部署")

def get_full_analysis(ticker):
    try:
        # 抓取 AASTOCKS 報價頁 (獲取現價與今日波幅)
        url = f"http://www.aastocks.com/tc/stocks/analysis/stock-quote-details.aspx?stock={ticker}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(r.text, 'html.parser')
        
        price = float(soup.find('div', {'class': 'lastPrice'}).text.strip().replace(',', ''))
        
        # 模擬從歷史表格計算 LEGO 位 (實戰中可進一步抓取歷史分頁)
        # 這裡設定 2513 與 100 的 2026 年 4 月歷史 LEGO 區間
        lego_config = {
            '02513': {'base': 760, 'top': 850, 'support': 764},
            '00100': {'base': 920, 'top': 980, 'support': 935}
        }
        
        conf = lego_config.get(ticker)
        status = "突破中" if price > conf['top'] else ("底位疊磚" if price < conf['base'] + 10 else "區間震盪")
        
        return {
            "現價": price,
            "LEGO方塊底": conf['base'],
            "LEGO方塊頂": conf['top'],
            "關鍵支撐": conf['support'],
            "狀態": status
        }
    except:
        return None

# 2. 呈現部署看板
st.subheader(f"📅 明日部署建議 ({datetime.now().strftime('%Y-%m-%d')})")

stocks = [('02513', '智譜 AI'), ('00100', 'MiniMax-W')]
cols = st.columns(2)

for i, (tid, name) in enumerate(stocks):
    with cols[i]:
        res = get_full_analysis(tid)
        if res:
            st.metric(f"{name} ({tid})", f"${res['現價']}", delta=f"{res['狀態']}")
            st.write(f"🧱 **LEGO 方塊區間：** ${res['LEGO方塊底']} - ${res['LEGO方塊頂']}")
            st.write(f"🛡️ **明日部署：** 若守住 ${res['關鍵支撐']} 則繼續持貨，跌破則減倉。")
            
            # 進度條顯示現價在方塊中的位置
            progress = (res['現價'] - res['LEGO方塊底']) / (res['LEGO方塊頂'] - res['LEGO方塊底'])
            st.progress(min(max(progress, 0.0), 1.0), text="方塊位置")
        else:
            st.error(f"無法加載 {name} 數據")

st.markdown("---")
st.info("☀️ **算力提醒：** 收市後數據已固化。目前 2513 (智譜) 正處於能量回測期，若明日低開不破 764，則是『陽氣回升』之兆。")
